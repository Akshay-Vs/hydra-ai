from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, status

from app.config.settings import settings
from app.core.auth.clerk_auth import ClerkAuth
from app.models.enums import Permissions
from app.models.sql_model import (
    Organization,
    OrganizationMember,
    Role,
    RolePermission,
    User,
    UserPreference,
)
from app.services.database_service import get_session
from app.utils.logging import create_logger


router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def create_user(request: Request):
    try:
        if not settings.clerk_secret_key:
            raise ValueError(
                "Clerk secret key is not configured",
                {"error_code": "CONFIG_ERROR", "status_code": 500},
            )

        authenticator = ClerkAuth(settings.clerk_secret_key)
        clerk_user = await authenticator.authenticate_HTTP(request)
        with get_session() as session:
            now = datetime.now(timezone.utc).isoformat()

            # Create new user with clerk user id
            user = User(clerk_id=clerk_user.id, created_at=now, updated_at=now)
            session.add(user)

            # Initialize user preference
            user_preference = UserPreference(user_id=user.id)
            session.add(user_preference)

            # Create Organization
            organization = Organization(
                name="onboarding",
                description="onbooarding organization",
                created_at=now,
                updated_at=now,
            )
            session.add(organization)

            # Create Roles and Permission
            role = Role(
                name="owner",
                description="organization owner",
                is_system=True,
                is_default=True,
                level=10,
                organization_id=organization.id,
            )
            session.add(role)

            # Permission
            permission = RolePermission(
                role_id=role.id, action=Permissions.WRITE, created_at=now
            )
            session.add(permission)

            # Join Organization and User
            org_member = OrganizationMember(
                organization_id=organization.id,
                user_id=user.id,
                role_id=role.id,
                joined_at=now,
            )
            session.add(org_member)

            session.commit()

            return {
                "id": user.id,
                "clerk_id": clerk_user.id,
                "organization_id": organization.id,
                "created_at": now,
            }

    except HTTPException as e:
        logger.error(f"Authorization error: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )
