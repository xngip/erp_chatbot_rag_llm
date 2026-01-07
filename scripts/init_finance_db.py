# scripts/init_finance_db.py
import sys
import os

# Cho phép import app/*
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db.finance_database import engine, FinanceBase

# Import toàn bộ models để SQLAlchemy biết cần tạo bảng nào
from app.erp_tools.modules.finance_accounting import models  # noqa: F401


def init_finance_db():
    print("🚀 Đang tạo bảng Finance & Accounting...")
    FinanceBase.metadata.create_all(bind=engine)
    print("✅ Tạo DB Finance & Accounting thành công!")


if __name__ == "__main__":
    init_finance_db()
