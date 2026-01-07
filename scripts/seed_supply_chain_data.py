# scripts/seed_supply_chain_data.py
import sys
import os
from datetime import date, datetime, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from datetime import date
from app.db.supply_chain_database import SupplyChainSessionLocal

from app.erp_tools.modules.supply_chain.models import (
    Warehouse,
    BinLocation,
    ProductCategory,
    Product,
    Supplier,
    PurchaseRequest,
    PRItem,
    PurchaseOrder,
    POItem,
    GoodsReceipt,
    GRItem,
    CurrentStock,
)

def seed_supply_chain_data():
    db = SupplyChainSessionLocal()

    try:
        print("🌱 Seeding Supply Chain data...")

        # --------------------------------------------------
        # 1. Warehouses
        # --------------------------------------------------
        wh_hn = Warehouse(
            warehouse_code="WH-HN-01",
            warehouse_name="Kho Chính Hà Nội",
            warehouse_type="TRADING",
            address="Cầu Giấy, Hà Nội",
        )

        wh_asset = Warehouse(
            warehouse_code="WH-ASSET",
            warehouse_name="Kho Tài Sản",
            warehouse_type="ASSET",
            address="Văn phòng Công ty",
        )

        db.add_all([wh_hn, wh_asset])
        db.flush()

        # --------------------------------------------------
        # 2. Bin Locations
        # --------------------------------------------------
        bin_laptop = BinLocation(
            warehouse_id=wh_hn.warehouse_id,
            bin_code="A-01-01",
            description="Kệ Laptop - Tầng 1",
        )

        bin_phone = BinLocation(
            warehouse_id=wh_hn.warehouse_id,
            bin_code="A-01-02",
            description="Kệ Điện thoại - Tầng 1",
        )

        db.add_all([bin_laptop, bin_phone])
        db.flush()

        # --------------------------------------------------
        # 3. Product Categories
        # --------------------------------------------------
        cat_laptop = ProductCategory(category_name="Laptop")
        cat_phone = ProductCategory(category_name="Điện thoại")

        db.add_all([cat_laptop, cat_phone])
        db.flush()

        # --------------------------------------------------
        # 4. Products
        # --------------------------------------------------
        dell_xps = Product(
            sku="DELL-XPS13",
            product_name="Dell XPS 13 9310",
            category_id=cat_laptop.category_id,
            product_type="TRADING_GOODS",
            brand="Dell",
            min_stock_level=10,
        )

        iphone_15 = Product(
            sku="IPHONE-15",
            product_name="iPhone 15 Pro Max",
            category_id=cat_phone.category_id,
            product_type="TRADING_GOODS",
            brand="Apple",
            min_stock_level=20,
        )

        db.add_all([dell_xps, iphone_15])
        db.flush()

        # --------------------------------------------------
        # 5. Suppliers
        # --------------------------------------------------
        fpt_supplier = Supplier(
            supplier_code="SUP-FPT",
            supplier_name="FPT Trading",
            tax_code="0101234567",
            finance_partner_id=101,
        )

        digi_supplier = Supplier(
            supplier_code="SUP-DIGI",
            supplier_name="Digiworld",
            tax_code="0109876543",
            finance_partner_id=102,
        )

        db.add_all([fpt_supplier, digi_supplier])
        db.flush()

        # --------------------------------------------------
        # 6. Purchase Request
        # --------------------------------------------------
        pr = PurchaseRequest(
            pr_code="PR-001",
            requester_id=1,
            request_date=date.today(),
            reason="Bổ sung hàng bán tháng này",
            status="APPROVED",
        )

        db.add(pr)
        db.flush()

        pr_item_1 = PRItem(
            pr_id=pr.pr_id,
            product_id=dell_xps.product_id,
            quantity_requested=20,
        )

        pr_item_2 = PRItem(
            pr_id=pr.pr_id,
            product_id=iphone_15.product_id,
            quantity_requested=30,
        )

        db.add_all([pr_item_1, pr_item_2])

        # --------------------------------------------------
        # 7. Purchase Order
        # --------------------------------------------------
        po = PurchaseOrder(
            po_code="PO-001",
            supplier_id=fpt_supplier.supplier_id,
            order_date=date.today(),
            total_amount=500000000,
            status="APPROVED",
        )

        db.add(po)
        db.flush()

        po_item_1 = POItem(
            po_id=po.po_id,
            product_id=dell_xps.product_id,
            quantity_ordered=20,
            unit_price=20000000,
        )

        po_item_2 = POItem(
            po_id=po.po_id,
            product_id=iphone_15.product_id,
            quantity_ordered=30,
            unit_price=15000000,
        )

        db.add_all([po_item_1, po_item_2])

        # --------------------------------------------------
        # 8. Goods Receipt
        # --------------------------------------------------
        gr = GoodsReceipt(
            gr_code="GR-001",
            po_id=po.po_id,
            warehouse_id=wh_hn.warehouse_id,
            status="CONFIRMED",
        )

        db.add(gr)
        db.flush()

        gr_item_1 = GRItem(
            gr_id=gr.gr_id,
            product_id=dell_xps.product_id,
            bin_id=bin_laptop.bin_id,
            quantity_received=20,
        )

        gr_item_2 = GRItem(
            gr_id=gr.gr_id,
            product_id=iphone_15.product_id,
            bin_id=bin_phone.bin_id,
            quantity_received=30,
        )

        db.add_all([gr_item_1, gr_item_2])

        # --------------------------------------------------
        # 9. Current Stock
        # --------------------------------------------------
        stock_1 = CurrentStock(
            warehouse_id=wh_hn.warehouse_id,
            bin_id=bin_laptop.bin_id,
            product_id=dell_xps.product_id,
            quantity_on_hand=20,
        )

        stock_2 = CurrentStock(
            warehouse_id=wh_hn.warehouse_id,
            bin_id=bin_phone.bin_id,
            product_id=iphone_15.product_id,
            quantity_on_hand=30,
        )

        

        db.add_all([stock_1, stock_2])

        # --------------------------------------------------
        db.commit()
        print("✅ Seed Supply Chain data thành công!")

    except Exception as e:
        db.rollback()
        print("❌ Lỗi khi seed Supply Chain data")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_supply_chain_data()
