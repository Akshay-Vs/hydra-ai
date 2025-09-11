from datetime import datetime, timedelta
from fastapi import APIRouter, Depends

from hydra_types.telemetry import TelemetryBatch
from sqlmodel import Session
from app.core.auth.m2m_auth import get_current_client
from app.core.helpers.telemetry_data_processor import TelemetryDataProcessor
from app.core.types.auth_type import SessionClient
from app.services.database_service import get_db_session
from app.utils.logging import create_logger
from app.core.database.aggregate_reader import AggregateReader
from app.core.telemetry.anomaly_detection import (
    AnomalyDetectionEngine,
    AnomalyThresholds,
)

from app.utils.threads import fire_and_forget

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
    logger.debug(f"Authenticated as {client}")

    telemetry_processor = TelemetryDataProcessor(session)

    if not client.organization_id:
        logger.error("Client does not have an associated organization_id")
        return {
            "status": "error",
            "message": "Client does not have an associated organization",
        }

    telemetry_processor.store_telemetries(batch, client.organization_id)
    getter = AggregateReader(session)

    historic_metrics = getter.get_aggregated_metrics(
        organization_id=client.organization_id,
        metric_name="cpu.usage",
        start_time=datetime.now() - timedelta(hours=100),
        end_time=datetime.now(),
    )
    historic_logs = getter.get_aggregated_logs(
        organization_id=client.organization_id,
        service_name="my-fastapi-service",
        start_time=datetime.now() - timedelta(hours=100),
        end_time=datetime.now(),
    )

    # Initialize the engine
    logger.info("Initializing anomaly detection engine")
    thresholds = AnomalyThresholds(
        error_rate_absolute=60.0,
        error_rate_increase=25.0,
        latency_increase=50.0,
        resource_increase=40.0,
    )

    engine = AnomalyDetectionEngine(thresholds)

    # Detect anomalies
    logger.info("Detecting anomalies")
    anomalies = engine.detect_anomalies(batch, historic_metrics, historic_logs)

    # Process results
    logger.info("Processing anomalies")
    if not anomalies:
        logger.info("No anomalies detected")
        return {"status": "success", "message": "Batch received successfully"}

    for anomaly in anomalies:
        logger.info(f"Anomaly detected: {anomaly.model_dump_json(indent=2)}")
