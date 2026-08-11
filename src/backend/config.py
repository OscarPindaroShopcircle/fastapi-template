from functools import lru_cache
from typing import List, Protocol, Optional

from pydantic import Field, SecretStr, BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import (
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        yaml_file="config.yaml",
        extra="ignore",
        env_nested_delimiter="__",
        populate_by_name=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


class DatabaseSettingsProtocol(Protocol):
    """Protocol that all database settings must satisfy."""

    @property
    def async_url(self) -> str: ...

    @property
    def sync_url(self) -> str: ...


class PostgresConfig(BaseConfig):
    """PostgreSQL database configuration."""

    user: str = Field(description="Database username")
    password: SecretStr = Field(description="Database password")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    db: str = Field(description="Database name")

    @property
    def sync_url(self) -> str:
        """Build synchronous PostgreSQL connection URL."""
        return (
            f"postgresql://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db}"
        )

    @property
    def async_url(self) -> str:
        """Build asynchronous PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class MigratorConfig(PostgresConfig):
    """PostgreSQL credentials for running Alembic migrations.

    Uses a separate, more-privileged role than the runtime app.
    Only sync_url is meaningful here — Alembic doesn't use async.
    """

    pass


class SQLiteSettings(BaseSettings):
    """SQLite database configuration."""

    db_path: str = Field(default="app.db", description="Path to SQLite database file")

    @property
    def sync_url(self) -> str:
        """Build synchronous SQLite connection URL."""
        return f"sqlite:///{self.db_path}"

    @property
    def async_url(self) -> str:
        """Build asynchronous SQLite connection URL (using aiosqlite)."""
        return f"sqlite+aiosqlite:///{self.db_path}"


class FrontendConfig(BaseModel):
    """Frontend configuration."""

    enabled: bool = Field(default=True, description="Enable frontend rendering")
    templates_dir: Optional[str] = Field(
        default=None, description="Path to Jinja2 templates directory (optional)"
    )
    components_dir: str = Field(
        default="components", description="Path to JinjaX components directory"
    )
    static_dir: str = Field(
        default="static", description="Path to static files directory"
    )


class LoggingConfig(BaseModel):
    """Application logging configuration.

    All modules use ``logging.getLogger(__name__)`` and inherit from the root
    logger configured in ``log.py`` — no per-module handlers needed.
    """

    level: str = Field(default="INFO", alias="LOGGING__LEVEL")
    dir: str = Field(default="logs", alias="LOGGING__DIR")


class GoogleSSOConfig(BaseModel):
    """Google OAuth/OIDC credentials for fastapi-sso."""

    client_id: str
    client_secret: SecretStr


class AuthConfig(BaseModel):
    """Authentication configuration — JWT tokens, Google SSO, invitations."""

    google: Optional[GoogleSSOConfig] = None
    jwt_secret: SecretStr
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    invitation_expire_days: int = 7
    bootstrap_admin_email: Optional[str] = None
    redirect_uri: str = "http://localhost:8000/auth/callback"
    cookie_secure: Optional[bool] = None  # None = auto (True unless env=dev)


class StorageConfig(BaseModel):
    """Local-disk storage settings for uploaded files."""

    storage_root: str = Field(
        default="./data/uploads",
        description="Root directory uploaded files are written under",
    )


class AppConfig(BaseConfig):
    env: str = Field(default="dev")
    database: PostgresConfig = Field(default_factory=PostgresConfig)
    migrator: MigratorConfig = Field(default_factory=MigratorConfig)
    frontend: Optional[FrontendConfig] = Field(default=None)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    auth: Optional[AuthConfig] = Field(default=None)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    # Server configuration
    backend_host: str = Field(
        default="localhost", description="Server host", alias="HOST"
    )
    backend_port: int = Field(default=8000, description="Server port", alias="PORT")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["*"], description="CORS allowed origins", alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow CORS credentials",
        alias="CORS_ALLOW_CREDENTIALS",
    )
    cors_allow_methods: List[str] = Field(
        default=["*"], description="CORS allowed methods", alias="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], description="CORS allowed headers", alias="CORS_ALLOW_HEADERS"
    )


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    """Get or create API configuration singleton."""
    return AppConfig()
