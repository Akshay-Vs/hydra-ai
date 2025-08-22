import time
from typing import Optional, Dict, Any, Callable, Awaitable
from hydra_types.telemetry import Log


class LogHelper:
    """Helper class for structured logging with trace context"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._log_callback: Optional[Callable[[Log], Awaitable[None]]] = None
        self._trace_context_provider: Optional[
            Callable[[], tuple[Optional[str], Optional[str]]]
        ] = None

    def set_log_callback(self, callback: Callable[[Log], Awaitable[None]]):
        """Set callback function to handle log entries"""
        self._log_callback = callback

    def set_trace_context_provider(
        self, provider: Callable[[], tuple[Optional[str], Optional[str]]]
    ):
        """Set provider function to get current trace context (trace_id, span_id)"""
        self._trace_context_provider = provider

    async def info(self, message: str, **kwargs):
        """Log an info message"""
        await self._create_log("INFO", message, kwargs)

    async def error(self, message: str, **kwargs):
        """Log an error message"""
        await self._create_log("ERROR", message, kwargs)

    async def warning(self, message: str, **kwargs):
        """Log a warning message"""
        await self._create_log("WARNING", message, kwargs)

    async def debug(self, message: str, **kwargs):
        """Log a debug message"""
        await self._create_log("DEBUG", message, kwargs)

    async def critical(self, message: str, **kwargs):
        """Log a critical message"""
        await self._create_log("CRITICAL", message, kwargs)

    async def log(self, level: str, message: str, **kwargs):
        """Log a message with specified level"""
        await self._create_log(level, message, kwargs)

    async def _create_log(
        self, level: str, message: str, structured_data: Dict[str, Any]
    ):
        """Create and send a log entry"""
        if self._log_callback is None:
            return

        # Get current trace context if available
        trace_id, span_id = None, None
        if self._trace_context_provider:
            trace_id, span_id = self._trace_context_provider()

        log = Log(
            timestamp=self._current_timestamp(),
            service_name=self.service_name,
            level=level.upper(),
            message=message,
            trace_id=trace_id,
            span_id=span_id,
            structured_data=structured_data if structured_data else None,
        )

        await self._log_callback(log)

    def _current_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)


class ContextualLogHelper(LogHelper):
    """Log helper that includes additional context like user ID, request ID, etc."""

    def __init__(self, service_name: str):
        super().__init__(service_name)
        self._context: Dict[str, Any] = {}

    def set_context(self, **context_data):
        """Set additional context data that will be included in all logs"""
        self._context.update(context_data)

    def clear_context(self):
        """Clear all context data"""
        self._context.clear()

    def remove_context(self, *keys):
        """Remove specific keys from context"""
        for key in keys:
            self._context.pop(key, None)

    async def _create_log(
        self, level: str, message: str, structured_data: Dict[str, Any]
    ):
        """Create and send a log entry with additional context"""
        # Merge context data with structured data
        merged_data = dict(self._context)
        merged_data.update(structured_data)

        await super()._create_log(level, message, merged_data)
