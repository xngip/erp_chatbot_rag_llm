from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

HRM_ENGINE = create_engine(
    settings.HRM_DATABASE_URL,
    echo=True
)

HrmSessionLocal = sessionmaker(bind=HRM_ENGINE)

HrmBase = declarative_base()