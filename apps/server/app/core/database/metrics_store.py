from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, desc

from app.models.sql_model import Metric
from hydra_types.telemetry import Metric as MetricType


class MetricStore:
    """Class to handle metric operations using Metric model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_metric(
        self,
        service_name: str,
        service_version: str,
        metric_name: str,
        value: float,
        organization_id: str,
        labels: Optional[Dict[str, Any]] = None,
        unit: Optional[str] = None,
        anomaly_score: float = 0.0,
        timestamp: Optional[datetime] = None,
    ) -> Metric:
        """
        Create a new metric entry

        Args:
            service_name: Name of the service
            metric_name: Name of the metric
            value: Metric value
            organization_id: Organization identifier
            labels: Optional labels dictionary
            unit: Optional unit string
            anomaly_score: Anomaly score (default 0.0)
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Created Metric object
        """
        metric = Metric(
            service_name=service_name,
            service_version=service_version,
            metric_name=metric_name,
            value=value,
            organization_id=organization_id,
            labels=labels,
            unit=unit,
            anomaly_score=anomaly_score,
            timestamp=timestamp or datetime.now(),
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def bulk_create_metrics(
        self, metrics_data: List[MetricType], organization_id: str
    ) -> List[Metric]:
        """
        Bulk create multiple metrics

        Args:
            metrics_data: List of metric dictionaries

        Returns:
            List of created Metric objects
        """
        metrics = [
            Metric(
                service_name=data.service_name,
                metric_name=data.metric_name,
                service_version=data.service_version,
                value=data.value,
                labels=data.labels,
                unit=data.unit,
                timestamp=data.timestamp,
                organization_id=organization_id,
            )
            for data in metrics_data
        ]
        self.db.add_all(metrics)
        self.db.commit()
        for metric in metrics:
            self.db.refresh(metric)
        return metrics

    def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get metric by ID"""
        return self.db.get(Metric, metric_id)

    def get_metrics_by_service(
        self,
        service_name: str,
        organization_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Metric]:
        """
        Get metrics for a specific service within time range

        Args:
            service_name: Service name to filter by
            organization_id: Organization identifier
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of records to return

        Returns:
            List of Metric objects
        """
        statement = select(Metric).where(
            Metric.service_name == service_name,
            Metric.organization_id == organization_id,
        )

        if start_time:
            statement = statement.where(Metric.timestamp >= start_time)
        if end_time:
            statement = statement.where(Metric.timestamp <= end_time)

        statement = statement.order_by(desc(Metric.timestamp)).limit(limit)
        return list(self.db.exec(statement).all())

    def get_anomalous_metrics(
        self,
        organization_id: str,
        anomaly_threshold: float = 0.8,
        limit: int = 100,
    ) -> List[Metric]:
        """
        Get metrics with high anomaly scores

        Args:
            organization_id: Organization identifier
            anomaly_threshold: Minimum anomaly score
            limit: Maximum number of records

        Returns:
            List of anomalous Metric objects
        """
        statement = (
            select(Metric)
            .where(
                Metric.organization_id == organization_id,
                Metric.anomaly_score >= anomaly_threshold,
            )
            .order_by(desc(Metric.anomaly_score), desc(Metric.timestamp))
            .limit(limit)
        )
        return list(self.db.exec(statement).all())

    def update_anomaly_score(self, metric_id: str, anomaly_score: float) -> bool:
        """
        Update anomaly score for a metric

        Args:
            metric_id: Metric ID
            anomaly_score: New anomaly score

        Returns:
            True if updated successfully
        """
        metric = self.db.get(Metric, metric_id)
        if metric:
            metric.anomaly_score = anomaly_score
            self.db.add(metric)
            self.db.commit()
            return True
        return False

    def delete_old_metrics(self, organization_id: str, older_than: datetime) -> int:
        """
        Delete metrics older than specified date

        Args:
            organization_id: Organization identifier
            older_than: Delete metrics older than this date

        Returns:
            Number of metrics deleted
        """
        statement = select(Metric).where(
            Metric.organization_id == organization_id,
            Metric.timestamp < older_than,
        )
        metrics = self.db.exec(statement).all()
        count = len(metrics)

        for metric in metrics:
            self.db.delete(metric)

        self.db.commit()
        return count
