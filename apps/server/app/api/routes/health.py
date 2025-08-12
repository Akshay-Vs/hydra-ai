from fastapi import APIRouter, status
from datetime import datetime, timezone
import psutil
import socket
import sys
import os


router = APIRouter()


@router.get(
    "/hello",
    status_code=status.HTTP_200_OK,
    summary="Basic metrics",
    description="Returns basic application metrics",
)
async def hello():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": (
            datetime.now(timezone.utc)
            - datetime.fromtimestamp(psutil.boot_time(), timezone.utc)
        ).total_seconds(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "hostname": socket.gethostname(),
        "python_version": sys.version,
        "os_version": os.uname().version,
        "message": "Hello, World!",
    }
