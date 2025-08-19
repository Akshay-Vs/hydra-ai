from typing import List
from fastapi import HTTPException
from sqlmodel import Session, or_, select

from app.models.enums import Permissions
from app.models.sql_model import OrganizationMember, RolePermission


def ensure_org_permissions(
    session: Session,
    membership: OrganizationMember,
    required_permissions: List[Permissions],
):
    """
    Check if a user has any of the required permissions based on their role membership.

    Args:
        session: Database session
        membership: OrganizationMember instance containing user's role info
        required_permissions: List of permissions to check for

    Returns:
        bool: True if user has at least one of the required permissions, False otherwise
    """
    if not membership or not membership.role_id:
        return False

    if not required_permissions:
        return False

    permission_conditions = [
        RolePermission.action == perm for perm in required_permissions
    ]

    permission = session.exec(
        select(RolePermission).where(
            RolePermission.role_id == membership.role_id, or_(*permission_conditions)
        )
    ).first()

    if not permission:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You don't have the required permissions for this action",
        )
    return True
