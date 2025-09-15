import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Awaitable, Optional
from hydra_types.telemetry import Metric
import psutil
import os

class SystemMetricsCollector:
    """Collects system and process metrics for telemetry"""

    def __init__(
        self, service_name: str, service_version: str, metrics_interval: float = 60.0
    ):
        self.service_name = service_name
        self.service_version = service_version or os.getenv("HYDRA_SERVICE_VERSION")
        self.metrics_interval = metrics_interval
        self.logger = logging.getLogger(__name__)
        self._process = psutil.Process()
        self._collection_task: Optional[asyncio.Task] = None
        self._metric_callback: Optional[Callable[[Metric], Awaitable[None]]] = None

    def set_metric_callback(self, callback: Callable[[Metric], Awaitable[None]]):
        """Set callback function to handle collected metrics"""
        self._metric_callback = callback

    async def start(self):
        """Start collecting system metrics"""
        if self._metric_callback is None:
            raise ValueError("Metric callback must be set before starting")

        self._collection_task = asyncio.create_task(self._collection_worker())
        self.logger.info("System metrics collection started")

    async def stop(self):
        """Stop collecting system metrics"""
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        self.logger.info("System metrics collection stopped")

    async def _collection_worker(self):
        """Background worker to collect system metrics"""
        while True:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.metrics_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")

    async def _collect_metrics(self):
        """Collect all system metrics"""
        now = self._current_timestamp()

        await self._collect_cpu_metrics(now)
        await self._collect_memory_metrics(now)
        await self._collect_process_metrics(now)
        await self._collect_disk_metrics(now)
        await self._collect_network_metrics(now)
        await self._collect_load_metrics(now)

    async def _collect_cpu_metrics(self, timestamp: datetime):
        """Collect CPU-related metrics"""
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = float(psutil.cpu_count() or 0)
        cpu_freq = psutil.cpu_freq()

        await self._send_metric(
            timestamp, "system.cpu.usage_percent", cpu_percent, "percent"
        )
        await self._send_metric(timestamp, "system.cpu.count", cpu_count, "count")

        if cpu_freq:
            await self._send_metric(
                timestamp, "system.cpu.frequency_mhz", cpu_freq.current, "mhz"
            )

    async def _collect_memory_metrics(self, timestamp: datetime):
        """Collect memory-related metrics"""
        memory = psutil.virtual_memory()

        await self._send_metric(
            timestamp, "system.memory.usage_percent", memory.percent, "percent"
        )
        await self._send_metric(
            timestamp, "system.memory.used_bytes", memory.used, "bytes"
        )
        await self._send_metric(
            timestamp, "system.memory.available_bytes", memory.available, "bytes"
        )

    async def _collect_process_metrics(self, timestamp: datetime):
        """Collect process-specific metrics"""
        process_memory = self._process.memory_info()

        await self._send_metric(
            timestamp, "process.memory.rss_bytes", process_memory.rss, "bytes"
        )
        await self._send_metric(
            timestamp,
            "process.cpu.usage_percent",
            self._process.cpu_percent(),
            "percent",
        )

    async def _collect_disk_metrics(self, timestamp: datetime):
        """Collect disk I/O metrics"""
        disk_io = psutil.disk_io_counters()
        if disk_io:
            await self._send_metric(
                timestamp, "system.disk.read_bytes", disk_io.read_bytes, "bytes"
            )
            await self._send_metric(
                timestamp, "system.disk.write_bytes", disk_io.write_bytes, "bytes"
            )

    async def _collect_network_metrics(self, timestamp: datetime):
        """Collect network I/O metrics"""
        network_io = psutil.net_io_counters()
        if network_io:
            await self._send_metric(
                timestamp, "system.network.bytes_sent", network_io.bytes_sent, "bytes"
            )
            await self._send_metric(
                timestamp, "system.network.bytes_recv", network_io.bytes_recv, "bytes"
            )

    async def _collect_load_metrics(self, timestamp: datetime):
        """Collect load average metrics (Unix only)"""
        try:
            load_avg = psutil.getloadavg()
            await self._send_metric(
                timestamp, "system.load.avg_1m", load_avg[0], "load"
            )
            await self._send_metric(
                timestamp, "system.load.avg_5m", load_avg[1], "load"
            )
        except (AttributeError, OSError):
            pass  # Not available on Windows

    async def _send_metric(
        self, timestamp: datetime, name: str, value: float, unit: str
    ):
        """Send a metric using the callback"""
        metric = Metric(
            timestamp=timestamp,
            service_name=self.service_name,
            service_version=self.service_version,
            metric_name=name,
            value=value,
            unit=unit,
        )
        print(f"Sending metric: {metric.model_dump_json(indent=2)}")
        if self._metric_callback:
            await self._metric_callback(metric)

    def _current_timestamp(self) -> datetime:
        """Get current timestamp as a datetime object in UTC"""
        return datetime.now(timezone.utc)
