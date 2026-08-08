"""
BATIP Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # ---------------------------------------------------------
    # Project
    # ---------------------------------------------------------

    APP_NAME: str = "BATIP"
    APP_VERSION: str = "0.1.0"

    # ---------------------------------------------------------
    # Data Provider
    # ---------------------------------------------------------

    DATA_PROVIDER: str = "mock"
    DEFAULT_SYMBOL: str = "BANKNIFTY"

    # ---------------------------------------------------------
    # NSE
    # ---------------------------------------------------------

    NSE_BASE_URL: str = "https://www.nseindia.com"

    NSE_OPTION_CHAIN_PAGE: str = (
        "https://www.nseindia.com/option-chain"
    )

    OPTION_CHAIN_URL: str = (
        "https://www.nseindia.com/api/option-chain-v3"
    )

    NSE_OPTION_CHAIN_CONTRACT_INFO_URL: str = (
        "https://www.nseindia.com/api/option-chain-contract-info"
    )

    NSE_DEFAULT_EXPIRY: str = "25-Aug-2026"

    MARKET_STATUS_URL: str = (
        "https://www.nseindia.com/api/marketStatus"
    )

    # ---------------------------------------------------------
    # HTTP
    # ---------------------------------------------------------

    REQUEST_TIMEOUT: int = 20
    MAX_RETRIES: int = 3

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    CACHE_TTL_SECONDS: int = 10

    # ---------------------------------------------------------
    # Pydantic
    # ---------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()