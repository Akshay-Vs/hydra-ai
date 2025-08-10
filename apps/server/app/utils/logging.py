import logging
import sys
from typing import Any, Dict

import structlog
from structlog.typing import EventDict


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log events."""
    event_dict["app"] = "fastapi-socketio"
    return event_dict


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID from context if available."""
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    development: bool = False
) -> None:
    """
    Setup structured logging for FastAPI SocketIO application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
        development: Whether running in development mode (affects formatting)
    """

    # Configure log level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # Common processors for all configurations
    processors = [
        # Add timestamp
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),

        # Add custom context
        add_app_context,
        add_correlation_id,

        # Add caller information in development
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.FUNC_NAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ) if development else lambda *args: args[2],  # No-op if not development

        # Exception handling
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),

        # Stack info
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty printing for development
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True) if development
            else structlog.processors.JSONRenderer()
        ])

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure uvicorn loggers
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "socketio",
        "engineio"
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True

    # Set specific log levels for different components
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("socketio").setLevel(logging.INFO)
    logging.getLogger("engineio").setLevel(logging.WARNING)  # More verbose, usually set to WARNING


def create_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Create a bound logger with the given name."""
    return structlog.get_logger(name)


def setup_request_logging_middleware():
    """
    Example middleware setup for request correlation.
    You would integrate this with your FastAPI app.
    """
    import uuid
    from contextvars import ContextVar

    request_id_var: ContextVar[str] = ContextVar('request_id')

    def add_request_id_to_logs(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        try:
            request_id = request_id_var.get()
            event_dict["request_id"] = request_id
        except LookupError:
            pass  # No request ID in context
        return event_dict

    return add_request_id_to_logs, request_id_var


if __name__ == "__main__":
    # Development setup
    setup_logging(
        log_level="DEBUG",
        json_logs=False,
        development=True
    )

    # Create logger
    logger = create_logger("main")
    logger.info("Application starting", version="1.0.0")

    # Example structured logging
    logger.info(
        "User action",
        user_id="12345",
        action="login",
        ip_address="192.168.1.1",
        extra_data={"browser": "Chrome", "os": "Windows"}
    )
