import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.utils.logging import setup_logging, create_logger

from app.services.socketio_service import sio
from app.services.database_service import init_database#, seed_database

from app.api.routes import health
from app.api.routes import user_route

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(log_level="DEBUG", json_logs=False)
    # Create logger
    logger = create_logger("main")
    logger.info("Application starting", version="1.0.0")

    # Initialize database
    init_database()
    # seed_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    debug=settings.debug,
    version=settings.app_version,
)

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
app.include_router(user_route.router, prefix="/user", tags=["users"])
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Mount Socket.IO
asgi_app = socketio.ASGIApp(sio, app)
