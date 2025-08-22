import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils import _now

from telemetry_client import HydraTelemetryClient
from hydra_types.telemetry import Metric, Trace



class HydraMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic HTTP request instrumentation"""

    def __init__(self, app, hydra_client: HydraTelemetryClient):
        super().__init__(app)
        self.hydra_client = hydra_client

    async def dispatch(self, request: Request, call_next):
        if not self.hydra_client.config.enable_auto_instrumentation:
            return await call_next(request)

        start_time = time.time()
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())

        # Set trace context
        self.hydra_client._current_trace_id = trace_id
        self.hydra_client._current_span_id = span_id

        try:
            response = await call_next(request)
            status = "OK"
            error = None
        except Exception as e:
            status = "ERROR"
            error = str(e)
            response = Response(status_code=500)

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        # Create HTTP trace
        attributes = {
            "http.method": request.method,
            "http.url": str(request.url),
            "http.status_code": response.status_code,
            "http.user_agent": request.headers.get("user-agent", ""),
        }

        if error:
            attributes["error"] = error

        trace = Trace(
            trace_id=trace_id,
            span_id=span_id,
            operation_name=f"{request.method} {request.url.path}",
            start_time=int(start_time * 1000),
            end_time=int(end_time * 1000),
            duration_ms=duration_ms,
            status=status,
            attributes=attributes,
            service_name=self.hydra_client.config.service_name,
        )

        await self.hydra_client.add_trace(trace)

        # Add HTTP metrics
        now = _now()

        await self.hydra_client.add_metric(
            Metric(
                timestamp=now,
                service_name=self.hydra_client.config.service_name,
                metric_name="http.request.duration_ms",
                value=duration_ms,
                labels={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": str(response.status_code),
                },
                unit="milliseconds",
            )
        )

        await self.hydra_client.add_metric(
            Metric(
                timestamp=now,
                service_name=self.hydra_client.config.service_name,
                metric_name="http.request.count",
                value=1,
                labels={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": str(response.status_code),
                },
                unit="count",
            )
        )

        # Clear trace context
        self.hydra_client._current_trace_id = None
        self.hydra_client._current_span_id = None

        return response
