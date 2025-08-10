import socketio
from app.config.settings import settings
from app.utils.logging import create_logger

logger = create_logger("socketio-service")
# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.socketio_cors_allowed_origins,
    async_mode=settings.socketio_async_mode,
)

logger.info("Socket.IO application mounted", version="1.0.0")


@sio.event
async def connect(sid, environ, auth):
    print(f"Client {sid} connected")
    await sio.emit("status", {"msg": "Connected to server"}, room=sid)


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit("response", {"echo": data}, room=sid)
