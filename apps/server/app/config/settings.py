from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "FastAPI SocketIO Server"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    # Socket.IO settings
    socketio_cors_allowed_origins: str = "*"
    socketio_async_mode: str = "asgi"

    # Logging
    log_level: str = "INFO"

    # Security
    secret_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
