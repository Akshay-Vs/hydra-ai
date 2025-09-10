from datetime import datetime, timedelta
import json
from fastapi import APIRouter, Depends

from hydra_types.telemetry import TelemetryBatch
from sqlmodel import Session
from app.core.auth.m2m_auth import get_current_client
from app.core.helpers.telemetry_data_processor import TelemetryDataProcessor
from app.core.types.auth_type import SessionClient
from app.services.database_service import get_db_session
from app.utils.logging import create_logger
from app.core.database.aggregate_reader import AggregateReader
from app.core.telemetry.anomaly_detection import TelemetryAnomalyDetector
from app.core.types.aggregate_telemetry import (
    MetricAggregationData,
)
from hydra_types.telemetry import TelemetryBatch

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
    logger.debug(f"Received: {batch.model_dump_json(indent=2)}")

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

    # Initialize and train detector
    detector = TelemetryAnomalyDetector(n_trees=30, contamination=0.05)
    detector.fit(historic_metrics=historic_metrics, historic_logs=historic_logs)

    # Predict anomalies
    results = detector.predict_batch(batch)

    # Print results
    detector.print_results(results)

    return {"status": "success", "message": "Batch received successfully"}
