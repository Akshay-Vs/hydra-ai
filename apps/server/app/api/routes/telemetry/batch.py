from fastapi import APIRouter

from hydra_types.telemetry import TelemetryBatch
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
# TODO: Perform M2M authentication
def receive_batch(batch: TelemetryBatch):
    """
    Receive a batch of data for processing.
    """
    logger.info(f"Received batch: {batch.model_dump_json(indent=2)}")

    # Here you would typically process the batch
    # For now, we just log it and return a success message
    return {"status": "success", "message": "Batch received successfully"}
