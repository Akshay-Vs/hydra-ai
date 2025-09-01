from cuid import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi import HTTPException

from app.core.auth.m2m_auth import create_organization_credential
from app.core.database.organization_credentials_store import (
    OrganizationCredentialsStore,
)
from app.core.helpers.ensure_membership import ensure_org_membership
from app.core.helpers.ensure_permissions import ensure_org_permissions
from app.core.helpers.get_user import get_current_user
from app.models.enums import Permissions
from app.models.sql_model import User
from app.services.database_service import get_session
from app.utils.datetime_from_now import datetime_from_now
from app.utils.logging import create_logger
from app.utils.security import generate_key

router = APIRouter()
logger = create_logger(__name__)


class OrgCredRequest(BaseModel):
    organization_id: str
    expires_in: Optional[int]


class OrgCredResponse(BaseModel):
    hydra_org_id: str
    hydra_cred_id: str
    hydra_client_secret: str
    expires_at: str


@router.post("/generate")
async def generate_organization_credentials(
    payload: OrgCredRequest,
    db=Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Generate credentials for an organization.
    """
    logger.info(f"Generating credentials for organization: {payload.organization_id}")
    try:
        with db as session:
            membership = ensure_org_membership(session, payload.organization_id, user)
            ensure_org_permissions(
                session,
                membership,
                [Permissions.READ, Permissions.WRITE],
            )

            secret = generate_key()
            expires_at = datetime_from_now(payload.expires_in or 90)

            # Placeholder for actual credential generation logic
            credentials = create_organization_credential(
                payload.organization_id,
                secret,
                expires_at,
                session,
            )

            return OrgCredResponse(
                hydra_org_id=payload.organization_id,
                hydra_cred_id=credentials.id,
                hydra_client_secret=secret,
                expires_at=expires_at.isoformat(),
            )

    except HTTPException as e:
        logger.error(f"Error generating credentials: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Failed to generate credentials"}, 500


@router.get("/{organization_id}")
async def get_all_credentials(
    organization_id: str,
    db=Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Retrieve all credentials for an organization.
    """
    logger.info(f"Retrieving all credentials for organization: {organization_id}")
    try:
        with db as session:
            membership = ensure_org_membership(session, organization_id, user)
            ensure_org_permissions(
                session,
                membership,
                [Permissions.READ, Permissions.WRITE],
            )

            organization_store = OrganizationCredentialsStore(session)
            credentials = organization_store.get_all_organization_credentials(
                organization_id
            )
            return credentials
    except HTTPException as e:
        logger.error(f"Error retrieving credentials: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Failed to retrieve credentials"}, 500


@router.get("/{organization_id}/{credential_id}")
async def get_credentials(
    organization_id: str,
    credential_id: str,
    db=Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Retrieve credentials for an organization.
    """
    logger.info(
        f"Retrieving credentials for organization: {organization_id}, user: {user.id}"
    )
    try:
        with db as session:
            membership = ensure_org_membership(session, organization_id, user)
            ensure_org_permissions(
                session,
                membership,
                [Permissions.READ, Permissions.WRITE],
            )

            organization_store = OrganizationCredentialsStore(session)
            credentials = organization_store.get_organization_credential(
                organization_id, credential_id
            )
            return credentials
    except HTTPException as e:
        logger.error(f"Error retrieving credentials: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Failed to retrieve credentials"}, 500


@router.delete("/{organization_id}/{credential_id}")
async def delete_credentials(
    organization_id: str,
    credential_id: str,
    db=Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Delete credentials for an organization.
    """
    logger.info(
        f"Deleting credentials for organization: {organization_id}, user: {user.id}"
    )
    try:
        with db as session:
            membership = ensure_org_membership(session, organization_id, user)
            ensure_org_permissions(
                session,
                membership,
                [Permissions.WRITE],
            )

            organization_store = OrganizationCredentialsStore(session)
            organization_store.deactivate_organization_credential(
                organization_id, credential_id
            )
            return {"message": "Credentials deleted successfully"}
    except HTTPException as e:
        logger.error(f"Error deleting credentials: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Failed to delete credentials"}, 500
