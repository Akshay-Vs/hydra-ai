from datetime import datetime, timezone
from sqlmodel import Session

from app.core.database.aggregate_store import AggregateStore
from app.core.database.aggregation_checkpoint import AggregationCheckpointStore
from app.core.telemetry.aggregate_telemetry import AggregateTelemetry
from app.core.types.aggregate_telemetry import AggregationGranularity
from app.models.sql_model import (
    IncidentAggregation1h,
    LogAggregation1m,
    MetricAggregation1m,
)
from app.utils.logging import create_logger
from app.utils.now import now

logger = create_logger(__name__)


class TelemetryService:
    def __init__(self, session: Session):
        self.session = session
        self.aggregate_store = AggregateStore(session)
        self.aggrigator = AggregateTelemetry(session)
        self.checkpoint_store = AggregationCheckpointStore(session)

    def run_all_aggregation_job(
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
        self.aggrigate_metrics(org_id, start_time, end_time, granularity)
        self.aggrigate_logs(org_id, start_time, end_time, granularity)
        self.aggrigate_incidents(org_id, start_time, end_time, granularity)

    def aggrigate_metrics(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        metrics_args = self.aggrigator.aggregate_metrics(
            org_id, start_time, end_time, granularity
        )

        # store aggregated metrics
        self.aggregate_store.store_metric_aggregations(
            org_id, metrics_args, granularity
        )

    def aggrigate_logs(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        logs_args = self.aggrigator.aggregate_logs(
            org_id, start_time, end_time, granularity
        )

        # store aggregated logs
        self.aggregate_store.store_log_aggregations(org_id, logs_args, granularity)

    def aggrigate_incidents(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        incidents_args = self.aggrigator.aggregate_incidents(
            org_id, start_time, end_time
        )

        # store aggregated incidents
        self.aggregate_store.store_incident_aggregations(
            org_id, incidents_args, granularity
        )

    def auto_aggregate(self, org_id: str, threshold: int = (60 * 15)):  # runs every 15 minutes
        """
        Automatically aggregates the previous minute's data.
        """

        try:
            # Map each table to its respective aggregation method
            aggregation_map = {
                MetricAggregation1m: self.aggrigate_metrics,
                LogAggregation1m: self.aggrigate_logs,
                IncidentAggregation1h: self.aggrigate_incidents,
            }

            _now = now()

            for table, aggregator in aggregation_map.items():
                last_aggregated_at = self.checkpoint_store.last_aggregated_at(
                    org_id, table.__tablename__
                )

                if last_aggregated_at.tzinfo is None:
                    last_aggregated_at = last_aggregated_at.replace(tzinfo=timezone.utc)

                time_delta = _now - last_aggregated_at

                logger.debug(f"Last aggregated at: {last_aggregated_at}")
                logger.debug(f"Now: {_now}")
                logger.debug(f"Threshold: {threshold}")
                logger.debug(f"Time delta: {time_delta}")

                if time_delta.total_seconds() > threshold and aggregator:
                    logger.info(
                        f"Auto-aggregated {table.__tablename__} data for {org_id} from {last_aggregated_at} to {_now}"
                    )
                    aggregator(org_id, last_aggregated_at, _now)
                    self.checkpoint_store.update_timestamp(
                        org_id, table.__tablename__, _now
                    )

        except Exception as e:
            logger.error(f"Error in auto-aggregation: {e}")
