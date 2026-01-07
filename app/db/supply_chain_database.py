from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

SUPPLY_CHAIN_DATABASE_URL = settings.SUPPLY_CHAIN_DATABASE_URL

SupplyChainEngine = create_engine(
    SUPPLY_CHAIN_DATABASE_URL,
    echo=True
)

SupplyChainSessionLocal = sessionmaker(
    bind=SupplyChainEngine
)

SupplyChainBase = declarative_base()
