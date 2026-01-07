# app/erp_tools/modules/supply_chain/router/supply_chain.py

import re
from typing import Dict


def supply_chain_router(message: str) -> Dict:
    text = message.lower()

    # --------------------------------------------------
    # A. INVENTORY – TỒN KHO
    # --------------------------------------------------
    if any(k in text for k in [
        "tồn kho", "còn hàng", "hết hàng", "số lượng", "tồn"
    ]):
        if any(k in text for k in ["sku", "mã"]):
            return _result("inventory", "get_inventory_stock_by_sku", 0.95)
        if any(k in text for k in ["kho", "warehouse"]):
            return _result("inventory", "get_stock_by_warehouse", 0.95)
        if any(k in text for k in ["kệ", "bin", "vị trí"]):
            return _result("inventory", "get_stock_by_bin", 0.95)
        if any(k in text for k in ["tổng", "toàn hệ thống"]):
            return _result("inventory", "get_all_stock_summary", 0.95)
        return _result("inventory", "get_inventory_stock", 0.90)
    
    if "kho" in text and any(k in text for k in ["bao nhiêu", "còn"]):
        return {
            "domain": "inventory",
            "intent": "get_stock_by_warehouse",
            "confidence": 0.8
        }

    # --------------------------------------------------
    # B. INVENTORY ANALYTICS
    # --------------------------------------------------
    if any(k in text for k in [
        "sắp hết", "cảnh báo", "thiếu hàng"
    ]):
        return _result("inventory", "get_low_stock_products", 0.95)

    if any(k in text for k in [
        "tồn nhiều", "dư thừa", "overstock"
    ]):
        return _result("inventory", "get_overstock_products", 0.95)

    if any(k in text for k in [
        "không bán", "lâu không xuất", "dead stock"
    ]):
        return _result("inventory", "get_dead_stock_products", 0.95)

    # --------------------------------------------------
    # C. GOODS RECEIPT – NHẬP KHO
    # --------------------------------------------------
    if any(k in text for k in [
        "nhập kho", "phiếu nhập", "gr"
    ]):
        if any(k in text for k in ["trạng thái", "xong chưa"]):
            return _result("inbound", "get_goods_receipt_status", 0.95)
        if any(k in text for k in ["chi tiết", "gồm", "sản phẩm"]):
            return _result("inbound", "get_goods_receipt_detail", 0.95)
        if any(k in text for k in ["po", "đơn mua"]):
            return _result("inbound", "get_goods_receipts_by_po", 0.95)
        if any(k in text for k in ["nhà cung cấp", "ncc"]):
            return _result("inbound", "get_goods_receipts_by_supplier", 0.95)
        return _result("inbound", "get_recent_goods_receipts", 0.90)

    # --------------------------------------------------
    # D. GOODS ISSUE – XUẤT KHO
    # --------------------------------------------------
    if any(k in text for k in [
        "xuất kho", "phiếu xuất", "gi"
    ]):
        if any(k in text for k in ["trạng thái"]):
            return _result("outbound", "get_goods_issue_status", 0.95)
        if any(k in text for k in ["chi tiết", "sản phẩm"]):
            return _result("outbound", "get_goods_issue_detail", 0.95)
        if any(k in text for k in ["bán", "nội bộ", "chuyển"]):
            return _result("outbound", "get_goods_issues_by_type", 0.90)
        if any(k in text for k in ["đơn", "so", "hr"]):
            return _result("outbound", "get_goods_issues_by_reference", 0.90)

    # --------------------------------------------------
    # E. PROCUREMENT – MUA HÀNG
    # --------------------------------------------------
    if any(k in text for k in [
        "đơn mua", "po", "mua hàng"
    ]):
        if any(k in text for k in ["trạng thái"]):
            return _result("procurement", "get_purchase_order_status", 0.95)
        if any(k in text for k in ["chi tiết"]):
            return _result("procurement", "get_purchase_order_detail", 0.95)
        if any(k in text for k in ["chưa xong", "đang mở"]):
            return _result("procurement", "get_open_purchase_orders", 0.95)
        if any(k in text for k in ["đã nhập bao nhiêu", "tiến độ"]):
            return _result("procurement", "get_po_receiving_progress", 0.95)

    if any(k in text for k in [
        "yêu cầu mua", "pr"
    ]):
        if any(k in text for k in ["trạng thái"]):
            return _result("procurement", "get_purchase_request_status", 0.95)
        return _result("procurement", "get_open_purchase_requests", 0.90)

    # --------------------------------------------------
    # F. SUPPLIER – NHÀ CUNG CẤP
    # --------------------------------------------------
    if any(k in text for k in [
        "nhà cung cấp", "ncc", "supplier"
    ]):
        if any(k in text for k in ["thông tin", "profile"]):
            return _result("supplier", "get_supplier_profile", 0.95)
        if any(k in text for k in ["xếp hạng", "tốt nhất"]):
            return _result("supplier", "rank_suppliers_by_performance", 0.95)
        return _result("supplier", "get_supplier_purchase_history", 0.90)

    # --------------------------------------------------
    # G. AUDIT / LOG
    # --------------------------------------------------
    if any(k in text for k in [
        "log", "lịch sử", "biến động"
    ]):
        return _result("audit", "get_inventory_transaction_logs", 0.95)

    # --------------------------------------------------
    # H. STOCKTAKE – KIỂM KÊ
    # --------------------------------------------------
    if any(k in text for k in [
        "kiểm kê", "stocktake"
    ]):
        if any(k in text for k in ["trạng thái"]):
            return _result("stocktake", "get_stocktake_status", 0.95)
        if any(k in text for k in ["chênh lệch"]):
            return _result("stocktake", "get_stock_variance_report", 0.95)
        return _result("stocktake", "get_stocktake_detail", 0.90)

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------
    return _result("unknown", None, 0.0)


def _result(domain: str, intent: str, confidence: float) -> Dict:
    return {
        "domain": domain,
        "intent": intent,
        "confidence": confidence
    }
