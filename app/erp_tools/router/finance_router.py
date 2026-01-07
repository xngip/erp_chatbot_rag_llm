import re

from app.erp_tools.modules.finance_accounting.tools import (
    get_ar_invoice_status,
    get_ar_invoice_detail,
    get_customer_receivable_summary,

    get_ap_invoice_status,
    get_ap_invoice_detail,
    get_supplier_payable_summary,

    get_cash_transaction,
    get_cash_flow_history,

    get_journal_entries,
    get_journal_entry_detail,
    get_account_balance,

    get_current_fiscal_period,
    get_fiscal_periods,

    explain_posting_rule
)

# =====================================================
# HELPER: TRÍCH ID / CODE
# =====================================================

def extract_number(text: str):
    match = re.search(r"\b(\d+)\b", text)
    return int(match.group(1)) if match else None


def extract_invoice_code(text: str):
    match = re.search(r"(AR|AP)[-_ ]?(\d+)", text.upper())
    return int(match.group(2)) if match else None


def extract_partner_id(text: str):
    match = re.search(r"đối tác\s*(\d+)|khách hàng\s*(\d+)|nhà cung cấp\s*(\d+)", text.lower())
    if not match:
        return None
    return int(next(g for g in match.groups() if g))


def extract_account_id(text: str):
    match = re.search(r"tài khoản\s*(\d+)", text.lower())
    return int(match.group(1)) if match else None


def extract_event_code(text: str):
    match = re.search(r"event\s*([A-Z0-9_]+)", text.upper())
    return match.group(1) if match else None


# =====================================================
# RULE MATCHER
# =====================================================

def is_ar_invoice_query(text: str):
    return "hóa đơn bán" in text.lower() or "ar" in text.lower()


def is_ap_invoice_query(text: str):
    return "hóa đơn mua" in text.lower() or "ap" in text.lower()


def is_receivable_query(text: str):
    return "công nợ khách hàng" in text.lower() or "khách hàng còn nợ" in text.lower()


def is_payable_query(text: str):
    return "công nợ nhà cung cấp" in text.lower() or "phải trả" in text.lower()

def is_customer_receivable_query(text: str):
    return "còn nợ" in text.lower() or "công nợ" in text.lower()


def is_cash_query(text: str):
    return "thu chi" in text.lower() or "giao dịch tiền" in text.lower()


def is_journal_query(text: str):
    return "bút toán" in text.lower() or "nhật ký kế toán" in text.lower()


def is_account_balance_query(text: str):
    return "số dư tài khoản" in text.lower()


def is_fiscal_query(text: str):
    return "kỳ kế toán" in text.lower()


def is_posting_rule_query(text: str):
    return "hạch toán" in text.lower() or "ghi nhận" in text.lower()


# =====================================================
# ROUTER FINANCE
# =====================================================

def finance_router(query: str):
    """
    Finance Router
    Trả về dict hoặc None
    """

    q = query.lower()

    # =========================
    # 1️ HÓA ĐƠN BÁN (AR)
    # =========================
    if is_ar_invoice_query(q):
        invoice_id = extract_invoice_code(query) or extract_number(query)
        if invoice_id:
            if "chi tiết" in q:
                return get_ar_invoice_detail(invoice_id)
            return get_ar_invoice_status(invoice_id)

    # =========================
    # 2️ CÔNG NỢ KHÁCH HÀNG
    # =========================
    if is_receivable_query(q):
        partner_id = extract_partner_id(query)
        if partner_id:
            return get_customer_receivable_summary(partner_id)

    # =========================
    # 3️ HÓA ĐƠN MUA (AP)
    # =========================
    if is_ap_invoice_query(q):
        invoice_id = extract_invoice_code(query) or extract_number(query)
        if invoice_id:
            if "chi tiết" in q:
                return get_ap_invoice_detail(invoice_id)
            return get_ap_invoice_status(invoice_id)

    # =========================
    # 4️ CÔNG NỢ NHÀ CUNG CẤP
    # =========================
    if is_payable_query(q):
        partner_id = extract_partner_id(query)
        if partner_id:
            return get_supplier_payable_summary(partner_id)

    # =========================
    # 5️ THU – CHI
    # =========================
    if is_cash_query(q):
        tx_id = extract_number(query)
        if tx_id:
            return get_cash_transaction(tx_id)
        return get_cash_flow_history()

    # =========================
    # 6️ KẾ TOÁN
    # =========================
    if is_journal_query(q):
        entry_id = extract_number(query)
        if entry_id:
            return get_journal_entry_detail(entry_id)
        return get_journal_entries()

    if is_account_balance_query(q):
        account_id = extract_account_id(query)
        if account_id:
            return get_account_balance(account_id)

    # =========================
    # 7️ KỲ KẾ TOÁN
    # =========================
    if is_fiscal_query(q):
        if "hiện tại" in q:
            return get_current_fiscal_period()
        return get_fiscal_periods()

    # =========================
    # 8️ GIẢI THÍCH HẠCH TOÁN
    # =========================
    if is_posting_rule_query(q):
        event_code = extract_event_code(query)
        if event_code:
            return explain_posting_rule(event_code)
        

    # =========================
    # FALLBACK
    # =========================
    return None
