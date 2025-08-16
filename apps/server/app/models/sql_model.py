from sqlalchemy import Nullable
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import Enum as PyEnum
from cuid import cuid

from app.models.enums import AgentStatus, Permissions


# Enums for status fields
class InvitationStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class MembershipStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    clerk_id: str = Field(index=True, unique=True)
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    # Relationships - use simple type hints without Mapped
    preferences: Optional["UserPreference"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    organizations: List["OrganizationMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )
    sent_invites: List["OrganizationInvite"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationInvite.sender_id]"},
    )


class UserPreference(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    user_id: str = Field(foreign_key="user.id", unique=True)
    theme: Optional[str] = Field(default="light")
    timezone: Optional[str] = Field(default="UTC")
    language: Optional[str] = Field(default="en")
    show_notification: Optional[bool] = Field(default=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="preferences")


class Organization(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    # Relationships
    members: List["OrganizationMember"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    invites: List["OrganizationInvite"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    agents: List["OrganizationAgent"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    roles: List["Role"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrganizationMember(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(foreign_key="user.id")
    role_id: str = Field(foreign_key="role.id")

    joined_at: str
    left_at: Optional[str] = None
    granted_by: Optional[str] = Field(default=None, foreign_key="user.id")
    role_expires_at: Optional[str] = None

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(
        back_populates="organizations",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )
    role: Optional["Role"] = Relationship(back_populates="members")
    granter: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.granted_by]"}
    )


class OrganizationInvite(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    sender_id: str = Field(foreign_key="user.id")
    recipient_email: str = Field(index=True)
    role_id: str = Field(foreign_key="role.id")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    message: Optional[str] = None
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="invites")
    sender: Optional["User"] = Relationship(
        back_populates="sent_invites",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationInvite.sender_id]"},
    )
    role: Optional["Role"] = Relationship(back_populates="invites")


class OrganizationAgent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    agent_id: str = Field(foreign_key="agent.id")
    role_id: str = Field(foreign_key="role.id")
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE)
    added_at: str
    removed_at: Optional[str] = None
    role_expires_at: Optional[str] = None

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="agents")
    agent: Optional["Agent"] = Relationship(back_populates="organization_agents")
    role: Optional["Role"] = Relationship(back_populates="agent_assignments")


class Role(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    name: str = Field(index=True)
    description: Optional[str] = None
    is_default: bool = Field(default=False)
    is_system: bool = Field(default=False)
    level: int = Field(default=0)

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="roles")
    members: List["OrganizationMember"] = Relationship(back_populates="role")
    agent_assignments: List["OrganizationAgent"] = Relationship(back_populates="role")
    permissions: List["RolePermission"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    invites: List["OrganizationInvite"] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    role_id: str = Field(foreign_key="role.id")
    action: Permissions = Field(index=True, nullable=False)
    created_at: str

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="permissions")


class Agent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    agent_status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    is_system: bool = Field(default=False)
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    # Relationships
    organization_agents: List["OrganizationAgent"] = Relationship(
        back_populates="agent", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    config: Optional["AgentConfig"] = Relationship(
        back_populates="agent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )


class AgentConfig(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", unique=True)
    model: str
    version: str
    system_prompt: Optional[str] = None
    created_at: str
    updated_at: str

    # Relationships
    agent: Optional["Agent"] = Relationship(back_populates="config")
