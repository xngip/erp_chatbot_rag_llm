import sys
import os

# Cho phép import app/*
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db.supply_chain_database import SupplyChainEngine, SupplyChainBase
import app.erp_tools.modules.supply_chain.models

def init_supply_chain_db():
    print("🚀 Đang tạo bảng Supply Chain...")
    SupplyChainBase.metadata.create_all(bind=SupplyChainEngine)
    print("✅ Tạo database Supply Chain thành công!")

if __name__ == "__main__":
    init_supply_chain_db()
