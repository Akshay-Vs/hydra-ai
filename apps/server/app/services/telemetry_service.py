from datetime import datetime
import json
from sqlmodel import Session

from app.core.database.aggregate_reader import AggregateReader
from app.core.database.aggregate_store import AggregateStore
from app.core.telemetry.aggregate_telemetry import AggregateTelemetry
from app.core.types.aggregate_telemetry import AggregationGranularity
from app.services.database_service import get_session
from app.utils.datetime_from_now import datetime_from_now


class TelemetryService:
    def __init__(self, session: Session):
        self.session = session
        self.aggregate_store = AggregateStore(session)
        self.aggrigator = AggregateTelemetry(session)

    def run_aggregation_job(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        """
        Main aggregation job - typically run every minute via scheduler.
        Aggregates the previous minute's data.
        """

        metrics_args = self.aggrigator.aggregate_metrics(
            org_id, start_time, end_time, granularity
        )
        logs_args = self.aggrigator.aggregate_logs(
            org_id, start_time, end_time, granularity
        )
        incidents_args = self.aggrigator.aggregate_incidents(
            org_id, start_time, end_time
        )

        # store aggregated data
        self.aggregate_store.store_metric_aggregations(
            org_id, metrics_args, granularity
        )

        self.aggregate_store.store_log_aggregations(org_id, logs_args, granularity)

        self.aggregate_store.store_incident_aggregations(
            org_id, incidents_args, granularity
        )


if __name__ == "__main__":
    with get_session() as session:
        telemetry_service = TelemetryService(session)
        telemetry_service.run_aggregation_job(
            org_id="cmf17m0o6000107n3i3sumqup",
            start_time=datetime_from_now(-90),
            end_time=datetime.now(),
            granularity=AggregationGranularity.ONE_MINUTE,
        )
