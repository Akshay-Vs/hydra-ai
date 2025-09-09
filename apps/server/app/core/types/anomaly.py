from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel


class AnomalyType(Enum):
    METRIC_SPIKE = "metric_spike"
    ERROR_BURST = "error_burst"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DEPLOYMENT_ISSUE = "deployment_issue"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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
