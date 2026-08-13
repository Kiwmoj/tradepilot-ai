"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "TradePilot AI"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = Field(default="dev-secret-key-change-in-production-min-32-chars!!", min_length=32)
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://tradepilot:change-me@localhost:5432/tradepilot"
    )
    postgres_user: str = "tradepilot"
    postgres_password: str = "change-me"
    postgres_db: str = "tradepilot"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # Market data
    market_data_provider: str = "mock"
    alpha_vantage_api_key: str = ""
    finnhub_api_key: str = ""
    polygon_api_key: str = ""
    market_data_rate_limit_per_minute: int = 5
    market_data_timeout_seconds: int = 30
    market_data_max_retries: int = 3

    # Paper trading
    paper_starting_cash: float = 100_000.0
    paper_default_commission: float = 0.0

    # Agent
    agent_loop_interval_seconds: int = 60
    agent_default_symbols: str = "AAPL,MSFT,GOOGL,SPY,QQQ"

    # AI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_enabled: bool = False

    # Risk defaults
    risk_max_position_pct: float = 10.0
    risk_max_portfolio_exposure_pct: float = 80.0
    risk_max_risk_per_trade_pct: float = 2.0
    risk_max_daily_loss_pct: float = 5.0
    risk_max_drawdown_pct: float = 15.0
    risk_max_open_positions: int = 10
    risk_require_stop_loss: bool = True
    risk_trade_cooldown_seconds: int = 300
    risk_max_trades_per_day: int = 20

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | List[str]) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def agent_symbols_list(self) -> List[str]:
        return [s.strip().upper() for s in self.agent_default_symbols.split(",") if s.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
