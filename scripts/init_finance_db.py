# scripts/init_finance_db.py
from app.db.finance_database import engine, FinanceBase
from app.db import finance_models  # noqa

print("Creating Finance & Accounting tables...")
FinanceBase.metadata.create_all(bind=engine)
print("Done.")
