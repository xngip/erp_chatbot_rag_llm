# app/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# (Code tìm đường dẫn .env của bạn...)
app_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(app_dir)
env_path = os.path.join(project_root, ".env")


class Settings(BaseSettings):
    DATABASE_URL: str
    
    GOOGLE_API_KEY: str

    SALE_CRM_DATABASE_URL: str

    FINANCE_DATABASE_URL: str

    HRM_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=env_path)

# Tạo một đối tượng 'settings' duy nhất
settings = Settings()