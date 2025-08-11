from app.config.settings import settings
from app.core.auth.clerk_auth import ClerkSocketIOAuth
from app.core.auth.decorators import create_auth_decorators
from app.core.auth.session_manager import SessionManager
from app.utils.logging import create_logger
from socketio.exceptions import ConnectionRefusedError

import socketio

logger = create_logger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.socketio_cors_allowed_origins,
    async_mode=settings.socketio_async_mode,
)

session_manager = SessionManager()

# Create decorators with injected dependencies
auth_decorators = create_auth_decorators(session_manager, sio)
require_permission = auth_decorators['require_permission']
require_role = auth_decorators['require_role']
authenticated_only = auth_decorators['authenticated_only']


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
        user = await authenticator.authenticate(environ, auth["token"])

        logger.debug(f"Validated user: {user}, \n type: {type(user)}")

        if user is None:
            raise ConnectionRefusedError(
                "Invalid token", {"error_code": "TOKEN_INVALID", "status_code": 401}
            )


        # Create session data
        user_session = await session_manager.create_session(sid, user)

        # Join the user to their session room
        await sio.enter_room(sid, f"user_{user_session.user_id}")
        await sio.enter_room(sid, f"org_{user_session.org_id}")

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
@require_permission("chat")
async def message(sid, session, data):
    logger.info(f"Received message from {sid}: {data}")
    # Echo the message back to the client
    logger.debug(f"Echoing data: {data}")
    await sio.emit("message", {"echo": data}, room=sid)
    return "Message received"
