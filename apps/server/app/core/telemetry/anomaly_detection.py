import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import statistics
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.core.types.aggregate_telemetry import (
    MetricAggregationData,
    LogAggregationData,
)
from hydra_types.telemetry import TelemetryBatch
from app.utils.logging import create_logger

logger = create_logger(__name__)


class AnomalyType(Enum):
    HIGH_ERROR_RATE = "high_error_rate"
    INCREASED_LATENCY = "increased_latency"
    RESOURCE_SPIKE = "resource_spike"
    VERSION_REGRESSION = "version_regression"
    STATISTICAL_OUTLIER = "statistical_outlier"


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyThresholds:
    """Configuration for anomaly detection thresholds"""

    error_rate_absolute: float = 60.0  # Absolute error rate threshold (%)
    error_rate_increase: float = 20.0  # Percentage increase threshold
    latency_increase: float = 50.0  # Percentage increase threshold
    resource_increase: float = 40.0  # Percentage increase threshold
    isolation_forest_contamination: float = 0.1
    historical_window_hours: int = 24


class AnomalyDetection(BaseModel):
    """Represents a detected anomaly"""

    anomaly_type: AnomalyType
    severity: SeverityLevel
    service_name: str
    service_version: str
    timestamp: datetime
    current_value: float
    baseline_value: Optional[float] = None
    percentage_change: Optional[float] = None
    description: str = ""
    metadata: Dict[str, Any] = {}


class MetricAnalyzer:
    """Helper class for analyzing specific metrics"""

    def __init__(self):
        self.resource_metrics = [
            "cpu.usage",
            "memory.usage",
            "disk.io",
            "network.io",
            "http.request.duration_ms",
            "database.query.duration_ms",
        ]
        self.latency_metrics = [
            "http.request.duration_ms",
            "response.time",
            "database.query.duration_ms",
            "api.latency",
            "request.duration",
        ]

    def is_resource_metric(self, metric_name: str) -> bool:
        """Check if a metric represents resource consumption"""
        return any(
            resource in metric_name.lower() for resource in self.resource_metrics
        )

    def is_latency_metric(self, metric_name: str) -> bool:
        """Check if a metric represents latency"""
        return any(latency in metric_name.lower() for latency in self.latency_metrics)

    def calculate_error_rate(self, batch: "TelemetryBatch") -> float:
        """Calculate error rate from telemetry batch"""
        if not batch.logs:
            return 0.0

        total_logs = len(batch.logs)
        error_logs = sum(1 for log in batch.logs if log.level in ["ERROR", "FATAL"])

        return (error_logs / total_logs) * 100.0 if total_logs > 0 else 0.0

    def extract_metrics_data(self, batch: "TelemetryBatch") -> Dict[str, List[float]]:
        """Extract metric values grouped by metric name"""
        metrics_data = {}

        for metric in batch.metrics:
            if metric.metric_name not in metrics_data:
                metrics_data[metric.metric_name] = []
            metrics_data[metric.metric_name].append(metric.value)

        return metrics_data


def emit_distress():
    """Mock method to emit distress signals when anomalies are detected"""
    logger.critical("🚨 DISTRESS SIGNAL EMITTED - Critical anomaly detected!")
    # In real implementation, this would trigger alerts, notifications, etc.
    pass


class AnomalyDetectionEngine:
    """Main anomaly detection engine"""

    def __init__(self, thresholds: AnomalyThresholds):
        self.thresholds = thresholds or AnomalyThresholds()
        self.metric_analyzer = MetricAnalyzer()
        self.isolation_forest = IsolationForest(
            contamination=self.thresholds.isolation_forest_contamination,  # type: ignore
            random_state=42,
        )
        self.scaler = StandardScaler()
        self.is_model_fitted = False

    def detect_anomalies(
        self,
        live_batch: "TelemetryBatch",
        historical_metrics: List["MetricAggregationData"],
        historical_logs: List["LogAggregationData"],
    ) -> List[AnomalyDetection]:
        """Main method to detect anomalies in live telemetry data"""

        anomalies = []

        try:
            # 1. Check absolute error rate threshold
            error_rate_anomalies = self._check_absolute_error_rate(live_batch)
            anomalies.extend(error_rate_anomalies)

            # 2. Analyze metrics using Isolation Forest
            statistical_anomalies = self._detect_statistical_anomalies(live_batch)
            anomalies.extend(statistical_anomalies)

            # 3. Compare with historical data
            historical_anomalies = self._compare_with_historical_data(
                live_batch, historical_metrics, historical_logs
            )
            anomalies.extend(historical_anomalies)

            # 4. Version comparison analysis
            version_anomalies = self._detect_version_regressions(
                live_batch, historical_metrics, historical_logs
            )
            anomalies.extend(version_anomalies)

            # Log summary
            if anomalies:
                logger.warning(
                    f"Detected {len(anomalies)} anomalies in telemetry batch"
                )

                # Emit distress for critical anomalies
                critical_anomalies = [
                    a for a in anomalies if a.severity == SeverityLevel.CRITICAL
                ]
                if critical_anomalies:
                    emit_distress()

        except Exception as e:
            logger.error(f"Error during anomaly detection: {e}")

        return anomalies

    def _check_absolute_error_rate(
        self, batch: "TelemetryBatch"
    ) -> List[AnomalyDetection]:
        """Check if error rate exceeds absolute threshold (60%)"""
        anomalies = []

        error_rate = self.metric_analyzer.calculate_error_rate(batch)

        if error_rate > self.thresholds.error_rate_absolute:
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.HIGH_ERROR_RATE,
                severity=SeverityLevel.CRITICAL,
                service_name=batch.source_system,
                service_version="current",  # Could be extracted from batch metadata
                timestamp=batch.export_timestamp,
                current_value=error_rate,
                description=f"Error rate {error_rate:.2f}% exceeds critical threshold of {self.thresholds.error_rate_absolute}%",
                metadata={"threshold": self.thresholds.error_rate_absolute},
            )
            anomalies.append(anomaly)

            # Emit distress for high error rate
            emit_distress()

        return anomalies

    def _detect_statistical_anomalies(
        self, batch: "TelemetryBatch"
    ) -> List[AnomalyDetection]:
        """Use Isolation Forest to detect statistical anomalies"""
        anomalies = []

        if not batch.metrics:
            return anomalies

        try:
            # Prepare data for Isolation Forest
            metrics_data = self.metric_analyzer.extract_metrics_data(batch)

            for metric_name, values in metrics_data.items():
                if len(values) < 5:  # Need minimum samples for meaningful analysis
                    continue

                # Reshape data for sklearn
                X = np.array(values).reshape(-1, 1)

                # Fit and predict
                outliers = self.isolation_forest.fit_predict(X)
                anomaly_scores = self.isolation_forest.decision_function(X)

                # Find anomalous points
                for i, (is_outlier, score) in enumerate(zip(outliers, anomaly_scores)):
                    if is_outlier == -1:  # Anomaly detected
                        severity = (
                            SeverityLevel.HIGH if score < -0.5 else SeverityLevel.MEDIUM
                        )

                        anomaly = AnomalyDetection(
                            anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                            severity=severity,
                            service_name=batch.source_system,
                            service_version="current",
                            timestamp=batch.export_timestamp,
                            current_value=values[i],
                            description=f"Statistical outlier detected in {metric_name} (score: {score:.3f})",
                            metadata={
                                "metric_name": metric_name,
                                "anomaly_score": score,
                                "value_index": i,
                            },
                        )
                        anomalies.append(anomaly)

        except Exception as e:
            logger.error(f"Error in statistical anomaly detection: {e}")

        return anomalies

    def _compare_with_historical_data(
        self,
        batch: "TelemetryBatch",
        historical_metrics: List["MetricAggregationData"],
        historical_logs: List["LogAggregationData"],
    ) -> List[AnomalyDetection]:
        """Compare current batch with historical data to detect significant changes"""
        anomalies = []

        # Calculate historical baselines
        historical_baselines = self._calculate_historical_baselines(
            historical_metrics, historical_logs
        )

        # Compare metrics
        current_metrics = self.metric_analyzer.extract_metrics_data(batch)

        for metric_name, current_values in current_metrics.items():
            if metric_name not in historical_baselines:
                continue

            current_avg = statistics.mean(current_values)
            historical_avg = historical_baselines[metric_name]

            if historical_avg == 0:
                continue

            percentage_change = ((current_avg - historical_avg) / historical_avg) * 100

            # Check different types of metrics
            anomaly_detected = False
            anomaly_type = None

            severity = SeverityLevel.MEDIUM

            if self.metric_analyzer.is_latency_metric(metric_name):
                if percentage_change > self.thresholds.latency_increase:
                    anomaly_detected = True
                    anomaly_type = AnomalyType.INCREASED_LATENCY
                    severity = (
                        SeverityLevel.HIGH
                        if percentage_change > 100
                        else SeverityLevel.MEDIUM
                    )

            elif self.metric_analyzer.is_resource_metric(metric_name):
                if percentage_change > self.thresholds.resource_increase:
                    anomaly_detected = True
                    anomaly_type = AnomalyType.RESOURCE_SPIKE
                    severity = (
                        SeverityLevel.HIGH
                        if percentage_change > 80
                        else SeverityLevel.MEDIUM
                    )

            if anomaly_detected and anomaly_type:
                anomaly = AnomalyDetection(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    service_name=batch.source_system,
                    service_version="current",
                    timestamp=batch.export_timestamp,
                    current_value=current_avg,
                    baseline_value=historical_avg,
                    percentage_change=percentage_change,
                    description=f"{metric_name} increased by {percentage_change:.1f}% compared to historical baseline",
                    metadata={"metric_name": metric_name},
                )
                anomalies.append(anomaly)

                # Emit distress for significant increases
                if percentage_change > 100:  # 100% increase
                    emit_distress()

        # Compare error rates
        current_error_rate = self.metric_analyzer.calculate_error_rate(batch)
        historical_error_rate = self._calculate_historical_error_rate(historical_logs)

        if historical_error_rate > 0:
            error_rate_change = (
                (current_error_rate - historical_error_rate) / historical_error_rate
            ) * 100

            if error_rate_change > self.thresholds.error_rate_increase:
                anomaly = AnomalyDetection(
                    anomaly_type=AnomalyType.HIGH_ERROR_RATE,
                    severity=SeverityLevel.HIGH,
                    service_name=batch.source_system,
                    service_version="current",
                    timestamp=batch.export_timestamp,
                    current_value=current_error_rate,
                    baseline_value=historical_error_rate,
                    percentage_change=error_rate_change,
                    description=f"Error rate increased by {error_rate_change:.1f}% from baseline {historical_error_rate:.2f}%",
                    metadata={"baseline_error_rate": historical_error_rate},
                )
                anomalies.append(anomaly)

                if error_rate_change > 50:  # 50% increase in error rate
                    emit_distress()

        return anomalies

    def _detect_version_regressions(
        self,
        batch: "TelemetryBatch",
        historical_metrics: List["MetricAggregationData"],
        historical_logs: List["LogAggregationData"],
    ) -> List[AnomalyDetection]:
        """Compare current version performance with previous versions"""
        anomalies = []

        if not batch.metrics:
            return anomalies

        # Get current version from first metric (assuming consistent versioning)
        current_version = (
            batch.metrics[0].service_version if batch.metrics else "unknown"
        )

        # Group historical data by version
        version_baselines = self._calculate_version_baselines(
            historical_metrics, historical_logs
        )

        if len(version_baselines) < 2:  # Need at least 2 versions to compare
            return anomalies

        # Find previous version for comparison
        versions = sorted(version_baselines.keys(), reverse=True)
        previous_version = None

        for version in versions:
            if version != current_version:
                previous_version = version
                break

        if not previous_version:
            return anomalies

        previous_baseline = version_baselines[previous_version]
        current_metrics = self.metric_analyzer.extract_metrics_data(batch)

        # Compare metrics between versions
        for metric_name, current_values in current_metrics.items():
            if metric_name not in previous_baseline:
                continue

            current_avg = statistics.mean(current_values)
            previous_avg = previous_baseline[metric_name]

            if previous_avg == 0:
                continue

            percentage_change = ((current_avg - previous_avg) / previous_avg) * 100

            # Detect regressions (performance getting worse)
            if (
                self.metric_analyzer.is_latency_metric(metric_name)
                and percentage_change > 25
            ):
                anomaly = AnomalyDetection(
                    anomaly_type=AnomalyType.VERSION_REGRESSION,
                    severity=SeverityLevel.HIGH,
                    service_name=batch.source_system,
                    service_version=current_version,
                    timestamp=batch.export_timestamp,
                    current_value=current_avg,
                    baseline_value=previous_avg,
                    percentage_change=percentage_change,
                    description=f"Version regression: {metric_name} degraded by {percentage_change:.1f}% in {current_version} vs {previous_version}",
                    metadata={
                        "current_version": current_version,
                        "previous_version": previous_version,
                        "metric_name": metric_name,
                    },
                )
                anomalies.append(anomaly)

                if percentage_change > 75:  # Significant regression
                    emit_distress()

        return anomalies

    def _calculate_historical_baselines(
        self,
        historical_metrics: List["MetricAggregationData"],
        historical_logs: List["LogAggregationData"],
    ) -> Dict[str, float]:
        """Calculate baseline values from historical data"""
        baselines = {}

        # Group metrics by name
        metric_groups = {}
        for metric in historical_metrics:
            if metric.metric_name not in metric_groups:
                metric_groups[metric.metric_name] = []
            metric_groups[metric.metric_name].append(metric.avg_value)

        # Calculate baselines (using median for robustness)
        for metric_name, values in metric_groups.items():
            if values:
                baselines[metric_name] = statistics.median(values)

        return baselines

    def _calculate_historical_error_rate(
        self, historical_logs: List["LogAggregationData"]
    ) -> float:
        """Calculate historical error rate baseline"""
        if not historical_logs:
            return 0.0

        total_logs = sum(log.total_logs for log in historical_logs)
        total_errors = sum(log.error_count for log in historical_logs)

        return (total_errors / total_logs) * 100.0 if total_logs > 0 else 0.0

    def _calculate_version_baselines(
        self,
        historical_metrics: List["MetricAggregationData"],
        historical_logs: List["LogAggregationData"],
    ) -> Dict[str, Dict[str, float]]:
        """Calculate baselines grouped by service version"""
        version_baselines = {}

        # Group by version
        version_metrics = {}
        for metric in historical_metrics:
            version = metric.service_version
            if version not in version_metrics:
                version_metrics[version] = {}
            if metric.metric_name not in version_metrics[version]:
                version_metrics[version][metric.metric_name] = []
            version_metrics[version][metric.metric_name].append(metric.avg_value)

        # Calculate baselines for each version
        for version, metrics in version_metrics.items():
            version_baselines[version] = {}
            for metric_name, values in metrics.items():
                if values:
                    version_baselines[version][metric_name] = statistics.median(values)

        return version_baselines


# Example usage
def example_usage():
    """Example of how to use the anomaly detection engine"""

    # Initialize the engine
    thresholds = AnomalyThresholds(
        error_rate_absolute=60.0,
        error_rate_increase=25.0,
        latency_increase=50.0,
        resource_increase=40.0,
    )

    engine = AnomalyDetectionEngine(thresholds)

    # Mock data (in real usage, this would come from your data sources)
    # live_batch = TelemetryBatch(...)
    # historical_metrics = [...]
    # historical_logs = [...]

    # Detect anomalies
    # anomalies = engine.detect_anomalies(live_batch, historical_metrics, historical_logs)

    # Process results
    # for anomaly in anomalies:
    #     logger.info(f"Anomaly detected: {anomaly.description}")

    pass


if __name__ == "__main__":
    example_usage()
