from datetime import datetime, timedelta
from typing import List

from sqlmodel import delete

from app.core.telemetry.telemetry_aggregator import (
    AggregationGranularity,
    IncidentAggregation,
    LogAggregation,
    MetricAggregation,
)
from app.models.sql_model import (
    IncidentAggregation1h,
    LogAggregation1m,
    MetricAggregation1h,
    MetricAggregation1m,
)
from app.utils.logging import create_logger
from app.utils.now import now

logger = create_logger(__name__)


class AggregateStore:
    def __init__(self, session):
        self.session = session

    def store_metric_aggregations(
        self,
        org_id: str,
        aggregations: List[MetricAggregation],
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        """Store aggregated metrics in the appropriate table."""
        if not aggregations:
            logger.info("No metric aggregations to store")
            return

        # Determine the target model based on granularity
        if granularity == AggregationGranularity.ONE_MINUTE:
            target_model = MetricAggregation1m
        elif granularity == AggregationGranularity.ONE_HOUR:
            target_model = MetricAggregation1h
        else:
            logger.error(f"Unsupported granularity: {granularity}")
            return

        # Convert MetricAggregation objects to the appropriate model instances
        model_instances = []
        for agg in aggregations:
            # Extract the data from the MetricAggregation object
            instance_data = {
                "timestamp": agg.timestamp,
                "service_name": agg.service_name,
                "metric_name": agg.metric_name,
                "avg_value": agg.avg_value,
                "min_value": agg.min_value,
                "max_value": agg.max_value,
                "count_values": agg.count_values,
                "sum_values": agg.sum_values,
                "organization_id": org_id,
                "created_at": now(),
            }

            # Add optional fields if they exist
            if hasattr(agg, "p50_value") and agg.p50_value is not None:
                instance_data["p50_value"] = agg.p50_value
            if hasattr(agg, "p95_value") and agg.p95_value is not None:
                instance_data["p95_value"] = agg.p95_value
            if hasattr(agg, "p99_value") and agg.p99_value is not None:
                instance_data["p99_value"] = agg.p99_value
            if hasattr(agg, "stddev_value") and agg.stddev_value is not None:
                instance_data["stddev_value"] = agg.stddev_value

            model_instances.append(target_model(**instance_data))

        # Insert all at once
        self.session.add_all(model_instances)
        self.session.commit()

        # Refresh all instances to get any auto-generated fields
        for instance in model_instances:
            self.session.refresh(instance)

        logger.info(f"Stored {len(model_instances)} metric aggregations")
        return model_instances

    def store_log_aggregations(
        self,
        org_id: str,
        aggregations: List[LogAggregation],
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ):
        """Store aggregated logs in the appropriate table."""
        if not aggregations:
            logger.info("No log aggregations to store")
            return

        # Currently only 1m granularity is supported for log aggregations
        if granularity != AggregationGranularity.ONE_MINUTE:
            logger.error(
                f"Log aggregations only support 1-minute granularity, got: {granularity}"
            )
            return

        target_model = LogAggregation1m

        # Convert LogAggregation objects to model instances
        model_instances = []
        for agg in aggregations:
            instance_data = {
                "timestamp": agg.timestamp,
                "service_name": agg.service_name,
                "total_logs": agg.total_logs,
                "error_count": getattr(agg, "error_count", 0),
                "warn_count": getattr(agg, "warn_count", 0),
                "info_count": getattr(agg, "info_count", 0),
                "debug_count": getattr(agg, "debug_count", 0),
                "error_rate": getattr(agg, "error_rate", 0.0),
                "unique_traces": getattr(agg, "unique_traces", 0),
                "organization_id": org_id,
                "created_at": now(),
            }

            model_instances.append(target_model(**instance_data))

        # Insert all at once
        self.session.add_all(model_instances)
        self.session.commit()

        # Refresh all instances
        for instance in model_instances:
            self.session.refresh(instance)

        logger.info(f"Stored {len(model_instances)} log aggregations")
        return model_instances

    def store_incident_aggregations(
        self,
        org_id: str,
        aggregations: List[IncidentAggregation],
        granularity: AggregationGranularity = AggregationGranularity.ONE_HOUR,
    ):
        """Store aggregated incidents in the appropriate table."""
        if not aggregations:
            logger.info("No incident aggregations to store")
            return

        # Currently only 1h granularity is supported for incident aggregations
        if granularity != AggregationGranularity.ONE_HOUR:
            logger.error(
                f"Incident aggregations only support 1-hour granularity, got: {granularity}"
            )
            return

        target_model = IncidentAggregation1h

        # Convert IncidentAggregation objects to model instances
        model_instances = []
        for agg in aggregations:
            instance_data = {
                "timestamp": agg.timestamp,
                "service_name": agg.service_name,
                "total_incidents": agg.total_incidents,
                "critical_incidents": getattr(agg, "critical_incidents", 0),
                "high_incidents": getattr(agg, "high_incidents", 0),
                "medium_incidents": getattr(agg, "medium_incidents", 0),
                "low_incidents": getattr(agg, "low_incidents", 0),
                "avg_resolution_time": getattr(agg, "avg_resolution_time", None),
                "auto_resolved_count": getattr(agg, "auto_resolved_count", 0),
                "organization_id": org_id,
                "created_at": now(),
            }

            model_instances.append(target_model(**instance_data))

        # Insert all at once
        self.session.add_all(model_instances)
        self.session.commit()

        # Refresh all instances
        for instance in model_instances:
            self.session.refresh(instance)

        logger.info(f"Stored {len(model_instances)} incident aggregations")
        return model_instances

    def cleanup_old_aggregations(self, retention_days: int = 90):
        """
        Clean up old aggregation data to manage storage.
        """

        cutoff_date = datetime.now() - timedelta(days=retention_days)

        tables = [
            MetricAggregation1m,
            MetricAggregation1h,
            LogAggregation1m,
            IncidentAggregation1h,
        ]

        for table in tables:
            try:
                statement = delete(
                    table,
                ).where(
                    table.timestamp < cutoff_date,
                )
                result = self.session.exec(statement).rowcount
                self.session.commit()

                logger.info(f"Cleaned up {result} old records from {table}")
            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to cleanup {table}: {e}")
