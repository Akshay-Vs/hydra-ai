from typing import List
from fastapi import APIRouter

from hydra_types.telemetry import Metric
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def receive_metric(metric: List[Metric]):
    """
    Receive a metric for processing.
    """
    logger.info(f"Received metric: {metric}")

    # Here you would typically process the metric
    # For now, we just log it and return a success message
    return {"status": "success", "message": "Metric received successfully"}
