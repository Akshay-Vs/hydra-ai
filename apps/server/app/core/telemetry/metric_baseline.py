from datetime import datetime
from typing import Dict


class MetricBaseline:
    """Statistical baseline for each metric"""

    def __init__(self):
        self.mean: float = 0.0
        self.std: float = 0.0
        self.percentiles: Dict[int, float] = {}
        self.last_updated: datetime = datetime.now()
        self.sample_count: int = 0
