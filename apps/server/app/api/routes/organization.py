from fastapi import APIRouter, Depends
from sqlmodel import null, select

from app.core.decorators.get_user import get_current_user
from app.models.sql_model import Organization, OrganizationMember, User
from app.services.database_service import get_session
from app.utils.logging import create_logger


router = APIRouter()
logger = create_logger(__name__)


@router.get("/")
async def list_organizations(user: User = Depends(get_current_user)):
    try:
        with get_session() as session:
            # Get all organizations where user is a member
            orgs = session.exec(
                select(Organization)
                .join(OrganizationMember)
                .where(
                    OrganizationMember.user_id == user.id,
                    OrganizationMember.left_at == null(),
                )
                .order_by(Organization.name)
            ).all()

            if not orgs:
                logger.info(f"No organizations found for user {user.id}.")
                return {"message": "No organizations found"}

            return orgs
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        return {"error": "Failed to fetch organizations"}, 500


@router.get("/{org_id}")
async def get_organization(org_id: str, user: User = Depends(get_current_user)):
    if not org_id:
        return {"error": "Organization ID is required"}, 400

    try:
        with get_session() as session:
            org = session.exec(
                select(Organization)
                .join(OrganizationMember)
                .where(
                    Organization.id == org_id,
                    OrganizationMember.user_id == user.id,
                    OrganizationMember.left_at == null(),
                )
            ).one_or_none()

            if not org:
                return {"error": "Organization not found"}, 404

            return org
    except Exception as e:
        logger.error(f"Error fetching organization: {e}")
        return {"error": "Failed to fetch organization"}, 500
