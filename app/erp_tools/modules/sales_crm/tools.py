from sqlalchemy import func
from datetime import datetime

from app.db.sale_crm_database import SaleCrmSessionLocal
from app.erp_tools.modules.sales_crm.models import (
    User, Address,
    Product, ProductVariant, Brand,
    Order, OrderDetail, Payment,
    Review, ImgReview,
    Voucher, VoucherDetail, VoucherConstraint
)

# =====================================================
# TRA CỨU TRẠNG THÁI ĐƠN HÀNG
# =====================================================
def get_order_status(order_id: int, user_id: int):
    db = SaleCrmSessionLocal()
    try:
        row = (
            db.query(Order, Payment)
            .outerjoin(Payment, Order.payment_id == Payment.id)
            .filter(Order.id == order_id, Order.user_id == user_id)
            .first()
        )

        if not row:
            return {"message": f"Không tìm thấy đơn hàng {order_id}"}

        o, p = row
        return {
            "order_id": o.id,
            "order_status": o.order_status,
            "payment_status": p.payment_status if p else None,
            "payment_method": p.payment_method if p else None,
            "created_at": o.created_at
        }
    finally:
        db.close()


# =====================================================
# CHI TIẾT ĐƠN HÀNG
# =====================================================
def get_order_detail(order_id: int):
    db = SaleCrmSessionLocal()
    try:
        items = (
            db.query(
                ProductVariant.name,
                OrderDetail.quantity,
                OrderDetail.price
            )
            .join(ProductVariant, OrderDetail.product_variant_id == ProductVariant.id)
            .filter(OrderDetail.order_id == order_id)
            .all()
        )

        return [
            {
                "variant_name": name,
                "quantity": qty,
                "price": float(price)
            }
            for name, qty, price in items
        ]
    finally:
        db.close()


# =====================================================
# LỊCH SỬ MUA HÀNG
# =====================================================
def get_purchase_history(user_id: int):
    db = SaleCrmSessionLocal()
    try:
        rows = (
            db.query(
                Order.id,
                Order.created_at,
                Order.order_status,
                func.sum(OrderDetail.quantity * OrderDetail.price).label("total")
            )
            .join(OrderDetail, Order.id == OrderDetail.order_id)
            .filter(Order.user_id == user_id)
            .group_by(Order.id)
            .order_by(Order.created_at.desc())
            .all()
        )

        return [
            {
                "order_id": oid,
                "created_at": created_at,
                "status": status,
                "total_amount": float(total)
            }
            for oid, created_at, status, total in rows
        ]
    finally:
        db.close()


# =====================================================
# TRẠNG THÁI THANH TOÁN
# =====================================================
def get_payment_status(payment_id: int):
    db = SaleCrmSessionLocal()
    try:
        p = db.query(Payment).filter(Payment.id == payment_id).first()
        if not p:
            return {"message": "Không tìm thấy thanh toán"}

        return {
            "payment_id": p.id,
            "status": p.payment_status,
            "method": p.payment_method,
            "amount": float(p.amount)
        }
    finally:
        db.close()


# =====================================================
# KIỂM TRA VOUCHER
# =====================================================
def check_voucher_valid(code: str, order_amount: float | None = None):
    db = SaleCrmSessionLocal()
    try:
        vd = (
            db.query(VoucherDetail)
            .filter(VoucherDetail.code == code, VoucherDetail.is_active == True)
            .first()
        )

        if not vd:
            return {"valid": False, "reason": "Voucher không tồn tại"}

        if order_amount is None:
            return {
                "valid": False,
                "need_more_info": True,
                "message": "Vui lòng cho biết giá trị đơn hàng để kiểm tra voucher"
            }

        v = vd.voucher
        vc = (
            db.query(VoucherConstraint)
            .filter(VoucherConstraint.voucher_id == v.id)
            .first()
        )

        now = datetime.utcnow()
        if not (v.start_date <= now <= v.end_date):
            return {"valid": False, "reason": "Voucher đã hết hạn"}

        if vc and order_amount < vc.min_order_amount:
            return {"valid": False, "reason": "Đơn hàng chưa đủ điều kiện"}

        return {
            "valid": True,
            "discount_type": v.discount_type,
            "discount_value": float(v.discount_value)
        }
    finally:
        db.close()


# =====================================================
# TẠO ĐÁNH GIÁ SẢN PHẨM
# =====================================================
def create_review(product_id: int, user_id: int, content: str, rating: int):
    db = SaleCrmSessionLocal()
    try:
        r = Review(
            product_id=product_id,
            user_id=user_id,
            content=content,
            rating=rating,
            created_at=datetime.utcnow()
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return {"review_id": r.id}
    finally:
        db.close()


# =====================================================
# XEM ĐÁNH GIÁ SẢN PHẨM
# =====================================================
def get_product_reviews(product_id: int):
    db = SaleCrmSessionLocal()
    try:
        rows = (
            db.query(
                Review.rating,
                Review.content,
                User.username,
                Review.created_at
            )
            .join(User, Review.user_id == User.id)
            .filter(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .all()
        )

        return [
            {
                "rating": rating,
                "content": content,
                "username": username,
                "created_at": created_at
            }
            for rating, content, username, created_at in rows
        ]
    finally:
        db.close()


# =====================================================
# THÔNG TIN KHÁCH HÀNG
# =====================================================
def get_customer_profile(user_id: int):
    db = SaleCrmSessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "Không tìm thấy khách hàng"}

        addr = (
            db.query(Address)
            .filter(Address.user_id == user_id, Address.is_default == True)
            .first()
        )

        return {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "default_address": addr.street_address if addr else None
        }
    finally:
        db.close()


# =====================================================
# THÔNG TIN SẢN PHẨM
# =====================================================
def get_product_info(product_id: int):
    db = SaleCrmSessionLocal()
    try:
        row = (
            db.query(Product, Brand)
            .join(Brand, Product.brand_id == Brand.id)
            .filter(Product.id == product_id)
            .first()
        )

        if not row:
            return {"message": "Không tìm thấy sản phẩm"}

        product, brand = row
        return {
            "name": product.name,
            "brand": brand.name,
            "rating": float(product.avg_rating),
            "active": product.is_active
        }
    finally:
        db.close()


# =====================================================
# BIẾN THỂ SẢN PHẨM
# =====================================================
def get_product_variants(product_id: int):
    db = SaleCrmSessionLocal()
    try:
        variants = (
            db.query(ProductVariant)
            .filter(ProductVariant.product_id == product_id)
            .all()
        )

        return [
            {
                "variant": v.name,
                "price": float(v.original_price),
                "discount": float(v.discount_amount or 0),
                "stock": v.stock
            }
            for v in variants
        ]
    finally:
        db.close()


# =====================================================
# SẢN PHẨM THEO HÃNG
# =====================================================
def get_products_by_brand(brand_id: int):
    db = SaleCrmSessionLocal()
    try:
        products = (
            db.query(Product)
            .filter(Product.brand_id == brand_id, Product.is_active == True)
            .all()
        )

        return [{"id": p.id, "name": p.name} for p in products]
    finally:
        db.close()
