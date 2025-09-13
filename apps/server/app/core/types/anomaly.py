from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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


class AnomalyThresholds(BaseModel):
    """Configuration for anomaly detection thresholds"""

    error_rate_absolute: float = 60.0  # Absolute error rate threshold (%)
    error_rate_increase: float = 20.0  # Percentage increase threshold
    latency_increase: float = 50.0  # Percentage increase threshold
    resource_increase: float = 40.0  # Percentage increase threshold
    isolation_forest_contamination: float = 0.1
    historical_window_hours: int = 24
    distress_historical_diff: int = 50  # Percentage difference threshold
    distress_error_rate: int = 25  # Percentage error rate threshold
    distress_version_regression: int = 75  # Percentage regression threshold


class AnomalyAlert(BaseModel):
    """Distress signal sent to activate agents"""

    anomaly_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence_score: float
    service_name: str
    title: str
    description: str
    context_data: Dict[str, Any]
    affected_metrics: List[str]
    recommended_actions: List[str]


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
