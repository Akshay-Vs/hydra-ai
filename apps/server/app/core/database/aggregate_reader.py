from typing import List, Optional
from datetime import datetime
from sqlmodel import col, select, func, desc


from app.core.types.aggregate_telemetry import (
    IncidentAggregationData,
    LogAggregationData,
    MetricAggregationData,
    ServiceIncidentTrend,
    ServiceMetricSummary,
    TopErrorService,
    AggregationGranularity,
)
from app.models.sql_model import (
    IncidentAggregation1h,
    LogAggregation1m,
    MetricAggregation1h,
    MetricAggregation1m,
)
from app.utils.logging import create_logger

logger = create_logger(__name__)


class AggregateReader:
    """
    Reader class for retrieving aggregated data from various aggregation tables.
    Provides methods for querying metrics, logs, and incidents aggregations.
    """

    def __init__(self, session):
        self.session = session

    def get_aggregated_metrics(
        self,
        organization_id: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
        limit: int = 1000,
    ) -> List[MetricAggregationData]:
        """Retrieve aggregated metrics for analysis and visualization."""

        # Determine the target model based on granularity
        if granularity == AggregationGranularity.ONE_MINUTE:
            target_model = MetricAggregation1m
        elif granularity == AggregationGranularity.ONE_HOUR:
            target_model = MetricAggregation1h
        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

        # Build the query
        statement = select(target_model).where(
            target_model.organization_id == organization_id,
            target_model.metric_name == metric_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )

        statement = statement.order_by(target_model.timestamp).limit(limit)  # type: ignore

        retult = list(self.session.exec(statement).all())
        return [
            MetricAggregationData(
                organization_id=row.organization_id,
                service_name=row.service_name,
                service_version=row.service_version,
                metric_name=row.metric_name,
                avg_value=row.avg_value,
                min_value=row.min_value,
                max_value=row.max_value,
                count_values=row.count_values,
                sum_values=row.sum_values,
                p50_value=row.p50_value,
                p95_value=row.p95_value,
                p99_value=row.p99_value,
                stddev_value=row.stddev_value,
                timestamp=row.timestamp,
                created_at=row.created_at,
            )
            for row in retult
        ]

    def get_aggregated_logs(
        self,
        organization_id: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
        min_error_rate: Optional[float] = None,
        limit: int = 1000,
    ) -> List[LogAggregationData]:
        """Retrieve aggregated logs for analysis and visualization."""

        # Currently only 1m granularity is supported for log aggregations
        if granularity != AggregationGranularity.ONE_MINUTE:
            raise ValueError(
                f"Log aggregations only support 1-minute granularity, got: {granularity}"
            )

        target_model = LogAggregation1m

        # Build the query
        statement = select(target_model).where(
            target_model.organization_id == organization_id,
            target_model.service_name == service_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )
        if min_error_rate is not None:
            statement = statement.where(target_model.error_rate >= min_error_rate)

        statement = statement.order_by(target_model.timestamp).limit(limit)  # type: ignore

        result = list(self.session.exec(statement).all())
        return [
            LogAggregationData(
                organization_id=row.organization_id,
                service_name=row.service_name,
                total_logs=row.total_logs,
                error_count=row.error_count,
                warn_count=row.warn_count,
                info_count=row.info_count,
                debug_count=row.debug_count,
                error_rate=row.error_rate,
                unique_traces=row.unique_traces,
                timestamp=row.timestamp,
                created_at=row.created_at,
            )
            for row in result
        ]

    def get_aggregated_incidents(
        self,
        organization_id: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_HOUR,
        min_critical_incidents: Optional[int] = None,
        max_resolution_time: Optional[float] = None,
        limit: int = 1000,
    ) -> List[IncidentAggregationData]:
        """Retrieve aggregated incidents for analysis and visualization."""

        # Currently only 1h granularity is supported for incident aggregations
        if granularity != AggregationGranularity.ONE_HOUR:
            raise ValueError(
                f"Incident aggregations only support 1-hour granularity, got: {granularity}"
            )

        target_model = IncidentAggregation1h

        # Build the query
        statement = select(target_model).where(
            target_model.organization_id == organization_id,
            target_model.service_name == service_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )

        if min_critical_incidents is not None:
            statement = statement.where(
                target_model.critical_incidents >= min_critical_incidents
            )

        if max_resolution_time and target_model.avg_resolution_time:
            statement = statement.where(
                target_model.avg_resolution_time <= max_resolution_time
            )

        statement = statement.order_by(target_model.timestamp).limit(limit)  # type: ignore

        retults = list(self.session.exec(statement).all())
        return [IncidentAggregationData(**row._mapping) for row in retults]

    def get_service_metrics_summary(
        self,
        organization_id: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ) -> List[ServiceMetricSummary]:
        """Get summary of all metrics for a service within time range."""

        if granularity == AggregationGranularity.ONE_MINUTE:
            target_model = MetricAggregation1m
        elif granularity == AggregationGranularity.ONE_HOUR:
            target_model = MetricAggregation1h
        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

        statement = select(
            target_model.metric_name,
            func.avg(target_model.avg_value).label("overall_avg"),
            func.min(target_model.min_value).label("overall_min"),
            func.max(target_model.max_value).label("overall_max"),
        ).where(
            target_model.service_name == service_name,
            target_model.organization_id == organization_id,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )
        statement = statement.group_by(target_model.metric_name)

        results = list(self.session.exec(statement).all())

        return [
            ServiceMetricSummary(
                metric_name=metric_name,
                overall_avg=overall_avg,
                overall_min=overall_min,
                overall_max=overall_max,
                data_points=len(metric_name),
            )
            for metric_name, overall_avg, overall_min, overall_max in results
        ]

    def get_top_error_services(
        self,
        organization_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 10,
    ) -> List[TopErrorService]:
        """Get services with highest error rates in the given time period."""

        statement = select(
            LogAggregation1m.service_name,
            func.avg(LogAggregation1m.error_rate).label("avg_error_rate"),
            func.sum(LogAggregation1m.error_count).label("total_errors"),
            func.sum(LogAggregation1m.total_logs).label("total_logs"),
        ).where(
            LogAggregation1m.organization_id == organization_id,
            LogAggregation1m.timestamp >= start_time,
            LogAggregation1m.timestamp <= end_time,
        )

        statement = (
            statement.group_by(LogAggregation1m.service_name)
            .order_by(desc("avg_error_rate"))
            .limit(limit)
        )

        results = list(self.session.exec(statement).all())
        return [TopErrorService(**row._mapping) for row in results]

    def get_service_incident_trends(
        self,
        organization_id: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[ServiceIncidentTrend]:
        """Get incident trends for a specific service over time."""

        statement = select(IncidentAggregation1h).where(
            IncidentAggregation1h.service_name == service_name,
            IncidentAggregation1h.organization_id == organization_id,
            IncidentAggregation1h.timestamp >= start_time,
            IncidentAggregation1h.timestamp <= end_time,
        )

        statement = statement.order_by(IncidentAggregation1h.timestamp)  # type: ignore

        results = list(self.session.exec(statement).all())
        return [
            ServiceIncidentTrend(
                timestamp=entry.timestamp,
                total_incidents=entry.total_incidents,
                critical_incidents=entry.critical_incidents,
                high_incidents=entry.high_incidents,
                avg_resolution_time=entry.avg_resolution_time,
                auto_resolved_count=entry.auto_resolved_count,
            )
            for entry in results
        ]

    def get_metrics_by_service_list(
        self,
        organization_id: str,
        service_names: List[str],
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
        limit: int = 1000,
    ) -> List[MetricAggregationData]:
        """Get metrics for multiple services for comparison."""

        if granularity == AggregationGranularity.ONE_MINUTE:
            target_model = MetricAggregation1m
        elif granularity == AggregationGranularity.ONE_HOUR:
            target_model = MetricAggregation1h
        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

        statement = select(target_model).where(
            col(target_model.service_name).in_(service_names),
            target_model.organization_id == organization_id,
            target_model.metric_name == metric_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )
        statement = statement.order_by(
            target_model.service_name,
            target_model.timestamp,  # type: ignore
        ).limit(limit)

        result = list(self.session.exec(statement).all())
        return [MetricAggregationData(**row._mapping) for row in result]

    def get_anomaly_candidates(
        self,
        organization_id: str,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        metric_name: str | None = None,
        threshold_multiplier: float = 3.0,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ) -> List[MetricAggregationData]:
        """
        Get potential anomaly data points where values deviate significantly from the average.
        Uses simple statistical threshold (mean ± threshold_multiplier * stddev).
        """

        if granularity == AggregationGranularity.ONE_MINUTE:
            target_model = MetricAggregation1m
        elif granularity == AggregationGranularity.ONE_HOUR:
            target_model = MetricAggregation1h
        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

        # First, get the statistical baseline
        baseline_statement = select(
            func.avg(target_model.avg_value).label("mean_value"),
            func.stddev(target_model.avg_value).label("stddev_value"),
        ).where(
            target_model.service_name == service_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
        )
        if metric_name:
            baseline_statement = baseline_statement.where(
                target_model.metric_name == metric_name
            )
        if organization_id:
            baseline_statement = baseline_statement.where(
                target_model.organization_id == organization_id
            )

        baseline_result = self.session.exec(baseline_statement).first()

        if not baseline_result or baseline_result.mean_value is None:
            return []

        mean_val = baseline_result.mean_value
        stddev_val = baseline_result.stddev_value or 0

        lower_threshold = mean_val - (threshold_multiplier * stddev_val)
        upper_threshold = mean_val + (threshold_multiplier * stddev_val)

        # Get data points outside the threshold
        anomaly_statement = select(target_model).where(
            target_model.service_name == service_name,
            target_model.metric_name == metric_name,
            target_model.timestamp >= start_time,
            target_model.timestamp <= end_time,
            (target_model.avg_value < lower_threshold)
            | (target_model.avg_value > upper_threshold),
        )

        if organization_id:
            anomaly_statement = anomaly_statement.where(
                target_model.organization_id == organization_id
            )

        anomaly_statement = anomaly_statement.order_by(
            target_model.timestamp  # type: ignore
        )

        results = list(self.session.exec(anomaly_statement).all())
        return [MetricAggregationData(**row._mapping) for row in results]
