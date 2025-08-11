from pydantic_settings import BaseSettings
from typing import Optional
import os

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(
    " "
)
HOST = os.getenv("HOST", "0.0.0")
PORT = int(os.getenv("PORT", 8000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class Settings(BaseSettings):
    app_name: str = "FastAPI SocketIO Server"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = HOST
    port: int = PORT
    cors_origins: list[str] = CORS_ALLOWED_ORIGINS

    # Socket.IO settings
    socketio_cors_allowed_origins: str = "*"
    socketio_async_mode: str = "asgi"

    # Logging
    log_level: str = LOG_LEVEL

    # Security
    secret_key: Optional[str] = None
    clerk_secret_key: Optional[str] = CLERK_SECRET_KEY
    session_expiry: int = 86400

    # Databasee
    redis_url: str = REDIS_URL

    class Config:
        env_file = ".env"


settings = Settings()
