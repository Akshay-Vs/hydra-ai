from logging import debug
from dotenv import load_dotenv
from pathlib import Path

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.api.routes import health
from app.services.socketio_service import sio
from app.utils.logging import setup_logging, create_logger

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(log_level="DEBUG", json_logs=False, development=True)

    # Create logger
    logger = create_logger("main")
    logger.info("Application starting", version="1.0.0")
    yield


app = FastAPI(lifespan=lifespan, title=settings.app_name, debug=settings.debug, version=settings.app_version)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Mount Socket.IO
asgi_app = socketio.ASGIApp(sio, app)
