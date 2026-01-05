import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.db.sale_crm_database import sale_crm_engine, SaleCrmBase

# 🔥 BẮT BUỘC import models để SQLAlchemy biết bảng
from app.erp_tools.modules.sales_crm import models

print("Creating Sale & CRM tables...")
SaleCrmBase.metadata.create_all(bind=sale_crm_engine)
print("Done!")
