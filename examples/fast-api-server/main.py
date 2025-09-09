import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from hydra_sdk import (
    HydraTelemetryClient,
    get_hydra_client,
    setup_hydra_telemetry,
    hydra_trace,
)
from hydra_sdk.hydra_config import HydraConfig
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


# Setup telemetry configuration
config = HydraConfig(
    service_name="my-fastapi-service",
    batch_interval=5,  # Send every 30 seconds
    max_batch_size=100,
    system_metrics_interval=10,  # Collect system metrics every 90 seconds
    timeout=30,
)

# Initialize telemetry client
hydra_client = setup_hydra_telemetry(app, config)

# Alternative: Manual client setup (if not using global SDK)
# hydra_client = HydraTelemetryClient(config, use_contextual_logging=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Start telemetry client on application startup"""
    client = get_hydra_client()
    if client:
        await client.start()
        await client.log_info("FastAPI application started", version="1.0.0")
    yield

    """Stop telemetry client on application shutdown"""
    client = get_hydra_client()
    if client:
        await client.log_info("FastAPI application shutting down")
        await client.stop()


@app.get("/health")
async def health_check():
    """Health check endpoint with telemetry logging"""
    client = get_hydra_client()
    if client:
        await client.log_info("Health check requested", endpoint="/health")
    return {"status": "healthy", "service": "my-fastapi-service"}


@app.get("/api/users/{user_id}")
@hydra_trace("get_user")
async def get_user(user_id: int):
    """Get user endpoint with distributed tracing"""
    client = get_hydra_client()

    if client:
        # Set contextual logging data (if using ContextualLogHelper)
        client.set_log_context(user_id=user_id, endpoint="/api/users")

        try:
            # Create a child span for database operations
            async with client.child_span("database_query", {"table": "users"}) as (
                trace_id,
                span_id,
            ):
                # Simulate database query
                await asyncio.sleep(0.1)
                await client.log_info(f"Database query executed for user {user_id}")

            # Another span for data processing
            async with client.child_span("data_processing") as (trace_id, span_id):
                await asyncio.sleep(0.05)
                await client.log_info(f"User data processed for user {user_id}")

            # Log successful retrieval
            await client.log_info(f"Successfully retrieved user {user_id}")

            # Add custom metric
            from hydra_types.telemetry import Metric

            metric = Metric(
                timestamp=datetime.now(),
                service_name=config.service_name,
                metric_name="api.users.requests",
                value=1,
                unit="count",
            )
            await client.add_metric(metric)

        except Exception as e:
            await client.log_error(f"Error retrieving user {user_id}", error=str(e))
            raise
        finally:
            # Clear contextual data
            client.clear_log_context()

    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": f"user{user_id}@example.com",
    }


@app.get("/api/users")
async def list_users(limit: int = 10, offset: int = 0):
    """List users with telemetry and trace context"""
    client = get_hydra_client()

    if client:
        try:
            raise HTTPException(status_code=500, detail="Internal server error")
            # Use trace_span for the entire operation
            async with client.trace_span(
                "list_users", {"limit": limit, "offset": offset}
            ) as (trace_id, span_id):
                await client.log_info(
                    f"Listing users with limit={limit}, offset={offset}"
                )

                # Simulate database query
                async with client.child_span("database_query") as (_, _):
                    await asyncio.sleep(0.2)

                users = [
                    {"user_id": i, "name": f"User {i}"}
                    for i in range(offset + 1, offset + limit + 1)
                ]

                await client.log_info(f"Retrieved {len(users)} users")

            if not users:
                return

            return {"users": users, "total": 100, "limit": limit, "offset": offset}
        except Exception as e:
            await client.log_error("Error retrieving users", error=str(e))
            raise


@app.post("/api/users")
@hydra_trace("create_user")
async def create_user(user_data: dict):
    """Create user with error handling and telemetry"""
    client = get_hydra_client()

    if client:
        client.set_log_context(
            operation="create_user", user_email=user_data.get("email")
        )

        try:
            # Validate input
            if not user_data.get("email"):
                await client.log_warning("User creation attempted without email")
                return {"error": "Email is required"}, 400

            async with client.child_span("validation") as (trace_id, span_id):
                await client.log_info("User data validation completed")

            async with client.child_span("database_insert") as (trace_id, span_id):
                # Simulate database insert
                await asyncio.sleep(0.15)
                new_user_id = 123
                await client.log_info(f"User created with ID {new_user_id}")

            # Add success metric
            from hydra_types.telemetry import Metric

            metric = Metric(
                timestamp=datetime.now(),
                service_name=config.service_name,
                metric_name="api.users.created",
                value=1,
                unit="count",
            )
            await client.add_metric(metric)

            return {"user_id": new_user_id, "status": "created"}

        except Exception as e:
            await client.log_error(
                "Failed to create user", error=str(e), user_data=user_data
            )
            return {"error": "Internal server error"}, 500
        finally:
            client.clear_log_context()


# Alternative initialization without global SDK
async def init_telemetry_manual():
    """Manual telemetry initialization (alternative approach)"""
    client = HydraTelemetryClient(config, use_contextual_logging=True)
    await client.start()
    return client


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
