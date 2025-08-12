from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from app.models.user import User, UserPreference
from app.services.database_service import get_session


router = APIRouter()


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    theme: str
    timezone: str
    language: str
    show_notification: bool


@router.post("/")
async def create_user(payload: UserCreateRequest):
    with get_session() as session:
        now = datetime.now(timezone.utc).isoformat()
        user = User(
            username=payload.username,
            email=payload.email,
            display_name=payload.display_name,
            avatar_url=payload.avatar_url,
            bio=payload.bio,
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
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "theme": user_preference.theme,
            "timezone": user_preference.timezone,
            "language": user_preference.language,
            "show_notification": user_preference.show_notification,
        }
