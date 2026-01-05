import re

from app.erp_tools.modules.sales_crm.tools import (
    get_order_status,
    get_order_detail,
    get_purchase_history,
    get_payment_status,
    check_voucher_valid,
    create_review,
    get_product_reviews,
    get_customer_profile,
    get_product_info,
    get_product_variants,
    get_products_by_brand
)

# =====================================================
# ENTITY EXTRACT
# =====================================================
def extract_order_id(text: str):
    match = re.search(r"đơn hàng\s*(\d+)", text.lower())
    return int(match.group(1)) if match else None


def extract_product_id(text: str):
    match = re.search(r"sản phẩm\s*(\d+)", text.lower())
    return int(match.group(1)) if match else None


def extract_voucher_code(text: str):
    match = re.search(r"\b[A-Z0-9]{4,}\b", text.upper())
    return match.group(0) if match else None


def extract_rating(text: str):
    match = re.search(r"(\d)\s*sao", text.lower())
    return int(match.group(1)) if match else None


# =====================================================
# RULE CHECK
# =====================================================
def is_order_detail_query(text: str):
    return "chi tiết" in text and "đơn hàng" in text


def is_order_status_query(text: str):
    return "đơn hàng" in text


def is_purchase_history_query(text: str):
    return any(k in text for k in [
        "lịch sử mua", "đã mua", "mua những gì"
    ])


def is_payment_query(text: str):
    return "thanh toán" in text


def is_voucher_query(text: str):
    return "voucher" in text or "mã" in text


def is_voucher_preview_query(text: str):
    return any(k in text for k in [
        "còn bao nhiêu tiền",
        "sau khi áp",
        "giảm còn",
        "áp voucher"
    ])


def is_profile_query(text: str):
    return "thông tin tài khoản" in text or "thông tin của tôi" in text


def is_product_query(text: str):
    return "sản phẩm" in text


def is_brand_query(text: str):
    return "hãng" in text


def is_review_query(text: str):
    return "đánh giá" in text


# =====================================================
# SALE & CRM ROUTER
# =====================================================
def sale_crm_router(
    query: str,
    user_id: int = 1  # demo hardcode
):
    q = query.lower()

    # 1️ CHI TIẾT ĐƠN HÀNG
    if is_order_detail_query(q):
        order_id = extract_order_id(q)
        if order_id:
            return get_order_detail(order_id)

    # 2️ TRẠNG THÁI ĐƠN HÀNG
    if is_order_status_query(q):
        order_id = extract_order_id(q)
        if order_id:
            return get_order_status(order_id, user_id)

    # 3️ LỊCH SỬ MUA
    if is_purchase_history_query(q):
        return get_purchase_history(user_id)

    # 4️ TRẠNG THÁI THANH TOÁN
    if is_payment_query(q):
        order_id = extract_order_id(q)
        if order_id:
            return get_payment_status(order_id)

    # 5️ VOUCHER – KIỂM TRA
    if is_voucher_query(q) and not is_voucher_preview_query(q):
        code = extract_voucher_code(query)
        if code:
            return check_voucher_valid(code)

    # 6 THÔNG TIN KHÁCH HÀNG
    if is_profile_query(q):
        return get_customer_profile(user_id)

    # 7 SẢN PHẨM
    if is_product_query(q):
        product_id = extract_product_id(q)
        if product_id:
            return {
                "info": get_product_info(product_id),
                "variants": get_product_variants(product_id),
                "reviews": get_product_reviews(product_id)
            }

    # 8 SẢN PHẨM THEO HÃNG
    if is_brand_query(q):
        # demo đơn giản: user hỏi “sản phẩm của hãng 1”
        match = re.search(r"hãng\s*(\d+)", q)
        if match:
            return get_products_by_brand(int(match.group(1)))

    # 9 ĐÁNH GIÁ SẢN PHẨM
    if is_review_query(q):
        product_id = extract_product_id(q)
        rating = extract_rating(q)
        if product_id and rating:
            return create_review(
                product_id=product_id,
                user_id=user_id,
                content="Đánh giá từ chatbot",
                rating=rating
            )

    return None
