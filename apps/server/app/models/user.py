# app/models/user.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr
from cuid import cuid

if TYPE_CHECKING:
    from app.models.organization import OrganizationInvite, OrganizationMember


class User(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(index=True, unique=True, nullable=False)
    display_name: Optional[str] = Field(default=None, nullable=True)
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    bio: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    deleted_at: Optional[str] = Field(default=None, nullable=True)

    # One-to-one relationship with preferences
    preferences: Optional[UserPreference] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )

    # One-to-many relationships
    organizations: list[OrganizationMember] = Relationship(back_populates="user")

    sent_invites: list[OrganizationInvite] = Relationship(back_populates="sender")


class UserPreference(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False, unique=True)
    theme: str = Field(default="light", nullable=False)
    timezone: str = Field(default="UTC", nullable=True)
    language: str = Field(default="en", nullable=True)
    show_notification: bool = Field(default=True, nullable=False)

    # Back-reference to user
    user: User = Relationship(back_populates="preferences")
