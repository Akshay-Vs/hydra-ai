from eventemitter import EventEmitter

from app.utils.logging import create_logger

# Event Emitter
emitter = EventEmitter()
logger = create_logger(__name__)


def emit(event_name: str, data: dict):
    """Emit an event with data"""
    logger.info(f"Emitting event: {event_name}")
    emitter.emit(event_name, data)


def capture(event_name: str, callback):
    """Capture an event and call a callback function"""
    logger.info(f"Capturing event: {event_name}")
    emitter.on(event_name, callback)
