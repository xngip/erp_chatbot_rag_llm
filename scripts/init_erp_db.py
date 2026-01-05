import sys
import os

# Thao tác này giúp Python tìm thấy thư mục 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -------------------------------------

from app.db.database import engine, Base
from app.erp_tools.modules.sales_crm import models

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
