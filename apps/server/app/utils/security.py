import secrets
import base64


def generate_key(length: int = 43) -> str:
    """
    Generate a cryptographically secure random string, similar to Base64 format,
    without padding, safe for URLs.

    Args:
        length (int): Desired length of the key. Default is 43 (similar to your example).

    Returns:
        str: Secure random key.
    """
    # Generate enough random bytes and encode in URL-safe base64
    key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    return key[:length]
