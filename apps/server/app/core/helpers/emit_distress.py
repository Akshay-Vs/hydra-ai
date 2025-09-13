from app.core.types.anomaly import AnomalyDetection
from app.utils.logging import create_logger
from app.core.helpers.event_emitter import emit, capture

logger = create_logger(__name__)


def emit_distress(anomaly: AnomalyDetection):
    logger.critical("🚨 DISTRESS SIGNAL EMITTED - Critical anomaly detected!")
    emit("distress", anomaly)   # pass the object directly

def capture_distress(callback):
    capture("distress", callback)
