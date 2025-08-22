import os


class HydraConfig:
    """Configuration for Hydra telemetry client"""

    def __init__(
        self,
        hydra_base_url: str,
        app_id: str,
        secret_key: str,
        service_name: str,
        batch_interval: int = 5,
        enable_auto_instrumentation: bool = True,
        system_metrics_interval: int = 10,
        max_batch_size: int = 1000,
        timeout: int = 30,
    ):
        self.hydra_base_url = hydra_base_url or os.getenv(
            "HYDRA_BASE_URL", "http://localhost:8000/"
        )
        self.app_id = app_id or os.getenv("HYDRA_APP_ID")
        self.secret_key = secret_key or os.getenv("HYDRA_SECRET_KEY")
        self.service_name = service_name or os.getenv(
            "HYDRA_SERVICE_NAME", "unknown-service"
        )
        self.batch_interval = batch_interval
        self.enable_auto_instrumentation = enable_auto_instrumentation
        self.system_metrics_interval = system_metrics_interval
        self.max_batch_size = max_batch_size
        self.timeout = timeout

        if not all([self.hydra_base_url, self.app_id, self.secret_key]):
            raise ValueError("hydra_base_url, app_id, and secret_key must be provided")

        # Ensure base URL ends with /telemetry
        if not self.hydra_base_url.endswith("/"):
            self.hydra_base_url += "/"
        if not self.hydra_base_url.endswith("telemetry/"):
            self.hydra_base_url += "telemetry/"
