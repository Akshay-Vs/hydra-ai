from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session

from app.config.settings import settings
from app.core.database.organization_credentials_store import (
    OrganizationCredentialsStore,
)
from app.core.database.revoked_token_store import RevokedTokenStore
from app.core.database.session_store import SessionStore
from app.core.database.organization_store import OrganizationStore
from app.core.types.auth_type import SessionClient
from app.services.database_service import get_session
from app.utils.hash_secret import hash_secret
from app.utils.logging import create_logger


security = HTTPBearer()
logger = create_logger(__name__)


def verify_organization_credentials(
    organization_id: str, credential_id: str, organization_secret: str, db: Session
) -> bool:
    """Verify organization credentials (replace verify_client_credentials)"""
    org_store = OrganizationStore(db)
    cred_store = OrganizationCredentialsStore(db)

    # Check if organization exists and is active
    organization = org_store.get_organization(organization_id)
    if not organization:
        logger.warning(f"Organization {organization_id} not found or inactive")
        return False

    # Check credentials from separate table
    credentials = cred_store.get_organization_credential(organization_id, credential_id)
    if not credentials:
        return False

    hashed_input = hash_secret(organization_secret)
    match = credentials["client_secret"] == hashed_input
    if not match:
        logger.warning("Organization secret does not match")
    return match


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "iat": datetime.now()})
    encoded_jwt = jwt.encode(
        to_encode, settings.m2m_auth_secret_key, algorithm=settings.m2m_auth_algorithm
    )
    return encoded_jwt, expire


def create_organization_credential(
    organization_id: str, client_secret: str, expired_at: datetime, db: Session
):
    """Create organization credentials (client ID and secret)"""
    cred_store = OrganizationCredentialsStore(db)

    # Hash the client secret before storing
    secret_hash = hash_secret(client_secret)

    return cred_store.create_organization_credentials(
        organization_id, secret_hash, expired_at
    )


def store_session(
    token_jti: str,
    organization_id: str,
    expires_at: datetime,
    db: Session,
    ip_address: Optional[str] = None,
):
    """Store session information"""
    session_store = SessionStore(db)
    org_store = OrganizationStore(db)

    # Verify organization exists
    organization = org_store.get_organization(organization_id)
    if not organization:
        raise ValueError(f"Organization {organization_id} not found")

    return session_store.create_session(
        token_jti=token_jti,
        organization_id=organization_id,
        expires_at=expires_at,
        ip_address=ip_address,
    )


def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> SessionClient:
    """Dependency to get current authenticated client"""
    token = credentials.credentials

    with session as db:
        try:
            # Decode JWT to get token JTI
            payload = jwt.decode(
                token,
                settings.m2m_auth_secret_key,
                algorithms=[settings.m2m_auth_algorithm],
                options={"verify_exp": False},  # check expiry from database
            )
            token_jti: str | None = payload.get("jti")  # JWT ID
            organization_id: str | None = payload.get("sub")  # Subject (organization)

            if token_jti is None or organization_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token is revoked
        revoked_store = RevokedTokenStore(db)
        if revoked_store.is_token_revoked(token_jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check session validity
        session_store = SessionStore(db)
        auth_session = session_store.get_session(token_jti)

        if not auth_session or not session_store.is_session_valid(token_jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last used timestamp
        session_store.update_session_last_used(token_jti)

        # Return session data with organization info
        return SessionClient(
            session_id=auth_session.id,
            organization_id=auth_session.organization_id,
            organization_name=(
                auth_session.organization.name if auth_session.organization else None
            ),
            expires_at=auth_session.expires_at,
            last_used_at=auth_session.last_used_at,
        )
