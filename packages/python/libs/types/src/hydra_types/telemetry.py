from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Metric(BaseModel):
    timestamp: datetime
    service_name: str
    service_version: str
    metric_name: str
    value: float
    labels: Optional[Dict[str, str]] = None
    unit: Optional[str] = None


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Log(BaseModel):
    timestamp: datetime
    service_name: str
    service_version: str
    level: LogLevelEnum
    message: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None


class TraceEvent(BaseModel):
    name: str
    timestamp: int
    attributes: Optional[Dict[str, Any]] = None


class Trace(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str
    attributes: Optional[Dict[str, Any]] = None
    events: Optional[List[TraceEvent]] = None
    service_name: str
    service_version: str


class Event(BaseModel):
    event_id: str
    timestamp: datetime
    event_type: str
    source: str
    severity: str
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Incident(BaseModel):
    incident_id: str
    timestamp: datetime
    severity: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_signature: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class TelemetryBatch(BaseModel):
    metrics: List[Metric] = []
    logs: List[Log] = []
    traces: List[Trace] = []
    events: List[Event] = []
    incidents: List[Incident] = []
    source_system: str
    export_timestamp: datetime
