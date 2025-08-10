from app.main import asgi_app
from app.config.settings import settings
import uvicorn

uvicorn.run(
    asgi_app,
    host=settings.host,
    port=settings.port,
    log_level=settings.log_level.lower(),
    reload=settings.debug,
)
