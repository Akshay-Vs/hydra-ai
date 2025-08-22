from fastapi import APIRouter

from typing import List
from hydra_types.telemetry import Incident
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def receive_incident(incident: List[Incident]):
    """
    Receive an incident for processing.
    """
    logger.info(f"Received incident: {incident}")

    # Here you would typically process the incident
    # For now, we just log it and return a success message
    return {"status": "success", "message": "Incident received successfully"}
