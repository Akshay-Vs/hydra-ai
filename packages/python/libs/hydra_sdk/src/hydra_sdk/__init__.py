"""
Hydra Telemetry Client - A comprehensive telemetry solution for Python applications

This package provides tools for collecting, batching, and sending telemetry data
including metrics, logs, traces, events, and incidents to the Hydra platform.

Main Components:
- HydraTelemetryClient: Main client for telemetry operations
- SystemMetricsCollector: Automatic system metrics collection
- BatchSender: Efficient batching and HTTP transmission
- TraceContextManager: Distributed tracing support
- LogHelper: Structured logging with trace context
- Hydra SDK: Global client and decorators for easy integration
"""

# Version information
__version__ = "1.0.0"

# Core components
from .telemetry_client import HydraTelemetryClient
from .system_metric_collector import SystemMetricsCollector
from .batch_sender import BatchSender
from .trace_context_manager import TraceContextManager
from .log_helper import LogHelper, ContextualLogHelper

# SDK utilities
from .helpers import (
    hydra_trace,
    get_hydra_client,
    setup_hydra_telemetry,
    _global_hydra_client,
)

# Public API
__all__ = [
    # Main client
    "HydraTelemetryClient",
    # Individual components (for advanced usage)
    "SystemMetricsCollector",
    "BatchSender",
    "TraceContextManager",
    "LogHelper",
    "ContextualLogHelper",
    # SDK utilities
    "hydra_trace",
    "get_hydra_client",
    "setup_hydra_telemetry",
    "_global_hydra_client",
    # Metadata
    "__version__",
]

