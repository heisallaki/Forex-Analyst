from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Forex Trading Analyst"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REDIS_URL: str = "redis://localhost:6379/0"
    TWELVE_DATA_API_KEY: str
    TWELVE_DATA_REST_URL: str = "https://api.twelvedata.com"
    TWELVE_DATA_WS_URL: str = "wss://ws.twelvedata.com/v1/quotes/price"
    MARKET_INSTRUMENTS: list[str] = [
        "EUR/USD",
        "GBP/USD",
        "USD/JPY",
        "USD/CHF",
        "AUD/USD",
        "USD/CAD",
        "NZD/USD",
        "XAU/USD",
    ]
    MODEL_STORAGE_PATH: str = "./models"
    EXECUTION_ENABLED: bool = False
    EXECUTION_MAX_POSITION_SIZE: float = 10000.0
    EXECUTION_MAX_OPEN_POSITIONS: int = 3
    EXECUTION_MAX_DAILY_LOSS_PCT: float = 5.0


settings = Settings()
