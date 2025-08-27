from cuid import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi import HTTPException

from app.core.auth.m2m_auth import create_organization_credentials
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
    organization_id: str
    client_secret: str
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
            credentials = create_organization_credentials(
                payload.organization_id,
                secret,
                expires_at,
                session,
            )

            return OrgCredResponse(
                organization_id=credentials.organization_id,
                client_secret=secret,
                expires_at=expires_at.isoformat(),
            )
    except HTTPException as e:
        logger.error(f"Error generating credentials: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Failed to generate credentials"}, 500
