import sys
import os

# Cho phép import app/*
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db.hrm_database import HRM_ENGINE, HrmBase

# BẮT BUỘC import models để SQLAlchemy biết các bảng
from app.erp_tools.modules.hrm import models  # noqa

def main():
    print("🚀 Creating HRM tables from ORM...")
    HrmBase.metadata.create_all(bind=HRM_ENGINE)
    print("✅ HRM tables created successfully.")

if __name__ == "__main__":
    main()
