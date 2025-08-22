from fastapi import APIRouter

from typing import List
from app.core.types.telemetry_type import Event
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def receive_event(event: List[Event]):
    """
    Receive an event for processing.
    """
    logger.info(f"Received event: {event}")

    # Here you would typically process the event
    # For now, we just log it and return a success message
    return {"status": "success", "message": "Event received successfully"}
