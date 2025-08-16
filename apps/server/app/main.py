from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.utils.logging import setup_logging, create_logger

from app.services.socketio_service import sio
from app.services.database_service import init_database  # , seed_database

from app.api.routes import health, user_route, onboarding

import socketio


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
app.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.exception_handler(HTTPException)
async def global_exception_handler(request: Request, exc: HTTPException):
    logger = create_logger("main")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": exc.detail if hasattr(exc, "detail") else "Internal Server Error",
            "status_code": exc.status_code if hasattr(exc, "status_code") else 500,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger = create_logger("main")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "status_code": 500,
        },
    )


# Mount Socket.IO
asgi_app = socketio.ASGIApp(sio, app)
