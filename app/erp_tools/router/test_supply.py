import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)
sys.path.insert(0, PROJECT_ROOT)

from app.erp_tools.router.supply_chain_router import supply_chain_router

print(supply_chain_router("Sản phẩm iPhone 15 còn hàng không?"))
print(supply_chain_router("Đơn mua PO-001 đã nhập bao nhiêu %?"))
print(supply_chain_router("Kho Hà Nội còn bao nhiêu laptop?"))
