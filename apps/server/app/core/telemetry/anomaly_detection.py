import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.core.types.aggregate_telemetry import (
    MetricAggregationData,
    LogAggregationData,
    IncidentAggregationData,
)
from hydra_types.telemetry import TelemetryBatch
from app.utils.logging import create_logger

logger = create_logger(__name__)


class TelemetryAnomalyDetector:
    """
    Enhanced Isolation Forest for detecting usage spikes and critical errors in telemetry data.
    Uses historical data from AggregateReader and rule-based checks for reliable detection.
    """

    def __init__(self, n_trees=20, sample_size=256, contamination=0.1):
        self.n_trees = n_trees
        self.sample_size = sample_size
        self.contamination = contamination
        self.trees = []
        self.threshold = 0
        self.is_trained = False
        self.feature_names = []
        self.historic_stats = {}

    def fit(
        self,
        historic_metrics: Optional[List[MetricAggregationData]] = None,
        historic_logs: Optional[List[LogAggregationData]] = None,
        historic_incidents: Optional[List[IncidentAggregationData]] = None,
    ):
        logger.info("Training anomaly detector...")
        all_features = []
        if historic_metrics:
            all_features.extend(self._extract_features(historic_metrics, "metrics"))
            self._compute_historic_stats(historic_metrics, "metrics")
        if historic_logs:
            all_features.extend(self._extract_features(historic_logs, "logs"))
            self._compute_historic_stats(historic_logs, "logs")
        if historic_incidents:
            all_features.extend(self._extract_features(historic_incidents, "incidents"))
            self._compute_historic_stats(historic_incidents, "incidents")

        if not all_features:
            logger.warning(
                "Cannot train anomaly detector, No historic data is available"
            )
            return

        self.feature_names = list(all_features[0].keys())
        data_matrix = self._features_to_matrix(all_features)

        self._build_forest(data_matrix)
        scores = [self._get_anomaly_score(point) for point in data_matrix]
        self.threshold = np.percentile(scores, (1 - self.contamination) * 100)
        self.is_trained = True
        logger.info(f"Training complete. Threshold: {self.threshold:.3f}")

    def _compute_historic_stats(self, data_list, data_type: str):
        features_list = self._extract_features(data_list, data_type)
        stats = {}
        for item in data_list:
            service = item.service_name
            if service not in stats:
                stats[service] = {}
            if data_type == "metrics" and item.metric_name == "request_count":
                stats[service]["request_rate"] = [
                    f["request_rate"]
                    for f in features_list
                    if f.get("service_name") == service
                ]
            elif data_type == "logs":
                stats[service]["error_rate"] = [
                    f["error_rate"]
                    for f in features_list
                    if f.get("service_name") == service
                ]
        for service in stats:
            self.historic_stats[(data_type, service)] = {
                "request_rate_mean": np.mean(stats[service].get("request_rate", [0]))
                if stats[service].get("request_rate")
                else 0,
                "request_rate_std": np.std(stats[service].get("request_rate", [0]))
                if stats[service].get("request_rate")
                else 0,
                "error_rate_mean": np.mean(stats[service].get("error_rate", [0]))
                if stats[service].get("error_rate")
                else 0,
                "error_rate_std": np.std(stats[service].get("error_rate", [0]))
                if stats[service].get("error_rate")
                else 0,
            }

    def predict_batch(
        self, live_telemetry_batch: TelemetryBatch
    ) -> List[Dict[str, Any]]:
        if not self.is_trained:
            logger.warning("Skipping anomaly detection, Model must be trained first!")
            return []
        if not live_telemetry_batch:
            logger.warning("Skipping anomaly detection, Telemetry batch is required")
            return []

        logger.info("Analyzing telemetry batch for anomalies...")
        results = []

        for data_type, raw_data in [
            ("metrics", live_telemetry_batch.metrics),
            ("logs", live_telemetry_batch.logs),
            ("traces", live_telemetry_batch.traces),
            ("incidents", live_telemetry_batch.incidents),
        ]:
            if raw_data:
                aggregated_data = self._aggregate_raw_data(raw_data, data_type)
                type_results = self._detect_anomalies(aggregated_data, data_type)
                results.extend(type_results)

        logger.info(
            f"Found {sum(1 for r in results if r['is_anomaly'] or r.get('is_usage_spike') or r.get('is_critical_error'))} issues in {len(results)} data points"
        )
        return results

    def _aggregate_raw_data(self, raw_data, data_type: str) -> List[Dict[str, Any]]:
        if data_type == "metrics":
            return self._aggregate_metrics(raw_data)
        elif data_type == "logs":
            return self._aggregate_logs(raw_data)
        elif data_type == "traces":
            return self._aggregate_traces(raw_data)
        elif data_type == "incidents":
            return self._aggregate_incidents(raw_data)
        return []

    def _aggregate_traces(self, traces) -> List[Dict[str, Any]]:
        groups = {}
        for trace in traces:
            service = trace.service_name
            if service not in groups:
                groups[service] = []
            groups[service].append(trace)

        aggregated = []
        for service_name, trace_list in groups.items():
            http_traces = []
            status_codes = []
            for trace in trace_list:
                if (
                    hasattr(trace, "attributes")
                    and trace.attributes
                    and "http.status_code" in trace.attributes
                ):
                    try:
                        status_code = int(
                            trace.attributes["http.status_code"]
                        )  # Ensure numerical
                        http_traces.append(trace)
                        status_codes.append(status_code)
                    except (ValueError, TypeError):
                        continue  # Skip invalid status codes

            if http_traces:
                status_2xx = sum(1 for code in status_codes if 200 <= code < 300)
                status_5xx = sum(1 for code in status_codes if 500 <= code < 600)
                status_500 = sum(1 for code in status_codes if code == 500)
                total_http_requests = len(status_codes)

                start_times = [trace.start_time for trace in http_traces]
                time_window_ms = (
                    max(start_times) - min(start_times)
                    if start_times
                    else timedelta(milliseconds=1)
                )
                time_window_min = max(time_window_ms.total_seconds() / 60, 0.0167)
                request_rate = total_http_requests / time_window_min

                durations = [
                    float(trace.duration_ms)
                    for trace in http_traces
                    if hasattr(trace, "duration_ms") and trace.duration_ms is not None
                ]
                avg_duration = np.mean(durations) if durations else 0
                max_duration = np.max(durations) if durations else 0

                aggregated.append(
                    {
                        "timestamp": max(trace.start_time for trace in http_traces),
                        "service_name": service_name,
                        "total_http_requests": total_http_requests,
                        "request_rate": request_rate,
                        "status_2xx_count": status_2xx,
                        "status_5xx_count": status_5xx,
                        "status_500_count": status_500,
                        "error_rate": status_5xx / total_http_requests
                        if total_http_requests > 0
                        else 0,
                        "avg_response_time": avg_duration,
                        "max_response_time": max_duration,
                    }
                )

        return aggregated

    def _extract_features(self, data_list, data_type: str) -> List[Dict[str, float]]:
        features_list = []
        for item in data_list:
            item_dict = item.model_dump() if hasattr(item, "model_dump") else item
            features = {}

            if (
                data_type == "metrics"
                and item_dict.get("metric_name") == "request_count"
            ):
                features.update(
                    {
                        "request_rate": float(item_dict.get("count_values", 1)) / 60.0,
                        "avg_value": float(item_dict.get("avg_value", 0)),
                        "max_value": float(item_dict.get("max_value", 0)),
                    }
                )
            elif data_type == "logs":
                total_logs = max(int(item_dict.get("total_logs", 1)), 1)
                features.update(
                    {
                        "error_rate": float(item_dict.get("error_rate", 0)),
                        "total_logs": float(total_logs),
                        "error_count": float(item_dict.get("error_count", 0)),
                    }
                )
            elif data_type == "traces":
                total_requests = max(int(item_dict.get("total_http_requests", 1)), 1)
                features.update(
                    {
                        "request_rate": float(item_dict.get("request_rate", 0)),
                        "error_rate": float(item_dict.get("error_rate", 0)),
                        "status_5xx_count": float(item_dict.get("status_5xx_count", 0)),
                        "avg_response_time": float(
                            item_dict.get("avg_response_time", 0)
                        ),
                    }
                )
            elif data_type == "incidents":
                features.update(
                    {
                        "total_incidents": float(item_dict.get("total_incidents", 1)),
                        "critical_incidents": float(
                            item_dict.get("critical_incidents", 0)
                        ),
                    }
                )

            timestamp = item_dict.get("timestamp", datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            elif isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp / 1000)
            features.update(
                {
                    "hour": float(timestamp.hour),
                    "day_of_week": float(timestamp.weekday()),
                }
            )
            features_list.append(
                features
            )  # Exclude service_name from numerical features

        return features_list

    def _aggregate_metrics(self, metrics) -> List[Dict[str, Any]]:
        groups = {}
        for metric in metrics:
            key = f"{metric.service_name}:{metric.metric_name}"
            if key not in groups:
                groups[key] = []
            groups[key].append(metric)

        aggregated = []
        for key, metric_list in groups.items():
            service_name, metric_name = key.split(":", 1)
            values = []
            for m in metric_list:
                try:
                    values.append(float(m.value))  # Convert to float
                except (ValueError, TypeError):
                    continue  # Skip invalid values
            values_array = np.array(values) if values else np.array([0.0])

            aggregated.append(
                {
                    "timestamp": max(m.timestamp for m in metric_list),
                    "service_name": service_name,
                    "metric_name": metric_name,
                    "avg_value": float(np.mean(values_array))
                    if len(values_array) > 0
                    else 0.0,
                    "max_value": float(np.max(values_array))
                    if len(values_array) > 0
                    else 0.0,
                    "min_value": float(np.min(values_array))
                    if len(values_array) > 0
                    else 0.0,
                    "count_values": len(values_array),
                }
            )
        return aggregated

    def _aggregate_logs(self, logs) -> List[Dict[str, Any]]:
        groups = {}
        for log in logs:
            service = log.service_name
            if service not in groups:
                groups[service] = []
            groups[service].append(log)

        aggregated = []
        for service_name, log_list in groups.items():
            error_count = sum(
                1 for log in log_list if log.level.lower() in ["error", "fatal"]
            )
            total_logs = len(log_list)
            aggregated.append(
                {
                    "timestamp": max(log.timestamp for log in log_list),
                    "service_name": service_name,
                    "total_logs": total_logs,
                    "error_count": error_count,
                    "error_rate": error_count / total_logs if total_logs > 0 else 0,
                }
            )
        return aggregated

    def _aggregate_incidents(self, incidents) -> List[Dict[str, Any]]:
        groups = {}
        for incident in incidents:
            service_name = (
                incident.metadata.get("service_name", "unknown")
                if incident.metadata
                else "unknown"
            )
            if service_name not in groups:
                groups[service_name] = []
            groups[service_name].append(incident)

        aggregated = []
        for service_name, incident_list in groups.items():
            critical_count = sum(
                1 for inc in incident_list if inc.severity.lower() == "critical"
            )
            aggregated.append(
                {
                    "timestamp": max(inc.timestamp for inc in incident_list),
                    "service_name": service_name,
                    "total_incidents": len(incident_list),
                    "critical_incidents": critical_count,
                }
            )
        return aggregated

    def _detect_anomalies(
        self, aggregated_data, data_type: str
    ) -> List[Dict[str, Any]]:
        results = []
        features_list = self._extract_features(aggregated_data, data_type)

        for i, (features, raw_data) in enumerate(zip(features_list, aggregated_data)):
            point = [features.get(name, 0.0) for name in self.feature_names]
            point = np.array(point, dtype=float)  # Ensure float dtype
            score = self._get_anomaly_score(point)
            is_anomaly = score > self.threshold

            service = raw_data.get("service_name")
            is_usage_spike = False
            is_critical_error = False
            problem_details = []

            if data_type in ["metrics", "traces"]:
                historic_key = (data_type, service)
                if historic_key in self.historic_stats:
                    stats = self.historic_stats[historic_key]
                    request_rate = features.get("request_rate", 0)
                    if (
                        request_rate
                        > stats["request_rate_mean"] + 3 * stats["request_rate_std"]
                    ):
                        is_usage_spike = True
                        problem_details.append(
                            f"Usage Spike: {request_rate:.2f} req/min vs historical {stats['request_rate_mean']:.2f}"
                        )

            if data_type in ["logs", "traces"]:
                historic_key = (data_type, service)
                if historic_key in self.historic_stats:
                    stats = self.historic_stats[historic_key]
                    error_rate = features.get("error_rate", 0)
                    if (
                        error_rate > stats["error_rate_mean"] + 0.1
                        or error_rate > 2 * stats["error_rate_mean"]
                    ):
                        is_critical_error = True
                        problem_details.append(
                            f"Critical Error: error rate {error_rate:.2%} vs historical {stats['error_rate_mean']:.2%}"
                        )

            result = {
                "timestamp": raw_data.get("timestamp"),
                "service_name": service,
                "data_type": data_type,
                "anomaly_score": round(score, 4),
                "is_anomaly": is_anomaly,
                "is_usage_spike": is_usage_spike,
                "is_critical_error": is_critical_error,
                "threshold": round(self.threshold, 4),
                "features": features,
                "raw_data": raw_data,
                "problem_details": problem_details,
            }
            results.append(result)
        return results

    def _features_to_matrix(self, features_list: List[Dict[str, float]]) -> np.ndarray:
        matrix = []
        for features in features_list:
            row = [float(features.get(name, 0)) for name in self.feature_names]
            matrix.append(row)
        return np.array(matrix, dtype=float)  # Ensure float dtype

    def _build_forest(self, data: np.ndarray):
        self.trees = []
        n_samples = len(data)
        for _ in range(self.n_trees):
            indices = (
                np.random.choice(n_samples, self.sample_size, replace=False)
                if n_samples > self.sample_size
                else np.arange(n_samples)
            )
            sample = data[indices]
            tree = self._build_tree(sample, height=0, max_height=10)
            self.trees.append(tree)

    def _build_tree(self, data: np.ndarray, height: int, max_height: int) -> Dict:
        n_samples, n_features = data.shape
        if height >= max_height or n_samples <= 1:
            return {"type": "leaf", "size": n_samples}

        feature_idx = random.randint(0, n_features - 1)
        feature_values = data[:, feature_idx]
        min_val, max_val = np.min(feature_values), np.max(feature_values)
        if min_val == max_val:
            return {"type": "leaf", "size": n_samples}

        split_value = random.uniform(min_val, max_val)
        left_mask = feature_values < split_value
        return {
            "type": "node",
            "feature": feature_idx,
            "split": split_value,
            "left": self._build_tree(data[left_mask], height + 1, max_height),
            "right": self._build_tree(data[~left_mask], height + 1, max_height),
        }

    def _get_anomaly_score(self, point: np.ndarray) -> float:
        if not self.trees:
            return 0
        path_lengths = [self._get_path_length(point, tree) for tree in self.trees]
        avg_path = np.mean(path_lengths)
        c = self._average_path_length(self.sample_size)
        return float(2 ** (-avg_path / c)) if c > 0 else 0.0

    def _get_path_length(self, point: np.ndarray, tree: Dict, length: int = 0) -> float:
        if tree["type"] == "leaf":
            return length + self._average_path_length(tree["size"])
        if point[tree["feature"]] < tree["split"]:
            return self._get_path_length(point, tree["left"], length + 1)
        return self._get_path_length(point, tree["right"], length + 1)

    def _average_path_length(self, n: int) -> float:
        if n <= 1:
            return 0
        return 2 * (np.log(n - 1) + 0.5772) - (2 * (n - 1) / n)

    def print_results(self, results: List[Dict[str, Any]]):
        issues = [
            r
            for r in results
            if r["is_anomaly"] or r.get("is_usage_spike") or r.get("is_critical_error")
        ]
        logger.info("=== DETECTION RESULTS ===")
        logger.info(f"Total data points: {len(results)}")
        logger.info(f"Issues detected: {len(issues)}")

        for result in issues:
            timestamp = result["timestamp"]
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            elif isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            problems = []
            if result["is_usage_spike"]:
                problems.append("Usage Spike")
            if result["is_critical_error"]:
                problems.append("Critical Error")
            if result["is_anomaly"]:
                problems.append("General Anomaly")

            logger.info(
                f"🚨 {' + '.join(problems)} | {result['data_type']} | {timestamp}"
            )
            logger.info(f"  Service: {result['service_name']}")
            for detail in result["problem_details"]:
                logger.info(f"  {detail}")
            logger.info(
                f"  Score: {result['anomaly_score']:.4f} (threshold: {result['threshold']:.4f})"
            )
