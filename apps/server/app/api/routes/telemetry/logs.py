from fastapi import APIRouter
from typing import List

from app.core.types.telemetry_type import Log
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def receive_log(log_entry: List[Log]):
    """
    Receive a log entry for processing.
    """
    logger.info(f"Received log entry: {log_entry}")

    # Here you would typically process the log entry
    # For now, we just log it and return a success message
    return {"status": "success", "message": "Log entry received successfully"}
