from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import null, select

from app.core.helpers.get_user import get_current_user
from app.core.helpers.ensure_membership import ensure_org_membership
from app.core.helpers.ensure_permissions import ensure_org_permissions
from app.models.enums import Permissions
from app.models.sql_model import (
    OrganizationInvite,
    OrganizationMember,
    RolePermission,
    User,
)
from app.services.database_service import get_session
from app.utils.logging import create_logger
from app.utils.now import now


router = APIRouter()
logger = create_logger(__name__)


class OrganizationInviteCreate(BaseModel):
    recipient_email: str
    role_id: str
    message: Optional[str] = None
    expires_at: Optional[str] = None


@router.get("/{org_id}/invites")
async def list_organization_invites(
    org_id: str, user: User = Depends(get_current_user)
):
    """
    List all invites for a specific organization.
    """
    try:
        with get_session() as session:
            # Check if user has permission to view invites
            # First, check if user is a member of the organization

            membership = ensure_org_membership(session, org_id, user)

            # Check if the user's role has write permissions
            ensure_org_permissions(
                session,
                membership,
                [Permissions.READ, Permissions.WRITE],
            )

            # If user has permissions, fetch the invites
            invites = session.exec(
                select(OrganizationInvite).where(
                    OrganizationInvite.organization_id == org_id,
                )
            ).all()

            if not invites:
                logger.info(f"No invites found for organization {org_id}.")
                return {"message": "No invites found", "data": []}

            return {"data": invites, "count": len(invites)}

    except HTTPException as http_exc:
        logger.error(f"HTTP error fetching organization invites: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Error fetching organization invites: {e}")
        return {"error": "Failed to fetch organization invites"}, 500


@router.post("/{org_id}/invites")
async def create_organization_invite(
    org_id: str,
    invite_data: OrganizationInviteCreate,
    user: User = Depends(get_current_user),
):
    """
    Create a new invite for an organization.
    """
    try:
        with get_session() as session:
            _now = now()
            # Check if user is a member of the organization
            membership = session.exec(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user.id,
                    OrganizationMember.left_at == null(),
                )
            ).first()

            if not membership:
                logger.warning(
                    f"User {user.id} is not a member of organization {org_id}"
                )
                return {
                    "error": "Access denied: User is not a member of this organization"
                }, 403

            # Check if the user's role has write permissions
            has_write_permission = session.exec(
                select(RolePermission).where(
                    RolePermission.role_id == membership.role_id,
                    RolePermission.action == Permissions.WRITE,
                )
            ).first()

            if not has_write_permission:
                logger.warning(
                    f"User {user.id} does not have write permissions for organization {org_id}"
                )
                return {"error": "Access denied: Insufficient permissions"}, 403

            # Create the invite
            invite = OrganizationInvite(
                organization_id=org_id,
                sender_id=user.id,
                recipient_email=invite_data.recipient_email,
                role_id=invite_data.role_id,
                message=invite_data.message,
                created_at=_now,
                updated_at=_now,
                expires_at=invite_data.expires_at or None,
            )

            session.add(invite)
            session.commit()
            session.refresh(invite)

            logger.info(f"Invite created successfully for organization {org_id}.")
            return {"data": invite, "message": "Invite created successfully"}

    except Exception as e:
        logger.error(f"Error creating organization invite: {e}")
        return {"error": "Failed to create organization invite"}, 500


@router.delete("/{org_id}/invites/{invite_id}")
async def delete_organization_invite(
    org_id: str,
    invite_id: str,
    user: User = Depends(get_current_user),
):
    """
    Delete an invite for an organization.
    """
    try:
        with get_session() as session:
            # Check if user is a member of the organization
            membership = ensure_org_membership(session, org_id, user)

            # Check if the user's role has write permissions
            ensure_org_permissions(
                session,
                membership,
                [Permissions.WRITE],
            )

            # Fetch the invite to be deleted
            invite = session.exec(
                select(OrganizationInvite).where(
                    OrganizationInvite.id == invite_id,
                    OrganizationInvite.organization_id == org_id,
                )
            ).first()

            if not invite:
                logger.warning(
                    f"Invite {invite_id} not found in organization {org_id}."
                )
                return {"error": "Invite not found"}, 404

            session.delete(invite)
            session.commit()

            logger.info(
                f"Invite {invite_id} deleted successfully from organization {org_id}."
            )
            return {"message": "Invite deleted successfully"}

    except HTTPException as http_exc:
        logger.error(f"HTTP error deleting organization invite: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Error deleting organization invite: {e}")
        return {"error": "Failed to delete organization invite"}, 500
