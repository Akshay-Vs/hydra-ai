# TODO: Add authorization and authentication
# TODO: Add decorators to check permissions and authorization

from datetime import datetime, timezone
from fastapi import APIRouter

from app.core.types.user_type import UserCreateRequest, UserPreferenceUpdateRequest
from app.models.sql_model import User, UserPreference
from app.services.database_service import get_session
from app.utils.logging import create_logger


router = APIRouter()
logger = create_logger(__name__)


@router.post("/preferencee")
async def create_user(payload: UserCreateRequest):
    try:
        with get_session() as session:
            now = datetime.now(timezone.utc).isoformat()
            user = User(
                clerk_id=payload.clerk_id,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            session.flush()

            user_preference = UserPreference(
                user_id=user.id,
                theme=payload.theme,
                timezone=payload.timezone,
                language=payload.language,
                show_notification=payload.show_notification,
            )
            session.add(user_preference)
            session.commit()

            return {
                "id": user.id,
                "theme": user_preference.theme,
                "timezone": user_preference.timezone,
                "language": user_preference.language,
                "show_notification": user_preference.show_notification,
            }

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {"error": "Failed to create user"}, 500


@router.get("/{user_id}")
async def get_user(user_id: str):
    try:
        with get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found"}, 404

            user_preference = session.get(UserPreference, user_id)
            return {
                "id": user.id,
                "theme": user_preference.theme if user_preference else None,
                "timezone": user_preference.timezone if user_preference else None,
                "language": user_preference.language if user_preference else None,
                "show_notification": (
                    user_preference.show_notification if user_preference else None
                ),
            }
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        return {"error": "Failed to retrieve user"}, 500


@router.put("/{user_id}")
async def update_user(user_id: str, payload: UserPreferenceUpdateRequest):
    try:
        with get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found"}, 404

            user.avatar_url = payload.avatar_url
            user.bio = payload.bio
            user.updated_at = datetime.now(timezone.utc).isoformat()

            user_preference = session.get(UserPreference, user_id)

            if not user_preference:
                user_preference = UserPreference(
                    user_id=user.id,
                    theme=payload.theme,
                    timezone=payload.timezone,
                    language=payload.language,
                    show_notification=payload.show_notification,
                )
                session.add(user_preference)
            else:
                user_preference.theme = payload.theme
                user_preference.timezone = payload.timezone
                user_preference.language = payload.language
                user_preference.show_notification = payload.show_notification

            session.commit()

            return {
                "id": user.id,
                "theme": user_preference.theme,
                "timezone": user_preference.timezone,
                "language": user_preference.language,
                "show_notification": user_preference.show_notification,
            }
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return {"error": "Failed to update user"}, 500


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    try:
        with get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return {"error": "User not found"}, 404

            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return {"error": "Failed to delete user"}, 500
