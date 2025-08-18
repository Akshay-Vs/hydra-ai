from functools import wraps
from typing import Callable
from fastapi import Request, HTTPException
from sqlmodel import select
import logging

from app.config.settings import settings
from app.core.auth.clerk_auth import ClerkAuth
from app.models.sql_model import User
from app.services.database_service import get_session

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> User:
    """
    FastAPI dependency that handles Clerk authentication and returns the User object.
    Usage: user: User = Depends(get_current_user)
    """
    try:
        # Authenticate with Clerk
        if not settings.clerk_secret_key:
            raise HTTPException(
                status_code=500, detail="Clerk secret key is not configured"
            )

        authenticator = ClerkAuth(settings.clerk_secret_key)
        clerk_user = await authenticator.authenticate_HTTP(request)

        # Get user from database
        with get_session() as session:
            user = session.exec(
                select(User).where(User.clerk_id == clerk_user.id)
            ).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")
