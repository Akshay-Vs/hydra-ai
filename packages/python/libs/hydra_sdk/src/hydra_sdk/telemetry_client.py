import asyncio
import logging
import psutil
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from utils import _now

import httpx
from hydra_config import HydraConfig
from hydra_types.telemetry import Metric, Log, Event, Incident, TelemetryBatch, Trace

class HydraTelemetryClient:
    """Main telemetry client for collecting and sending data to Hydra"""

    def __init__(self, config: HydraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # In-memory storage for batching
        self._metrics: List[Metric] = []
        self._logs: List[Log] = []
        self._traces: List[Trace] = []
        self._events: List[Event] = []
        self._incidents: List[Incident] = []

        # Background tasks
        self._batch_task: Optional[asyncio.Task] = None
        self._system_metrics_task: Optional[asyncio.Task] = None
        self._http_client: httpx.AsyncClient

        # Current trace context
        self._current_trace_id: Optional[str] = None
        self._current_span_id: Optional[str] = None

        # Process info for system metrics
        self._process = psutil.Process()

    async def start(self):
        """Start the telemetry client and background tasks"""
        if not self.config.app_id or not self.config.secret_key:
            raise ValueError("app_id and secret_key must be set in the configuration")

        auth = httpx.BasicAuth(self.config.app_id, self.config.secret_key)
        self._http_client = httpx.AsyncClient(
            auth=auth,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"},
        )

        # Start background tasks
        self._batch_task = asyncio.create_task(self._batch_worker())
        self._system_metrics_task = asyncio.create_task(self._system_metrics_worker())

        self.logger.info(
            f"Hydra telemetry client started for service: {self.config.service_name}"
        )

    async def stop(self):
        """Stop the telemetry client and clean up resources"""
        if self._batch_task:
            self._batch_task.cancel()
        if self._system_metrics_task:
            self._system_metrics_task.cancel()

        # Send final batch
        await self._send_batch()

        if self._http_client:
            await self._http_client.aclose()

        self.logger.info("Hydra telemetry client stopped")

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

    async def _system_metrics_worker(self):
        """Background worker to collect system metrics"""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.config.system_metrics_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")

    async def _collect_system_metrics(self):
        """Collect system metrics for anomaly prediction"""
        now = _now()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = float(psutil.cpu_count() or 0)
        cpu_freq = psutil.cpu_freq()

        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="system.cpu.usage_percent",
                value=cpu_percent,
                unit="percent",
            )
        )

        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="system.cpu.count",
                value=cpu_count,
                unit="count",
            )
        )

        if cpu_freq:
            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.cpu.frequency_mhz",
                    value=cpu_freq.current,
                    unit="mhz",
                )
            )

        # Memory metrics
        memory = psutil.virtual_memory()
        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="system.memory.usage_percent",
                value=memory.percent,
                unit="percent",
            )
        )

        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="system.memory.used_bytes",
                value=memory.used,
                unit="bytes",
            )
        )

        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="system.memory.available_bytes",
                value=memory.available,
                unit="bytes",
            )
        )

        # Process-specific metrics
        process_memory = self._process.memory_info()
        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="process.memory.rss_bytes",
                value=process_memory.rss,
                unit="bytes",
            )
        )

        await self.add_metric(
            Metric(
                timestamp=now,
                service_name=self.config.service_name,
                metric_name="process.cpu.usage_percent",
                value=self._process.cpu_percent(),
                unit="percent",
            )
        )

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.disk.read_bytes",
                    value=disk_io.read_bytes,
                    unit="bytes",
                )
            )

            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.disk.write_bytes",
                    value=disk_io.write_bytes,
                    unit="bytes",
                )
            )

        # Network I/O
        network_io = psutil.net_io_counters()
        if network_io:
            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.network.bytes_sent",
                    value=network_io.bytes_sent,
                    unit="bytes",
                )
            )

            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.network.bytes_recv",
                    value=network_io.bytes_recv,
                    unit="bytes",
                )
            )

        # Load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.load.avg_1m",
                    value=load_avg[0],
                    unit="load",
                )
            )

            await self.add_metric(
                Metric(
                    timestamp=now,
                    service_name=self.config.service_name,
                    metric_name="system.load.avg_5m",
                    value=load_avg[1],
                    unit="load",
                )
            )
        except (AttributeError, OSError):
            pass  # Not available on Windows

    async def _send_batch(self):
        """Send collected telemetry data as a batch"""
        if not any(
            [self._metrics, self._logs, self._traces, self._events, self._incidents]
        ):
            return

        batch = TelemetryBatch(
            metrics=self._metrics[: self.config.max_batch_size],
            logs=self._logs[: self.config.max_batch_size],
            traces=self._traces[: self.config.max_batch_size],
            events=self._events[: self.config.max_batch_size],
            incidents=self._incidents[: self.config.max_batch_size],
            source_system=self.config.service_name,
            export_timestamp=_now(),
        )

        try:
            url = "http://localhost:8000/telemetry/batch/"
            json_data = batch.model_dump_json(indent=2, exclude_none=True)
            print(f"Sending telemetry batch to {url}: {json_data[:100]}...")
            response = await self._http_client.post(
                url, content=json_data, headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            # Clear sent data
            self._metrics = self._metrics[self.config.max_batch_size :]
            self._logs = self._logs[self.config.max_batch_size :]
            self._traces = self._traces[self.config.max_batch_size :]
            self._events = self._events[self.config.max_batch_size :]
            self._incidents = self._incidents[self.config.max_batch_size :]

            self.logger.debug(
                f"Sent batch with {len(batch.metrics)} metrics, {len(batch.logs)} logs"
            )

        except Exception as e:
            self.logger.error(f"Failed to send telemetry batch: {e}")

    # Public API methods
    async def add_metric(self, metric: Metric):
        """Add a metric to the collection queue"""
        self._metrics.append(metric)

    async def add_log(self, log: Log):
        """Add a log to the collection queue"""
        self._logs.append(log)

    async def add_trace(self, trace: Trace):
        """Add a trace to the collection queue"""
        self._traces.append(trace)

    async def add_event(self, event: Event):
        """Add an event to the collection queue"""
        self._events.append(event)

    async def add_incident(self, incident: Incident):
        """Add an incident to the collection queue"""
        self._incidents.append(incident)

    # Helper methods for easy logging
    async def log_info(self, message: str, **kwargs):
        """Log an info message"""
        await self.add_log(
            Log(
                timestamp=_now(),
                service_name=self.config.service_name,
                level="INFO",
                message=message,
                trace_id=self._current_trace_id,
                span_id=self._current_span_id,
                structured_data=kwargs if kwargs else None,
            )
        )

    async def log_error(self, message: str, **kwargs):
        """Log an error message"""
        await self.add_log(
            Log(
                timestamp=_now(),
                service_name=self.config.service_name,
                level="ERROR",
                message=message,
                trace_id=self._current_trace_id,
                span_id=self._current_span_id,
                structured_data=kwargs if kwargs else None,
            )
        )

    async def log_warning(self, message: str, **kwargs):
        """Log a warning message"""
        await self.add_log(
            Log(
                timestamp=_now(),
                service_name=self.config.service_name,
                level="WARNING",
                message=message,
                trace_id=self._current_trace_id,
                span_id=self._current_span_id,
                structured_data=kwargs if kwargs else None,
            )
        )

    # Trace context management
    @asynccontextmanager
    async def trace_span(
        self, operation_name: str, attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager for creating trace spans"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        start_time = int(time.time() * 1000)

        # Set current trace context
        parent_trace_id = self._current_trace_id
        parent_span_id = self._current_span_id
        self._current_trace_id = trace_id
        self._current_span_id = span_id

        sys_status: str = "OK"
        try:
            yield trace_id, span_id
        except Exception as e:
            sys_status = "ERROR"
            if attributes is None:
                attributes = {}
            attributes["error"] = str(e)
            raise

        finally:
            end_time = int(time.time() * 1000)
            duration_ms = end_time - start_time

            trace = Trace(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                status=sys_status,
                attributes=attributes,
                service_name=self.config.service_name,
            )

            await self.add_trace(trace)

            # Restore previous trace context
            self._current_trace_id = parent_trace_id
            self._current_span_id = parent_span_id
