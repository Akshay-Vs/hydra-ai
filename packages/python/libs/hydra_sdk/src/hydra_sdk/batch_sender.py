import asyncio
import logging
import os
from typing import List, Optional
import httpx
from hydra_types.telemetry import Metric, Log, Trace, Event, Incident, TelemetryBatch

from hydra_sdk.auth_manager import AuthManager
from hydra_sdk.utils import _now
from .hydra_config import HydraConfig


class BatchSender:
    """Handles batching and sending telemetry data to Hydra API"""

    def __init__(self, config: HydraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._http_client: Optional[httpx.AsyncClient] = None
        self._batch_task: Optional[asyncio.Task] = None

        # In-memory storage for batching
        self._metrics: List[Metric] = []
        self._logs: List[Log] = []
        self._traces: List[Trace] = []
        self._events: List[Event] = []
        self._incidents: List[Incident] = []

        # Initialize AuthManager
        self.base_url = os.getenv("HYDRA_BASE_URL", "").rstrip("/")
        self.org_id = os.getenv("HYDRA_ORG_ID", "")
        self.cred_id = os.getenv("HYDRA_CRED_ID", "")
        self.client_secret = os.getenv("HYDRA_CLIENT_SECRET", "")

        if not all([self.base_url, self.org_id, self.cred_id, self.client_secret]):
            raise ValueError(
                "Missing required environment variables for AuthManager, "
                + "please set HYDRA_BASE_URL, HYDRA_ORG_ID, HYDRA_CRED_ID, and HYDRA_CLIENT_SECRET"
            )

        self.auth = AuthManager(
            base_url=self.base_url,
            org_id=self.org_id,
            cred_id=self.cred_id,
            client_secret=self.client_secret,
        )

    async def start(self):
        """Start the batch sender and HTTP client"""
        token = await self.auth.get_token()
        if not token:
            raise RuntimeError("Failed to obtain access token for authentication")

        auth_header = await self.auth.get_auth_header()

        self._http_client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": auth_header["Authorization"],
            },
        )

        # Start background batch worker
        self._batch_task = asyncio.create_task(self._batch_worker())
        self.logger.info("Batch sender started")

    async def stop(self):
        """Stop the batch sender and clean up resources"""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass

        # Send final batch before closing
        await self._send_batch()

        if self._http_client:
            await self._http_client.aclose()

        self.logger.info("Batch sender stopped")

    async def add_metric(self, metric: Metric):
        """Add a metric to the batch queue"""
        self._metrics.append(metric)

    async def add_log(self, log: Log):
        """Add a log to the batch queue"""
        self._logs.append(log)

    async def add_trace(self, trace: Trace):
        """Add a trace to the batch queue"""
        self._traces.append(trace)

    async def add_event(self, event: Event):
        """Add an event to the batch queue"""
        self._events.append(event)

    async def add_incident(self, incident: Incident):
        """Add an incident to the batch queue"""
        self._incidents.append(incident)

    async def _batch_worker(self):
        """Background worker to send batched telemetry data"""
        while True:
            try:
                await asyncio.sleep(self.config.batch_interval)
                await self._send_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in batch worker: {e}")

    async def _send_batch(self):
        """Send collected telemetry data as a batch"""
        if not self._has_data():
            return

        batch = self._create_batch()

        try:
            await self._send_to_api(batch)
            self._clear_sent_data()
            self.logger.debug(
                f"Sent batch with {len(batch.metrics)} metrics, "
                f"{len(batch.logs)} logs, {len(batch.traces)} traces"
            )
        except Exception as e:
            self.logger.error(f"Failed to send telemetry batch: {e}")

    def _has_data(self) -> bool:
        """Check if there's any data to send"""
        return any(
            [self._metrics, self._logs, self._traces, self._events, self._incidents]
        )

    def _create_batch(self) -> TelemetryBatch:
        """Create a telemetry batch from current data"""
        max_size = self.config.max_batch_size

        return TelemetryBatch(
            metrics=self._metrics[:max_size],
            logs=self._logs[:max_size],
            traces=self._traces[:max_size],
            events=self._events[:max_size],
            incidents=self._incidents[:max_size],
            source_system=self.config.service_name,
            export_timestamp=_now(),
        )

    async def _send_to_api(self, batch: TelemetryBatch):
        """Send batch to Hydra API"""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        url = f"{self.base_url}/telemetry/batch/"
        json_data = batch.model_dump_json(indent=2, exclude_none=True)

        self.logger.debug(f"Sending telemetry batch to {url}")
        response = await self._http_client.post(
            url, content=json_data, headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()

    def _clear_sent_data(self):
        """Clear data that was successfully sent"""
        max_size = self.config.max_batch_size

        self._metrics = self._metrics[max_size:]
        self._logs = self._logs[max_size:]
        self._traces = self._traces[max_size:]
        self._events = self._events[max_size:]
        self._incidents = self._incidents[max_size:]
