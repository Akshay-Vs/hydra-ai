import traceback
from app.config.settings import settings
from cryptography.fernet import Fernet

from app.utils.logging import create_logger

logger = create_logger(__name__)

if not settings.encryption_key:
    raise ValueError("Encryption key is not set in settings.")

cipher = Fernet(settings.encryption_key)


def encrypt(token: str | bytes) -> bytes:
    """Encrypt the auth_token of an MCPServer instance if it's a valid Fernet token."""
    try:
        if isinstance(token, str):
            token = token.encode()

        return cipher.encrypt(token)
    except Exception as e:
        logger.error(f"Error encrypting auth token: {type(e).__name__} - {e}")
        logger.debug(traceback.format_exc())
        raise e


def decrypt(token: str | bytes) -> str:
    """Decrypt the auth_token of an MCPServer instance if it's a valid Fernet token."""
    try:
        if isinstance(token, bytes):
            token = token.decode()

        return cipher.decrypt(token).decode()

    except Exception as e:
        logger.error(f"Error decrypting auth token: {type(e).__name__} - {e}")
        logger.debug(traceback.format_exc())
        raise e
