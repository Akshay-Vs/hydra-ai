import asyncio
from os import path
from sys import version
import socketio
from app.config.settings import settings
from app.core.auth import ClerkSocketIOAuth
from app.utils.logging import create_logger
from socketio.exceptions import ConnectionRefusedError

logger = create_logger("socketio-service")

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.socketio_cors_allowed_origins,
    async_mode=settings.socketio_async_mode,
)

logger.info("Socket.IO application mounted", version="1.0.0")


@sio.event
async def connect(sid, environ, auth):
    if not auth:
        raise ConnectionRefusedError(
            "No authentication provided",
            {"error_code": "AUTH_MISSING", "status_code": 401},
        )

    if "token" not in auth:
        raise ConnectionRefusedError(
            "Token required", {"error_code": "TOKEN_MISSING", "status_code": 401}
        )

    try:
        if not settings.clerk_secret_key:
            raise ValueError(
                "Clerk secret key is not configured",
                {"error_code": "CONFIG_ERROR", "status_code": 500},
            )
        authenticator = ClerkSocketIOAuth(settings.clerk_secret_key)
        validated_user = await authenticator.authenticate_socket_request(environ, auth["token"])

        logger.debug(f"Validated user: {validated_user}")

        if validated_user is None:
            raise ConnectionRefusedError(
                "Invalid token", {"error_code": "TOKEN_INVALID", "status_code": 401}
            )

    except Exception as e:
        logger.error(f"Authentication failed for client {sid}: {str(e)}")
        raise ConnectionRefusedError(
            "Authentication failed", {"error_code": "AUTH_FAILED", "status_code": 401}
        )

    logger.info(f"Client {sid} connected with auth: {auth}")
    await sio.emit("status", {"msg": "Connected to server"}, room=sid)
    return True


@sio.event
async def disconnect(sid, reason):
    logger.info(f"Client {sid} disconnected {reason}")
    await sio.emit("status", {"msg": reason}, room=sid)


@sio.event
async def message(sid, data):
    logger.info(f"Received message from {sid}: {data}")
    # Echo the message back to the client
    logger.debug(f"Echoing data: {data}")
    await sio.emit("message", {"echo": data}, room=sid)
    return "Message received"
