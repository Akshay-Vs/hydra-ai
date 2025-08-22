import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, Callable, Awaitable
from hydra_types.telemetry import Trace


class TraceContextManager:
    """Manages distributed tracing context and span creation"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._current_trace_id: Optional[str] = None
        self._current_span_id: Optional[str] = None
        self._trace_callback: Optional[Callable[[Trace], Awaitable[None]]] = None

    def set_trace_callback(self, callback: Callable[[Trace], Awaitable[None]]):
        """Set callback function to handle completed traces"""
        self._trace_callback = callback

    @property
    def current_trace_id(self) -> Optional[str]:
        """Get the current trace ID"""
        return self._current_trace_id

    @property
    def current_span_id(self) -> Optional[str]:
        """Get the current span ID"""
        return self._current_span_id

    def set_trace_context(self, trace_id: str, span_id: str):
        """Manually set the current trace context"""
        self._current_trace_id = trace_id
        self._current_span_id = span_id

    def clear_trace_context(self):
        """Clear the current trace context"""
        self._current_trace_id = None
        self._current_span_id = None

    @asynccontextmanager
    async def trace_span(
        self, operation_name: str, attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager for creating trace spans"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        start_time = int(time.time() * 1000)

        # Store current context to restore later
        parent_trace_id = self._current_trace_id
        parent_span_id = self._current_span_id

        # Set new context
        self._current_trace_id = trace_id
        self._current_span_id = span_id

        status = "OK"
        error_attributes = attributes or {}

        try:
            yield trace_id, span_id
        except Exception as e:
            status = "ERROR"
            error_attributes = dict(error_attributes)
            error_attributes["error"] = str(e)
            error_attributes["error_type"] = type(e).__name__
            raise
        finally:
            end_time = int(time.time() * 1000)
            duration_ms = end_time - start_time

            # Create and send trace
            trace = Trace(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                status=status,
                attributes=error_attributes if error_attributes else None,
                service_name=self.service_name,
            )

            if self._trace_callback:
                await self._trace_callback(trace)

            # Restore previous context
            self._current_trace_id = parent_trace_id
            self._current_span_id = parent_span_id

    @asynccontextmanager
    async def child_span(
        self, operation_name: str, attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a child span within the current trace context"""
        if not self._current_trace_id:
            # If no current trace, create a new one
            async with self.trace_span(operation_name, attributes) as (
                trace_id,
                span_id,
            ):
                yield trace_id, span_id
            return

        # Create child span
        parent_trace_id = self._current_trace_id
        parent_span_id = self._current_span_id
        child_span_id = str(uuid.uuid4())
        start_time = int(time.time() * 1000)

        # Update current span context
        self._current_span_id = child_span_id

        status = "OK"
        error_attributes = attributes or {}

        try:
            yield parent_trace_id, child_span_id
        except Exception as e:
            status = "ERROR"
            error_attributes = dict(error_attributes)
            error_attributes["error"] = str(e)
            error_attributes["error_type"] = type(e).__name__
            raise
        finally:
            end_time = int(time.time() * 1000)
            duration_ms = end_time - start_time

            # Create and send child trace
            trace = Trace(
                trace_id=parent_trace_id,
                span_id=child_span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                status=status,
                attributes=error_attributes if error_attributes else None,
                service_name=self.service_name,
            )

            if self._trace_callback:
                await self._trace_callback(trace)

            # Restore parent span context
            self._current_span_id = parent_span_id
