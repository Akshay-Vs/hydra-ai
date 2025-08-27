from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI SocketIO Server"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    # Socket.IO settings
    socketio_cors_allowed_origins: str = "*"
    socketio_async_mode: str = "asgi"

    # Logging
    log_level: str = "INFO"

    # Security
    secret_key: Optional[str] = None
    clerk_secret_key: Optional[str] = None
    access_token_expire_minutes: int = 30

    # Auth M2M
    session_expiry: int = 86400
    m2m_auth_secret_key: str = ""
    m2m_auth_algorithm: str = "HS256"

    # Database
    database_url: Optional[str] = None
    tidb_ssl_ca: Optional[Path] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
