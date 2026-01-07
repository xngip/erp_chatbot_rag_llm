from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.db.supply_chain_database import SupplyChainSessionLocal
from sqlalchemy import or_

from app.erp_tools.modules.supply_chain.models import (
    # Inventory
    CurrentStock,
    InventoryTransactionLog,

    # Master
    Product,
    Warehouse,
    BinLocation,
    Supplier,

    # Inbound
    GoodsReceipt,
    GRItem,

    # Outbound
    GoodsIssue,
    GIItem,

    # Procurement
    PurchaseRequest,
    PRItem,
    Quotation,
    PurchaseOrder,
    POItem,

    # Stocktake
    Stocktake,
    StocktakeDetail,
)

def get_inventory_stock(product_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            func.sum(CurrentStock.quantity_on_hand).label("quantity")
        ).join(Product).filter(
            CurrentStock.product_id == product_id
        ).group_by(Product.product_name).first()
    finally:
        db.close()


def get_inventory_stock_by_sku(sku: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.sku,
            Product.product_name,
            func.sum(CurrentStock.quantity_on_hand).label("quantity")
        ).join(Product).filter(
            Product.sku == sku
        ).group_by(Product.sku, Product.product_name).first()
    finally:
        db.close()

from sqlalchemy import func, or_
from app.erp_tools.modules.supply_chain.models import (
    Product, CurrentStock
)
from app.db.supply_chain_database import SupplyChainSessionLocal


def get_inventory_stock_by_keyword(keyword: str):
    db = SupplyChainSessionLocal()
    try:
        return (
            db.query(
                Product.product_name,
                func.sum(CurrentStock.quantity_on_hand).label("quantity")
            )
            .join(Product, Product.product_id == CurrentStock.product_id)
            .filter(
                or_(
                    Product.product_name.ilike(f"%{keyword}%"),
                    Product.sku.ilike(f"%{keyword}%")
                )
            )
            .group_by(Product.product_name)
            .all()
        )
    finally:
        db.close()

from sqlalchemy import or_
from app.erp_tools.modules.supply_chain.models import Supplier


def get_supplier_by_keyword(keyword: str):
    db = SupplyChainSessionLocal()
    try:
        return (
            db.query(Supplier)
            .filter(
                or_(
                    Supplier.supplier_name.ilike(f"%{keyword}%"),
                    Supplier.supplier_code.ilike(f"%{keyword.upper()}%")
                )
            )
            .all()
        )
    finally:
        db.close()

from sqlalchemy import or_
from app.erp_tools.modules.supply_chain.models import Warehouse


def get_stock_by_warehouse(keyword: str):
    db = SupplyChainSessionLocal()
    try:
        return (
            db.query(
                Product.product_name,
                func.sum(CurrentStock.quantity_on_hand).label("quantity")
            )
            .join(Product, Product.product_id == CurrentStock.product_id)
            .join(Warehouse, Warehouse.warehouse_id == CurrentStock.warehouse_id)
            .filter(
                or_(
                    Warehouse.warehouse_name.ilike(f"%{keyword}%"),
                    Warehouse.warehouse_code.ilike(f"%{keyword.upper()}%")
                )
            )
            .group_by(Product.product_name)
            .all()
        )
    finally:
        db.close()

def get_stock_by_warehouse_and_product(
    warehouse_keyword: str,
    product_keyword: str
):
    db = SupplyChainSessionLocal()
    try:
        return (
            db.query(
                Product.product_name,
                func.sum(CurrentStock.quantity_on_hand).label("quantity")
            )
            .join(Product)
            .join(Warehouse)
            .filter(
                Warehouse.warehouse_name.ilike(f"%{warehouse_keyword}%"),
                Product.product_name.ilike(f"%{product_keyword}%")
            )
            .group_by(Product.product_name)
            .all()
        )
    finally:
        db.close()

def get_stock_by_warehouse(warehouse_keyword: str):
    db = SupplyChainSessionLocal()
    try:
        return (
            db.query(
                Product.product_name,
                func.sum(CurrentStock.quantity_on_hand).label("quantity")
            )
            .join(Product, Product.product_id == CurrentStock.product_id)
            .join(Warehouse, Warehouse.warehouse_id == CurrentStock.warehouse_id)
            .filter(
                or_(
                    Warehouse.warehouse_name.ilike(f"%{warehouse_keyword}%"),
                    Warehouse.warehouse_code.ilike(f"%{warehouse_keyword.upper()}%")
                )
            )
            .group_by(Product.product_name)
            .all()
        )
    finally:
        db.close()


def get_stock_by_bin(bin_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            CurrentStock.quantity_on_hand
        ).join(Product).filter(
            CurrentStock.bin_id == bin_id
        ).all()
    finally:
        db.close()

def get_all_stock_summary():
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            func.sum(CurrentStock.quantity_on_hand).label("total_quantity")
        ).join(Product).group_by(Product.product_name).all()
    finally:
        db.close()

def check_product_availability(product_id: int):
    stock = get_inventory_stock(product_id)
    return stock and stock.quantity > 0


def get_low_stock_products():
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            func.sum(CurrentStock.quantity_on_hand).label("quantity"),
            Product.min_stock_level
        ).join(Product).group_by(Product.product_id).having(
            func.sum(CurrentStock.quantity_on_hand) < Product.min_stock_level
        ).all()
    finally:
        db.close()


def get_overstock_products(threshold: int = 500):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            func.sum(CurrentStock.quantity_on_hand).label("quantity")
        ).join(Product).group_by(Product.product_id).having(
            func.sum(CurrentStock.quantity_on_hand) > threshold
        ).all()
    finally:
        db.close()


def get_dead_stock_products(days: int = 90):
    db = SupplyChainSessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return db.query(Product.product_name).filter(
            ~Product.product_id.in_(
                db.query(InventoryTransactionLog.product_id)
                .filter(InventoryTransactionLog.transaction_date >= cutoff)
            )
        ).all()
    finally:
        db.close()


def get_stock_alerts():
    return {
        "low_stock": get_low_stock_products(),
        "dead_stock": get_dead_stock_products(),
    }

def get_stock_reserved_quantity(product_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            func.sum(CurrentStock.quantity_allocated)
        ).filter(
            CurrentStock.product_id == product_id
        ).scalar()
    finally:
        db.close()


def get_available_stock(product_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            func.sum(CurrentStock.quantity_on_hand - CurrentStock.quantity_allocated)
        ).filter(CurrentStock.product_id == product_id).scalar()
    finally:
        db.close()


def get_stock_for_sales_order(product_id: int, required_qty: int):
    available = get_available_stock(product_id)
    return available >= required_qty

def get_goods_receipt_status(gr_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            GoodsReceipt.gr_code,
            GoodsReceipt.status
        ).filter(GoodsReceipt.gr_code == gr_code).first()
    finally:
        db.close()


def get_goods_receipt_detail(gr_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            GRItem.quantity_received,
            Warehouse.warehouse_name
        ).join(GRItem).join(Product).join(Warehouse).filter(
            GoodsReceipt.gr_code == gr_code
        ).all()
    finally:
        db.close()


def get_goods_receipts_by_po(po_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsReceipt).filter(
            GoodsReceipt.po_id == po_id
        ).all()
    finally:
        db.close()


def get_goods_receipts_by_supplier(supplier_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsReceipt).join(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == supplier_id
        ).all()
    finally:
        db.close()


def get_recent_goods_receipts(days: int = 7):
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsReceipt).filter(
            GoodsReceipt.receipt_date >= datetime.utcnow() - timedelta(days=days)
        ).all()
    finally:
        db.close()

def get_received_vs_ordered_quantity(po_id: int):
    """
    So sánh số lượng đặt mua (PO) và số lượng đã nhập kho (GR)
    Dùng cho phân tích thiếu hàng / nhập chưa đủ
    """
    db = SupplyChainSessionLocal()
    try:
        result = (
            db.query(
                Product.product_name.label("product_name"),
                POItem.quantity_ordered.label("ordered_quantity"),
                func.coalesce(func.sum(GRItem.quantity_received), 0).label("received_quantity")
            )
            .join(POItem, POItem.product_id == Product.product_id)
            .outerjoin(
                GRItem,
                GRItem.product_id == Product.product_id
            )
            .outerjoin(
                GoodsReceipt,
                GoodsReceipt.gr_id == GRItem.gr_id
            )
            .filter(POItem.po_id == po_id)
            .group_by(Product.product_name, POItem.quantity_ordered)
            .all()
        )

        return [
            {
                "product": row.product_name,
                "ordered": row.ordered_quantity,
                "received": row.received_quantity,
                "missing": row.ordered_quantity - row.received_quantity
            }
            for row in result
        ]

    finally:
        db.close()


def get_partial_received_pos():
    db = SupplyChainSessionLocal()
    try:
        return db.query(PurchaseOrder.po_code).filter(
            PurchaseOrder.status == "PARTIAL_RECEIVED"
        ).all()
    finally:
        db.close()


def get_supplier_delivery_performance():
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Supplier.supplier_name,
            func.count(GoodsReceipt.gr_id).label("total_receipts")
        ).join(PurchaseOrder).join(GoodsReceipt).group_by(
            Supplier.supplier_name
        ).all()
    finally:
        db.close()

def get_goods_issue_status(gi_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            GoodsIssue.gi_code,
            GoodsIssue.status
        ).filter(GoodsIssue.gi_code == gi_code).first()
    finally:
        db.close()


def get_goods_issue_detail(gi_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            GIItem.quantity_issued
        ).join(GIItem).join(Product).filter(
            GoodsIssue.gi_code == gi_code
        ).all()
    finally:
        db.close()


def get_goods_issues_by_type(issue_type: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsIssue).filter(
            GoodsIssue.issue_type == issue_type
        ).all()
    finally:
        db.close()


def get_goods_issues_by_reference(ref: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsIssue).filter(
            GoodsIssue.reference_doc_id == ref
        ).all()
    finally:
        db.close()

def get_pending_goods_issues():
    db = SupplyChainSessionLocal()
    try:
        return db.query(GoodsIssue).filter(
            GoodsIssue.status == "DRAFT"
        ).all()
    finally:
        db.close()


def get_daily_outbound_summary():
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            func.date(GoodsIssue.issue_date),
            func.sum(GIItem.quantity_issued)
        ).join(GIItem).group_by(
            func.date(GoodsIssue.issue_date)
        ).all()
    finally:
        db.close()


def get_top_issued_products(limit: int = 5):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            func.sum(GIItem.quantity_issued).label("total")
        ).join(GIItem).join(Product).group_by(
            Product.product_name
        ).order_by(func.sum(GIItem.quantity_issued).desc()).limit(limit).all()
    finally:
        db.close()

def get_purchase_request_status(pr_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            PurchaseRequest.pr_code,
            PurchaseRequest.status
        ).filter(PurchaseRequest.pr_code == pr_code).first()
    finally:
        db.close()


def get_open_purchase_requests():
    db = SupplyChainSessionLocal()
    try:
        return db.query(PurchaseRequest).filter(
            PurchaseRequest.status != "PROCESSED"
        ).all()
    finally:
        db.close()


def get_pr_detail(pr_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            PRItem.quantity_requested
        ).join(PRItem).join(Product).filter(
            PRItem.pr_id == pr_id
        ).all()
    finally:
        db.close()


def get_purchase_order_status(po_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            PurchaseOrder.po_code,
            PurchaseOrder.status
        ).filter(PurchaseOrder.po_code == po_code).first()
    finally:
        db.close()


def get_po_receiving_progress(po_id: int):
    db = SupplyChainSessionLocal()
    try:
        ordered = db.query(func.sum(POItem.quantity_ordered)).filter(
            POItem.po_id == po_id
        ).scalar() or 0
        received = db.query(func.sum(GRItem.quantity_received)).join(GoodsReceipt).filter(
            GoodsReceipt.po_id == po_id
        ).scalar() or 0
        return {"ordered": ordered, "received": received}
    finally:
        db.close()

def get_supplier_profile(supplier_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(Supplier).filter(
            Supplier.supplier_code == supplier_code
        ).first()
    finally:
        db.close()


def rank_suppliers_by_performance():
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Supplier.supplier_name,
            func.count(PurchaseOrder.po_id).label("total_orders")
        ).join(PurchaseOrder).group_by(
            Supplier.supplier_name
        ).order_by(func.count(PurchaseOrder.po_id).desc()).all()
    finally:
        db.close()

def get_inventory_transaction_logs(product_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            InventoryTransactionLog.transaction_type,
            InventoryTransactionLog.quantity_change,
            InventoryTransactionLog.transaction_date
        ).filter(
            InventoryTransactionLog.product_id == product_id
        ).order_by(
            InventoryTransactionLog.transaction_date.desc()
        ).all()
    finally:
        db.close()

def get_stocktake_status(stocktake_code: str):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Stocktake.stocktake_code,
            Stocktake.status
        ).filter(
            Stocktake.stocktake_code == stocktake_code
        ).first()
    finally:
        db.close()


def get_stocktake_detail(stocktake_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            StocktakeDetail.system_quantity,
            StocktakeDetail.actual_quantity
        ).join(StocktakeDetail).join(Product).filter(
            StocktakeDetail.stocktake_id == stocktake_id
        ).all()
    finally:
        db.close()


def get_stock_variance_report(stocktake_id: int):
    db = SupplyChainSessionLocal()
    try:
        return db.query(
            Product.product_name,
            (StocktakeDetail.actual_quantity - StocktakeDetail.system_quantity).label("variance")
        ).join(StocktakeDetail).join(Product).filter(
            StocktakeDetail.stocktake_id == stocktake_id
        ).all()
    finally:
        db.close()

