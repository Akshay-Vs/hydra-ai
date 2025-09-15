from typing import Dict, List
from hydra_types.telemetry import TelemetryBatch
from app.utils.logging import create_logger

logger = create_logger(__name__)


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
