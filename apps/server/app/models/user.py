from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import EmailStr

from app.models.enums import UserType


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(index=True, unique=True, nullable=False)
    display_name: str = Field(default=None, nullable=True)
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    bio: Optional[str] = Field(default=None, nullable=True)
    type: UserType = Field(default=UserType.HUMAN, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)


class UserPreference(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    theme: str = Field(default="light", nullable=False)
    timezone: str = Field(default="UTC", nullable=True)
    language: str = Field(default="en", nullable=True)
    show_notification: bool = Field(default=True, nullable=False)

    user_id: int = Field(default=None, nullable=False, foreign_key="user.id")
