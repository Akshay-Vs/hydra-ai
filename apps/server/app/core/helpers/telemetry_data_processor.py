from datetime import datetime
from hydra_types.telemetry import TelemetryBatch
from sqlmodel import Session

from app.core.database.incident_store import IncidentStore
from app.core.database.logs_store import LogStore
from app.core.database.metrics_store import MetricStore
from app.models.enums import LogLevelEnum, SeverityEnum


class TelemetryDataProcessor:
    """Helper class to process incoming telemetry data"""

    def __init__(self, db_session: Session):
        self.metric_store = MetricStore(db_session)
        self.log_store = LogStore(db_session)
        self.incident_store = IncidentStore(db_session)

    def process_telemetry_batch(
        self, telemetry_data: TelemetryBatch, organization_id: str
    ):
        """
        Process a batch of telemetry data

        Args:
            telemetry_data: Dictionary containing metrics, logs, traces, events, incidents
            organization_id: Organization identifier
        """
        # Process metrics
        if telemetry_data.metrics:
            metrics_data = []
            for metric in telemetry_data.metrics:
                metric_data = {
                    "service_name": telemetry_data.source_system,
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "labels": metric.labels,
                    "unit": metric.unit,
                    "timestamp": datetime.fromisoformat(
                        str(metric.timestamp).replace("Z", "+00:00")
                    ),
                    "organization_id": organization_id,
                }
                metrics_data.append(metric_data)

            if metrics_data:
                self.metric_store.bulk_create_metrics(metrics_data)

        # Process logs
        if telemetry_data.logs:
            logs_data = []
            for log in telemetry_data.logs:
                log_data = {
                    "service_name": telemetry_data.source_system,
                    "level": LogLevelEnum(log.level),
                    "message": log.message,
                    "trace_id": log.trace_id,
                    "span_id": log.span_id,
                    "structured_data": log.structured_data,
                    "timestamp": datetime.fromisoformat(
                        str(log.timestamp).replace("Z", "+00:00")
                    ),
                    "organization_id": organization_id,
                }
                logs_data.append(log_data)

            if logs_data:
                self.log_store.bulk_create_logs(logs_data)

        # Process incidents
        if telemetry_data.incidents:
            for incident in telemetry_data.incidents:
                self.incident_store.create_incident(
                    service_name=telemetry_data.source_system,
                    severity=SeverityEnum(incident.severity),
                    title=incident.title,
                    description=incident.description,
                    error_signature=incident.error_signature,
                    context_data=incident.context_data,
                    timestamp=datetime.fromisoformat(
                        str(incident.timestamp).replace("Z", "+00:00")
                    ),
                    organization_id=organization_id,
                )
