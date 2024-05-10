# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    admin_email: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
