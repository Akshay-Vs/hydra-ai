from fastapi import APIRouter, HTTPException, Request, status
from sqlmodel import null, select

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
from app.utils.now import now


router = APIRouter()
logger = create_logger(__name__)


@router.post("/")
async def initialize_user(request: Request):
    logger.info("Initializing user...")
    try:
        if not settings.clerk_secret_key:
            raise ValueError(
                "Clerk secret key is not configured",
                {"error_code": "CONFIG_ERROR", "status_code": 500},
            )

        authenticator = ClerkAuth(settings.clerk_secret_key)
        clerk_user = await authenticator.authenticate_HTTP(request)

        if not clerk_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Clerk user not found",
            )

        logger.info(f"Authenticated Clerk user: {clerk_user.id}")

        with get_session() as session:
            _now = now()

            # Check if user already exists
            existing_user = existing_user = session.exec(
                select(User).where(User.clerk_id == clerk_user.id)
            ).one_or_none()
            print("Existing User: ", existing_user)

            if existing_user:
                logger.debug(f"User already exists with Clerk ID: {clerk_user.id}")
                user_orgs = session.exec(
                    select(Organization)
                    .join(OrganizationMember)
                    .where(
                        OrganizationMember.user_id == existing_user.id,
                        Organization.deleted_at == null(),
                        OrganizationMember.left_at == null(),
                    )
                ).all()
                return {
                    "id": existing_user.id,
                    "clerk_id": existing_user.clerk_id,
                    "organization_id": user_orgs[0].id,
                    "created_at": existing_user.created_at,
                }

            # Create new user with clerk user id
            user = User(clerk_id=clerk_user.id, created_at=_now, updated_at=_now)
            session.add(user)
            session.flush()
            # Create Organization
            organization = Organization(
                name="onboarding",
                description="onboarding organization",
                created_at=_now,
                updated_at=_now,
            )
            session.add(organization)
            session.flush()
            # Create Role
            role = Role(
                name="owner",
                description="organization owner",
                is_system=True,
                is_default=True,
                level=10,
                organization_id=organization.id,
            )
            session.add(role)
            session.flush()

            # Initialize user preference
            user_preference = UserPreference(user_id=user.id)
            session.add(user_preference)

            # Permission
            permission = RolePermission(
                role_id=role.id,
                action=Permissions.WRITE,
                created_at=_now,
            )
            session.add(permission)

            # Join Organization and User
            org_member = OrganizationMember(
                organization_id=organization.id,
                user_id=user.id,
                role_id=role.id,
                joined_at=_now,
            )
            session.add(org_member)

            session.commit()

            return {
                "id": user.id,
                "clerk_id": clerk_user.id,
                "organization_id": organization.id,
                "created_at": _now,
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
