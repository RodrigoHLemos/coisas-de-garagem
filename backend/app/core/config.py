"""
Configuration module following Single Responsibility Principle.
Each configuration class has a single, well-defined purpose.
"""
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache


class AppSettings(BaseSettings):
    """Application-specific settings"""
    app_name: str = Field(default="Coisas de Garagem API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")
    api_v1_prefix: str = Field(default="/api/v1")

    class Config:
        env_file = ".env"
        extra = "ignore"


class ServerSettings(BaseSettings):
    """Server configuration settings"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=False)
    workers: int = Field(default=1)

    class Config:
        env_file = ".env"
        extra = "ignore"


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    database_url: str = Field(...)
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=40)
    database_pool_timeout: int = Field(default=30)

    class Config:
        env_file = ".env"
        extra = "ignore"


class SecuritySettings(BaseSettings):
    """Security and authentication settings"""
    secret_key: str = Field(...)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    password_min_length: int = Field(default=8)
    bcrypt_rounds: int = Field(default=12)

    class Config:
        env_file = ".env"
        extra = "ignore"


class CORSSettings(BaseSettings):
    """CORS configuration settings"""
    cors_origins: List[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Se for "*", retorna como está
            if v == "*":
                return ["*"]
            # Senão, divide por vírgula
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


class RedisSettings(BaseSettings):
    """Configuração de cache Redis"""
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_ttl: int = Field(default=3600)
    redis_max_connections: int = Field(default=50)

    class Config:
        env_file = ".env"
        extra = "ignore"


class SupabaseSettings(BaseSettings):
    """Configurações do Supabase"""
    url: str = Field(...)
    anon_key: str = Field(...)
    service_key: str = Field(...)
    jwt_secret: Optional[str] = Field(default=None)
    storage_bucket: str = Field(default="products")
    qr_bucket: str = Field(default="qr-codes")

    class Config:
        env_file = ".env"
        env_prefix = "SUPABASE_"
        extra = "ignore"


class StorageSettings(BaseSettings):
    """Configuração de armazenamento de arquivos"""
    storage_type: str = Field(default="supabase")  # supabase, local
    local_storage_path: str = Field(default="./uploads")
    max_file_size: int = Field(default=5242880)  # 5MB
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"]
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


class QRCodeSettings(BaseSettings):
    """QR Code generation settings"""
    qr_code_base_url: str = Field(...)
    qr_code_version: int = Field(default=1)
    qr_code_box_size: int = Field(default=10)
    qr_code_border: int = Field(default=5)
    qr_code_fill_color: str = Field(default="black")
    qr_code_back_color: str = Field(default="white")

    class Config:
        env_file = ".env"
        extra = "ignore"


class PaginationSettings(BaseSettings):
    """Pagination settings"""
    default_page_size: int = Field(default=20)
    max_page_size: int = Field(default=100)

    class Config:
        env_file = ".env"
        extra = "ignore"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="production")

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings:
    """
    Main settings class that aggregates all configuration classes.
    This follows the Facade pattern to provide a unified interface.
    """
    def __init__(self):
        self.app = AppSettings()
        self.server = ServerSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()
        self.cors = CORSSettings()
        self.redis = RedisSettings()
        self.supabase = SupabaseSettings()
        self.storage = StorageSettings()
        self.qr_code = QRCodeSettings()
        self.pagination = PaginationSettings()
        self.logging = LoggingSettings()

    @property
    def is_development(self) -> bool:
        return self.app.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.app.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.app.environment == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    Uses Singleton pattern through lru_cache.
    """
    return Settings()