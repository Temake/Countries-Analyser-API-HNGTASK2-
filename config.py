from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database
    database_url: str = "sqlite:///database.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # External APIs
    countries_api_url: str = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    exchange_rate_api_url: str = "https://open.er-api.com/v6/latest/USD"
    
    # Timeout settings
    api_timeout: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
