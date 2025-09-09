from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from hydra_types.telemetry import Event, Incident, Log, Metric, Trace


# Summary and analytics models
class ServiceMetricSummary(BaseModel):
    """Response model for service metrics summary"""

    metric_name: str
    overall_avg: float
    overall_min: float
    overall_max: float
    data_points: int


class TopErrorService(BaseModel):
    """Response model for top error services"""

    service_name: str
    avg_error_rate: float
    total_errors: int
    total_logs: int


class ServiceIncidentTrend(BaseModel):
    """Response model for service incident trends"""

    timestamp: datetime
    total_incidents: int
    critical_incidents: int
    high_incidents: int
    avg_resolution_time: Optional[float]
    auto_resolved_count: int


class MetricAggregation(BaseModel):
    timestamp: datetime
    service_name: str
    metric_name: str
    avg_value: float
    min_value: float
    max_value: float
    count_values: int
    sum_values: float
    p50_value: float
    p95_value: float
    p99_value: float
    stddev_value: float


class LogAggregation(BaseModel):
    timestamp: datetime
    service_name: str
    total_logs: int
    error_count: int
    warn_count: int
    info_count: int
    debug_count: int
    error_rate: float
    unique_traces: int


class IncidentAggregation(BaseModel):
    timestamp: datetime
    service_name: str
    total_incidents: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    low_incidents: int
    avg_resolution_time: float
    auto_resolved_count: int


class AggregationGranularity(Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


class MetricAggregationData(BaseModel):
    """Response model for metric aggregation data"""

    timestamp: datetime
    service_name: str
    metric_name: str
    avg_value: float
    min_value: float
    max_value: float
    count_values: int
    sum_values: float
    p50_value: Optional[float] = None
    p95_value: Optional[float] = None
    p99_value: Optional[float] = None
    stddev_value: Optional[float] = None
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LogAggregationData(BaseModel):
    """Response model for log aggregation data"""

    timestamp: datetime
    service_name: str
    total_logs: int
    error_count: int = 0
    warn_count: int = 0
    info_count: int = 0
    debug_count: int = 0
    error_rate: float = 0.0
    unique_traces: int = 0
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentAggregationData(BaseModel):
    """Response model for incident aggregation data"""

    timestamp: datetime
    service_name: str
    total_incidents: int
    critical_incidents: int = 0
    high_incidents: int = 0
    medium_incidents: int = 0
    low_incidents: int = 0
    avg_resolution_time: Optional[float] = None
    auto_resolved_count: int = 0
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TraceEvent(BaseModel):
    name: str
    timestamp: int
    attributes: Optional[Dict[str, Any]] = None
