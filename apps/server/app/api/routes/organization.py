from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import null, select

from app.core.helpers.get_user import get_current_user
from app.models.enums import Permissions
from app.models.sql_model import (
    Organization,
    OrganizationMember,
    Role,
    RolePermission,
    User,
)
from app.services.database_service import get_session
from app.utils.logging import create_logger
from app.utils.now import now


router = APIRouter()
logger = create_logger(__name__)


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None


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
                    Organization.deleted_at == null(),
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


@router.post("/")
async def create_organization(
    org_data: OrganizationCreate, user: User = Depends(get_current_user)
):
    if not org_data.name:
        return {"error": "Organization name is required"}, 400
    try:
        _now = now()
        with get_session() as session:
            new_org = Organization(
                name=org_data.name,
                description=org_data.description,
                created_at=_now,
                updated_at=_now,
            )
            session.add(new_org)
            session.commit()
            session.refresh(new_org)

            # Create Role and Permission
            role = Role(
                name="owner",
                description="organization owner",
                is_system=True,
                is_default=True,
                level=10,
                organization_id=new_org.id,
            )
            session.add(role)

            # Permission
            permission = RolePermission(
                role_id=role.id, action=Permissions.WRITE, created_at=_now
            )
            session.add(permission)

            # Add the user as a member of the new organization
            member = OrganizationMember(
                organization_id=new_org.id,
                user_id=user.id,
                joined_at=new_org.created_at,
                role_id=role.id,
            )
            session.add(member)
            session.commit()

            logger.info(f"Organization {new_org.id} created by user {user.id}.")
            return new_org
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        return {"error": "Failed to create organization"}, 500


@router.put("/{org_id}")
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    user: User = Depends(get_current_user),
):
    if not org_id:
        return {"error": "Organization ID is required"}, 400

    try:
        with get_session() as session:
            org = session.exec(
                select(Organization).where(Organization.id == org_id)
            ).one_or_none()

            if not org:
                return {"error": "Organization not found"}, 404

            # Check if user is a member of the organization
            member = session.exec(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user.id,
                    OrganizationMember.left_at == null(),
                )
            ).one_or_none()

            if not member:
                return {"error": "User is not a member of this organization"}, 403

            # Update organization details
            if org_data.name:
                org.name = org_data.name
            if org_data.description:
                org.description = org_data.description
            if org_data.website:
                org.website = org_data.website
            if org_data.avatar_url:
                org.avatar_url = org_data.avatar_url

            org.updated_at = now()
            session.add(org)
            session.commit()

            logger.info(f"Organization {org_id} updated by user {user.id}.")
            return org
    except Exception as e:
        logger.error(f"Error updating organization: {e}")
        return {"error": "Failed to update organization"}, 500


@router.delete("/{org_id}")
async def delete_organization(org_id: str, user: User = Depends(get_current_user)):
    if not org_id:
        return {"error": "Organization ID is required"}, 400

    try:
        with get_session() as session:
            org = session.exec(
                select(Organization).where(Organization.id == org_id)
            ).one_or_none()

            if not org:
                return {"error": "Organization not found"}, 404

            # Check if user is a member of the organization
            member = session.exec(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user.id,
                    OrganizationMember.left_at == null(),
                )
            ).one_or_none()

            if not member:
                return {"error": "User is not a member of this organization"}, 403

            # Soft delete the organization
            org.deleted_at = now()
            session.add(org)
            session.commit()

            logger.info(f"Organization {org_id} deleted by user {user.id}.")
            return {"message": "Organization deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting organization: {e}")
        return {"error": "Failed to delete organization"}, 500
