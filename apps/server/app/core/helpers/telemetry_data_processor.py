from datetime import datetime
from hydra_types.telemetry import (
    Log,
    Metric,
    TelemetryBatch,
    Trace,
)
from sqlmodel import Session

from app.core.database.incident_store import IncidentStore
from app.core.database.logs_store import LogStore
from app.core.database.metrics_store import MetricStore
from app.core.database.trace_store import TraceStore


class TelemetryDataProcessor:
    """Helper class to process incoming telemetry data"""

    def __init__(self, db_session: Session):
        self.metric_store = MetricStore(db_session)
        self.log_store = LogStore(db_session)
        self.incident_store = IncidentStore(db_session)
        self.trace_store = TraceStore(db_session)

    def store_telemetries(self, telemetry_data: TelemetryBatch, organization_id: str):
        """
        Process a batch of telemetry data
        Args:
            telemetry_data: Dictionary containing metrics, logs, traces, events, incidents
            organization_id: Organization identifier
        """
        # Process metrics first (no dependencies)
        if telemetry_data.metrics:
            metrics_data = []
            for metric in telemetry_data.metrics:
                metric_data = Metric(
                    service_name=telemetry_data.source_system,
                    metric_name=metric.metric_name,
                    service_version=metric.service_version,
                    value=metric.value,
                    labels=metric.labels,
                    unit=metric.unit,
                    timestamp=datetime.fromisoformat(
                        str(metric.timestamp).replace("Z", "+00:00")
                    ),
                )
                metrics_data.append(metric_data)
            if metrics_data:
                self.metric_store.bulk_create_metrics(metrics_data, organization_id)

        # Process traces first to ensure they exist before logs reference them
        if telemetry_data.traces:
            traces_data = []
            for trace in telemetry_data.traces:
                trace_data = Trace(
                    trace_id=trace.trace_id,
                    span_id=trace.span_id,
                    parent_span_id=trace.parent_span_id,
                    operation_name=trace.operation_name,
                    start_time=trace.start_time,
                    end_time=trace.end_time,
                    duration_ms=trace.duration_ms,
                    status=trace.status,
                    attributes=trace.attributes,
                    service_name=trace.service_name,
                    service_version=trace.service_version,
                )
                traces_data.append(trace_data)
            if traces_data:
                self.trace_store.bulk_create_traces(traces_data, organization_id)

        # Process logs after traces to ensure trace_id references exist
        if telemetry_data.logs:
            logs_data = []
            for log in telemetry_data.logs:
                log_data = Log(
                    service_name=log.service_name,
                    service_version=log.service_version,
                    level=log.level,
                    message=log.message,
                    trace_id=log.trace_id,
                    span_id=log.span_id,
                    structured_data=log.structured_data,
                    timestamp=log.timestamp,
                )
                logs_data.append(log_data)
            if logs_data:
                self.log_store.bulk_create_logs(logs_data, organization_id)
