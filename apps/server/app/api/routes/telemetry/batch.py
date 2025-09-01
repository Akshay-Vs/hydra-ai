from fastapi import APIRouter, Depends

from hydra_types.telemetry import TelemetryBatch
from sqlmodel import Session
from app.core.auth.m2m_auth import get_current_client
from app.core.helpers.telemetry_data_processor import TelemetryDataProcessor
from app.core.types.auth_type import SessionClient
from app.services.database_service import get_db_session
from app.utils.logging import create_logger

router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
def receive_batch(
    batch: TelemetryBatch,
    client: SessionClient = Depends(get_current_client),
    session: Session = Depends(get_db_session),
):
    """
    Receive a batch of data for processing.
    """
    logger.debug(f"Received batch: {batch.model_dump_json(indent=2)}")
    logger.debug(f"Authenticated as {client}")

    telemetry_processor = TelemetryDataProcessor(session)

    if not client.organization_id:
        logger.error("Client does not have an associated organization_id")
        return {
            "status": "error",
            "message": "Client does not have an associated organization",
        }

    telemetry_processor.process_telemetry_batch(batch, client.organization_id)

    return {"status": "success", "message": "Batch received successfully"}
