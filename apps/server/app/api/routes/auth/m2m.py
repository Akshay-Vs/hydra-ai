from typing import Any
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session
import jwt

from app.config.settings import settings
from app.core.auth.m2m_auth import (
    verify_organization_credentials,
    create_access_token,
    store_session,
    get_current_client,
)
from app.core.database.revoked_token_store import RevokedTokenStore
from app.services.database_service import get_session
from app.core.database.session_store import SessionStore
from app.utils.logging import create_logger
from app.utils.now import now

router = APIRouter()
security = HTTPBearer()
logger = create_logger(__name__)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class OrganizationInfo(BaseModel):
    organization_id: str
    organization_name: str
    session_id: str
    expires_at: str
    last_used_at: str


@router.post(
    "/token",
)
async def get_access_token(token_request: Any, db: Session = Depends(get_session)):
    """
    OAuth2 Client Credentials Grant endpoint
    Authenticate organization and issue bearer token
    """
    # Validate grant type
    if token_request.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported grant type"
        )

    # Verify organization credentials (updated from client credentials)
    if not verify_organization_credentials(
        token_request.client_id,  # Now represents organization_id
        token_request.client_secret,  # Now represents organization_secret
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid organization credentials",
        )

    # Create access token with JTI for session tracking
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token_jti = str(uuid.uuid4())  # Generate unique token ID
    token_data = {
        "sub": token_request.client_id,  # Organization ID as subject
        "jti": token_jti,  # JWT ID for session management
        "type": "access_token",
        "scope": "api_access",
    }

    access_token, expires_at = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    # Store session with proper organization context
    try:
        store_session(
            token_jti=token_jti,
            organization_id=token_request.client_id,
            expires_at=expires_at,
            db=db,
            ip_address=None,  # Could be extracted from request if needed
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/verify", response_model=Any)
async def verify_token(
    current_client: dict = Depends(get_current_client),
):
    """
    Verify the current bearer token and return organization information
    """
    return OrganizationInfo(
        organization_id=current_client["organization_id"],
        organization_name=current_client["organization_name"],
        session_id=current_client["session_id"],
        expires_at=current_client["expires_at"],
        last_used_at=current_client["last_used_at"],
    )


@router.post("/revoke")
async def revoke_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
):
    """
    Revoke the current bearer token
    """
    token = credentials.credentials

    try:
        # Decode token to get JTI

        payload = jwt.decode(
            token,
            settings.m2m_auth_secret_key,
            algorithms=[settings.m2m_auth_algorithm],
            options={"verify_exp": False},
        )
        token_jti = payload.get("jti")

        if not token_jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format"
            )

        session_store = SessionStore(db)
        session = session_store.get_session(token_jti)

        if not session or not session_store.is_session_valid(token_jti):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token already revoked"
            )

        # Add token to revoked list
        revoked_store = RevokedTokenStore(db)
        revoked_store.revoke_token(
            token_jti, organization_id=session.organization_id, expires_at=now()
        )

        return {"message": "Token revoked successfully"}

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error revoking token",
        )


@router.get("/sessions")
async def list_active_sessions(
    current_client: dict = Depends(get_current_client),
    db: Session = Depends(get_session),
):
    """
    List all active sessions for the authenticated organization
    """
    organization_id = current_client["organization_id"]
    session_store = SessionStore(db)

    # Get all active sessions for the organization
    active_sessions = session_store.get_organization_settings(organization_id)

    # Format response (excluding sensitive information)
    sessions_response = []
    for session in active_sessions:
        if session_store.is_session_valid(session.token_jti):
            sessions_response.append(
                {
                    "session_id": session.id,
                    "token_jti_hash": session.token_jti[:16]
                    + "...",  # Partial hash for identification
                    "created_at": session.created_at,
                    "expires_at": session.expires_at,
                    "last_used_at": session.last_used_at,
                    "ip_address": session.ip_address,
                }
            )

    return {"organization_id": organization_id, "active_sessions": sessions_response}
