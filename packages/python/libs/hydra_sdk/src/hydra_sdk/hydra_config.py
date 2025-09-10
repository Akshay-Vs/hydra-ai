import os


class HydraConfig:
    """Configuration for Hydra telemetry client"""

    def __init__(
        self,
        service_name: str,
        service_version: str,
        batch_interval: int = 5,
        enable_auto_instrumentation: bool = True,
        system_metrics_interval: int = 10,
        max_batch_size: int = 1000,
        timeout: int = 30,
    ):
        self.service_name = service_name or os.getenv(
            "HYDRA_SERVICE_NAME", "unknown-service"
        )
        self.service_version = service_version
        self.batch_interval = batch_interval
        self.enable_auto_instrumentation = enable_auto_instrumentation
        self.system_metrics_interval = system_metrics_interval
        self.max_batch_size = max_batch_size
        self.timeout = timeout
