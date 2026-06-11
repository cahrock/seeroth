"""Application settings — loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_port_ai: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://seeroth:password@localhost:5432/seeroth_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_temperature: float = 0.3

    # Market Data
    polygon_api_key: str = ""
    fmp_api_key: str = ""
    alpha_vantage_api_key: str = ""
    benzinga_api_key: str = ""

    # Halal Screening
    zoya_api_key: str = ""

    # Macro
    fred_api_key: str = ""

    # CORS
    cors_allowed_origins: list[str] = ["http://localhost:4200"]


settings = Settings()
