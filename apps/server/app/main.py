from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from contextlib import asynccontextmanager

from app.api.routes.auth import m2m
from app.api.routes.telemetry import batch, events, incidents, logs, metrics
from app.config.settings import settings
from app.utils.logging import setup_logging, create_logger

from app.services.socketio_service import sio
from app.services.database_service import init_database  # , seed_database

from app.api.routes import (
    health,
    organization,
    organization_credentials,
    user_route,
    onboarding,
)

import socketio


logger = create_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(log_level="DEBUG", json_logs=False)
    # Create logger
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
app.include_router(organization.router, prefix="/org", tags=["organizations"])

# /telemetry routes
app.include_router(batch.router, prefix="/telemetry/batch", tags=["telemetry"])
app.include_router(events.router, prefix="/telemetry/events", tags=["telemetry"])
app.include_router(incidents.router, prefix="/telemetry/incidents", tags=["telemetry"])
app.include_router(logs.router, prefix="/telemetry/logs", tags=["telemetry"])
app.include_router(metrics.router, prefix="/telemetry/metrics", tags=["telemetry"])

# /auth/m2m routes
app.include_router(m2m.router, prefix="/auth/m2m", tags=["auth"])

app.include_router(
    organization_credentials.router, prefix="/org/credentials", tags=["org_credentials"]
)
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.exception_handler(HTTPException)
async def global_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.detail}", exc_info=True)
    logger.debug(f"Trace: {exc}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code if hasattr(exc, "status_code") else 500,
        content={
            "detail": exc.detail if hasattr(exc, "detail") else "Internal Server Error",
            "status_code": exc.status_code if hasattr(exc, "status_code") else 500,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}", exc_info=True)
    logger.debug(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
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
