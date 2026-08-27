"""
Configuration management using pydantic-settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_POOL_MIN_SIZE: int = 10
    DATABASE_POOL_MAX_SIZE: int = 50
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS - Use Union to prevent automatic JSON parsing
    CORS_ORIGINS: Union[str, List[str]] = []
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Parse CORS_ORIGINS from comma-separated string or JSON array format.
        
        Handles:
        - Already-parsed list (from JSON in some environments): return as-is
        - Comma-separated string: split and strip whitespace
        - JSON array string: parse as JSON
        - Empty string or None: return empty list
        """
        # Handle if already parsed as list
        if isinstance(v, list):
            return v
        
        # Handle string input
        if isinstance(v, str):
            # Empty string case
            if not v or v.strip() == '':
                return []
            
            # Try JSON parsing first (for backwards compatibility with JSON array format)
            if v.strip().startswith('['):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            
            # Parse as comma-separated string (Docker .env format)
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        
        # Fallback for unexpected types (None, etc.)
        return []
    
    # S3
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str = "us-east-1"
    
    # Payment Systems
    PAYME_MERCHANT_ID: str
    PAYME_SECRET_KEY: str
    CLICK_MERCHANT_ID: str
    CLICK_SECRET_KEY: str
    
    # SMS Gateway
    SMS_GATEWAY_URL: str
    SMS_GATEWAY_TOKEN: str
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        # Don't auto-parse complex types from JSON - let validators handle it
        json_schema_extra={'env_parse_none_str': None}
    )


settings = Settings()
