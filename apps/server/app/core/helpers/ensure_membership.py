from fastapi import HTTPException
from sqlmodel import Session, null, select

from app.models.sql_model import OrganizationMember, User


def ensure_org_membership(
    session: Session, org_id: str, user: User
) -> OrganizationMember:
    """Check if the user is a member of the organization."""
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user.id,
            OrganizationMember.left_at == null(),
        )
    ).first()

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You don't have access to this organization",
        )
    return membership
