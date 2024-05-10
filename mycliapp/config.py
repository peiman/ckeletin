# config.py
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    admin_email: str

    # Use ConfigDict to specify a custom config file
    model_config = ConfigDict(env_file=".env")

settings = Settings()  # This line creates an instance of the Settings class
