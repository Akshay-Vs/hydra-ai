import hashlib


def hash_secret(secret: str) -> str:
    """Hash client secret for secure comparison"""
    return hashlib.sha256(secret.encode()).hexdigest()
