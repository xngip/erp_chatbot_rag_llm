from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

SALE_CRM_DATABASE_URL = settings.SALE_CRM_DATABASE_URL

sale_crm_engine = create_engine(SALE_CRM_DATABASE_URL, echo=True)

SaleCrmSessionLocal = sessionmaker(bind=sale_crm_engine)
SaleCrmBase = declarative_base()