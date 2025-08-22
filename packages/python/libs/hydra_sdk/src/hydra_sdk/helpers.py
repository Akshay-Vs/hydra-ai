from typing import Optional
from functools import wraps
from fastapi import FastAPI


from .hydra_config import HydraConfig
from .hydra_middleware import HydraMiddleware
from .telemetry_client import HydraTelemetryClient


# Decorator for route-specific instrumentation
def hydra_trace(operation_name: Optional[str] = None):
    """Decorator for tracing specific functions"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Try to get hydra client from app state or global
            hydra_client = getattr(async_wrapper, "_hydra_client", None)
            if not hydra_client:
                return await func(*args, **kwargs)

            op_name = operation_name or func.__name__
            async with hydra_client.trace_span(op_name) as (trace_id, span_id):
                return await func(*args, **kwargs)

        return async_wrapper

    return decorator


# Global client instance
_global_hydra_client: Optional[HydraTelemetryClient] = None


def get_hydra_client() -> Optional[HydraTelemetryClient]:
    """Get the global Hydra client instance"""
    return _global_hydra_client


def setup_hydra_telemetry(app: FastAPI, config: HydraConfig) -> HydraTelemetryClient:
    """Setup Hydra telemetry for a FastAPI app"""
    global _global_hydra_client

    client = HydraTelemetryClient(config)
    _global_hydra_client = client

    # Add middleware
    app.add_middleware(HydraMiddleware, hydra_client=client)

    # Setup lifespan events
    @app.on_event("startup")
    async def startup_event():
        await client.start()

    @app.on_event("shutdown")
    async def shutdown_event():
        await client.stop()

    return client
