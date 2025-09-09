from datetime import datetime
from typing import List
from sqlmodel import Session, text

from app.core.types.aggregate_telemetry import (
    AggregationGranularity,
    IncidentAggregation,
    LogAggregation,
    MetricAggregation,
)
from app.utils.logging import create_logger

logger = create_logger(__name__)


class AggregateTelemetry:
    def __init__(self, session: Session):
        self.session = session

    def _time_bucket_sql(self, granularity: AggregationGranularity) -> str:
        interval = {"1m": 60, "5m": 300, "1h": 3600, "1d": 86400}.get(granularity.value)

        if interval is None:
            return "timestamp"  # fallback if unknown

        return (
            f"FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(timestamp) / {interval}) * {interval})"
        )

    def aggregate_metrics(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_HOUR,
    ) -> List[MetricAggregation]:
        """
        Aggregate metrics data for the specified time range.
        Uses TiFlash for analytical processing.
        """

        sql = f"""
          SELECT
            service_name,
            metric_name,
            {self._time_bucket_sql(granularity)} as time_bucket,
            AVG(value)     AS avg_value,
            MIN(value)     AS min_value,
            MAX(value)     AS max_value,
            COUNT(*)       AS count_values,
            SUM(value)     AS sum_values,
            STDDEV(value)  AS stddev_value,
            APPROX_PERCENTILE(value, 50) AS p50_value,
            APPROX_PERCENTILE(value, 95) AS p95_value,
            APPROX_PERCENTILE(value, 99) AS p99_value
          FROM metrics
          WHERE
              timestamp >= :start_time
              AND timestamp < :end_time
              AND organization_id = :org_id
          GROUP BY
              service_name,
              metric_name,
              time_bucket
          ORDER BY
              service_name,
              metric_name,
              time_bucket
          LIMIT 500;
        """

        try:
            result = self.session.execute(
                text(sql),
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "org_id": org_id,
                },
            )
            aggregations = []
            for row in result:
                agg = MetricAggregation(
                    timestamp=row.time_bucket,
                    service_name=row.service_name,
                    metric_name=row.metric_name,
                    avg_value=float(row.avg_value),
                    min_value=float(row.min_value),
                    max_value=float(row.max_value),
                    count_values=int(row.count_values),
                    sum_values=float(row.sum_values),
                    p50_value=float(row.p50_value) if row.p50_value else 0.0,
                    p95_value=float(row.p95_value) if row.p95_value else 0.0,
                    p99_value=float(row.p99_value) if row.p99_value else 0.0,
                    stddev_value=float(row.stddev_value) if row.stddev_value else 0.0,
                )
                aggregations.append(agg)

            logger.info(
                f"Aggregated {len(aggregations)} metric records for {granularity.value}"
            )
            return aggregations

        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
            raise

    def aggregate_logs(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_MINUTE,
    ) -> List[LogAggregation]:
        """Aggregate log data for error rates and patterns."""

        sql = f"""
        SELECT
            {self._time_bucket_sql(granularity)} as timebucket,
            service_name,
            COUNT(*) as total_logs,
            COUNT(CASE WHEN level = 'ERROR' THEN 1 END) as error_count,
            COUNT(CASE WHEN level = 'WARN' THEN 1 END) as warn_count,
            COUNT(CASE WHEN level = 'INFO' THEN 1 END) as info_count,
            COUNT(CASE WHEN level = 'DEBUG' THEN 1 END) as debug_count,
            (COUNT(CASE WHEN level = 'ERROR' THEN 1 END) * 100.0 / COUNT(*)) as error_rate,
            COUNT(DISTINCT trace_id) as unique_traces
        FROM logs
        WHERE timestamp >= :start_time
            AND timestamp < :end_time
            AND organization_id = :org_id
        GROUP BY
            timebucket,
            service_name
        ORDER BY timebucket, service_name
        """

        try:
            result = self.session.execute(
                text(sql),
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "org_id": org_id,
                },
            )

            aggregations = []
            for row in result:
                agg = LogAggregation(
                    timestamp=row.timebucket,
                    service_name=row.service_name,
                    total_logs=int(row.total_logs),
                    error_count=int(row.error_count),
                    warn_count=int(row.warn_count),
                    info_count=int(row.info_count),
                    debug_count=int(row.debug_count),
                    error_rate=float(row.error_rate),
                    unique_traces=int(row.unique_traces) if row.unique_traces else 0,
                )
                aggregations.append(agg)

            logger.info(
                f"Aggregated {len(aggregations)} log records for {granularity.value}"
            )
            return aggregations

        except Exception as e:
            logger.error(f"Failed to aggregate logs: {e}")
            raise

    def aggregate_incidents(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: AggregationGranularity = AggregationGranularity.ONE_HOUR,
    ) -> List[IncidentAggregation]:
        """Aggregate incident data for MTTR and frequency analysis."""

        sql = f"""
        SELECT
            {self._time_bucket_sql(granularity)} as time_bucket,
            service_name,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_incidents,
            COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high_incidents,
            COUNT(CASE WHEN severity = 'MEDIUM' THEN 1 END) as medium_incidents,
            COUNT(CASE WHEN severity = 'LOW' THEN 1 END) as low_incidents,
            AVG(resolution_time_seconds) as avg_resolution_time,
            COUNT(CASE WHEN auto_resolved = true THEN 1 END) as auto_resolved_count
        FROM incidents
        WHERE timestamp >= :start_time
            AND timestamp < :end_time
            AND organization_id = :org_id
        GROUP BY
            time_bucket,
            service_name
        ORDER BY time_bucket, service_name
        """

        try:
            result = self.session.execute(
                text(sql),
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "org_id": org_id,
                },
            )

            aggregations = []
            for row in result:
                agg = IncidentAggregation(
                    timestamp=row.time_bucket,
                    service_name=row.service_name,
                    total_incidents=int(row.total_incidents),
                    critical_incidents=int(row.critical_incidents),
                    high_incidents=int(row.high_incidents),
                    medium_incidents=int(row.medium_incidents),
                    low_incidents=int(row.low_incidents),
                    avg_resolution_time=(
                        float(row.avg_resolution_time)
                        if row.avg_resolution_time
                        else 0.0
                    ),
                    auto_resolved_count=int(row.auto_resolved_count),
                )
                aggregations.append(agg)

            logger.info(f"Aggregated {len(aggregations)} incident records")
            return aggregations

        except Exception as e:
            logger.error(f"Failed to aggregate incidents: {e}")
            raise
