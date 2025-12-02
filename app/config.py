"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "Android Package Uploader API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # OSS credentials (required)
    oss_access_key_id: str
    oss_access_key_secret: str
    
    # OSS configuration (with defaults)
    oss_endpoint: str = "https://oss-ap-southeast-1.aliyuncs.com"
    oss_bucket_name: str = "macaron-system"
    oss_region: str = "ap-southeast-1"
    oss_prefix: str = "android-packages"
    
    # Upload limits (increased for AAB files which can be larger)
    max_upload_size: int = 250 * 1024 * 1024  # 250MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

