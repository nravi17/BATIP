"""
BATIP Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project
    APP_NAME: str = "BATIP"
    APP_VERSION: str = "0.1.0"

    # NSE
    NSE_BASE_URL: str = "https://www.nseindia.com"
    OPTION_CHAIN_URL: str = (
        "https://www.nseindia.com/api/option-chain-indices"
    )
    MARKET_STATUS_URL: str = (
        "https://www.nseindia.com/api/marketStatus"
    )

    # HTTP
    REQUEST_TIMEOUT: int = 15
    MAX_RETRIES: int = 3

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )

    # Cache
    CACHE_TTL_SECONDS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()