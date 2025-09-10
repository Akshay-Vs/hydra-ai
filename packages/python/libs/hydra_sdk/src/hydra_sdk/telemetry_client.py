import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from hydra_sdk.batch_sender import BatchSender
from hydra_sdk.log_helper import ContextualLogHelper, LogHelper
from hydra_sdk.system_metric_collector import SystemMetricsCollector
from hydra_sdk.trace_context_manager import TraceContextManager

from .hydra_config import HydraConfig
from hydra_types.telemetry import Metric, Log, Event, Incident, Trace


class HydraTelemetryClient:
    """Main telemetry client for collecting and sending data to Hydra"""

    def __init__(self, config: HydraConfig, use_contextual_logging: bool = False):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self._batch_sender = BatchSender(config)
        self._system_metrics = SystemMetricsCollector(
            config.service_name, config.service_version, config.system_metrics_interval
        )
        self._trace_manager = TraceContextManager(
            config.service_name, config.service_version
        )

        # Initialize logging helper
        if use_contextual_logging:
            self._log_helper = ContextualLogHelper(
                config.service_name, config.service_version
            )
        else:
            self._log_helper = LogHelper(config.service_name, config.service_version)

        # Wire up callbacks
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Setup callbacks between components"""
        # System metrics -> batch sender
        self._system_metrics.set_metric_callback(self._batch_sender.add_metric)

        # Trace manager -> batch sender
        self._trace_manager.set_trace_callback(self._batch_sender.add_trace)

        # Log helper -> batch sender
        self._log_helper.set_log_callback(self._batch_sender.add_log)

        # Log helper -> trace context
        self._log_helper.set_trace_context_provider(
            lambda: (
                self._trace_manager.current_trace_id,
                self._trace_manager.current_span_id,
            )
        )

    async def start(self):
        """Start the telemetry client and all components"""
        await self._batch_sender.start()
        await self._system_metrics.start()

        self.logger.info(
            f"Hydra telemetry client started for service: {self.config.service_name}"
        )

    async def stop(self):
        """Stop the telemetry client and clean up resources"""
        await self._system_metrics.stop()
        await self._batch_sender.stop()

        self.logger.info("Hydra telemetry client stopped")

    # Direct telemetry data methods
    async def add_metric(self, metric: Metric):
        """Add a metric to the collection queue"""
        await self._batch_sender.add_metric(metric)

    async def add_log(self, log: Log):
        """Add a log to the collection queue"""
        await self._batch_sender.add_log(log)

    async def add_trace(self, trace: Trace):
        """Add a trace to the collection queue"""
        await self._batch_sender.add_trace(trace)

    async def add_event(self, event: Event):
        """Add an event to the collection queue"""
        await self._batch_sender.add_event(event)

    async def add_incident(self, incident: Incident):
        """Add an incident to the collection queue"""
        await self._batch_sender.add_incident(incident)

    # Logging helper methods
    async def log_info(self, message: str, **kwargs):
        """Log an info message"""
        await self._log_helper.info(message, **kwargs)

    async def log_error(self, message: str, **kwargs):
        """Log an error message"""
        await self._log_helper.error(message, **kwargs)

    async def log_warning(self, message: str, **kwargs):
        """Log a warning message"""
        await self._log_helper.warning(message, **kwargs)

    async def log_debug(self, message: str, **kwargs):
        """Log a debug message"""
        await self._log_helper.debug(message, **kwargs)

    async def log_critical(self, message: str, **kwargs):
        """Log a critical message"""
        await self._log_helper.critical(message, **kwargs)

    # Tracing methods
    @asynccontextmanager
    async def trace_span(
        self, operation_name: str, attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager for creating trace spans"""
        async with self._trace_manager.trace_span(operation_name, attributes) as (
            trace_id,
            span_id,
        ):
            yield trace_id, span_id

    @asynccontextmanager
    async def child_span(
        self, operation_name: str, attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager for creating child spans"""
        async with self._trace_manager.child_span(operation_name, attributes) as (
            trace_id,
            span_id,
        ):
            yield trace_id, span_id

    def set_trace_context(self, trace_id: str, span_id: str):
        """Manually set the current trace context"""
        self._trace_manager.set_trace_context(trace_id, span_id)

    def clear_trace_context(self):
        """Clear the current trace context"""
        self._trace_manager.clear_trace_context()

    @property
    def current_trace_id(self) -> Optional[str]:
        """Get the current trace ID"""
        return self._trace_manager.current_trace_id

    @property
    def current_span_id(self) -> Optional[str]:
        """Get the current span ID"""
        return self._trace_manager.current_span_id

    # Contextual logging methods (only available if using ContextualLogHelper)
    def set_log_context(self, **context_data):
        """Set additional context data for logging (if using contextual logging)"""
        if isinstance(self._log_helper, ContextualLogHelper):
            self._log_helper.set_context(**context_data)

    def clear_log_context(self):
        """Clear logging context (if using contextual logging)"""
        if isinstance(self._log_helper, ContextualLogHelper):
            self._log_helper.clear_context()

    def remove_log_context(self, *keys):
        """Remove specific keys from logging context (if using contextual logging)"""
        if isinstance(self._log_helper, ContextualLogHelper):
            self._log_helper.remove_context(*keys)
