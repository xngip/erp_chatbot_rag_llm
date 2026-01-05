# app/db/finance_database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.FINANCE_DATABASE_URL,
    echo=True 
)

FinanceSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

FinanceBase = declarative_base()
