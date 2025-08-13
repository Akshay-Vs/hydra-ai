from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from cuid import cuid
from sqlmodel import Field, Relationship, SQLModel
from app.models.enums import InvitationStatus, MembershipStatus

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user import User
    from app.models.agent import Agent


class Organization(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    avatar_url: str = Field(default=None, nullable=True)
    website: str = Field(default=None, nullable=True)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    deleted_at: str = Field(default=None, nullable=True)

    # Relationships
    members: list[OrganizationMember] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    agents: list[OrganizationAgent] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    invites: list[OrganizationInvite] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    roles: list[Role] = Relationship(  # Forward reference as string
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrganizationMember(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    role_id: str = Field(foreign_key="role.id", nullable=False)  # Fixed foreign key
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE, nullable=False)
    joined_at: str = Field(default=None, nullable=False)
    left_at: str = Field(default=None, nullable=True)
    granted_by: str = Field(foreign_key="user.id", nullable=True)
    role_expires_at: Optional[str] = Field(default=None, nullable=True)

    # Relationships - no cascade on child relationships
    organization: Organization = Relationship(back_populates="members")
    user: User = Relationship(back_populates="organizations")
    role: Role = Relationship(back_populates="members")  # Forward reference


class OrganizationInvite(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    sender_id: str = Field(foreign_key="user.id", nullable=False)
    recipient_email: str = Field(index=True, nullable=False)
    role_id: str = Field(foreign_key="role.id", nullable=False)  # Fixed foreign key
    status: InvitationStatus = Field(
        default=InvitationStatus.PENDING, nullable=False
    )  # Fixed enum type
    message: str = Field(default=None, nullable=True)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    expires_at: Optional[str] = Field(default=None, nullable=True)

    # Relationships - no cascade on child relationships
    organization: Organization = Relationship(back_populates="invites")
    sender: User = Relationship(back_populates="sent_invites")
    role: Role = Relationship(back_populates="invites")  # Forward reference


class OrganizationAgent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    agent_id: str = Field(foreign_key="agent.id", nullable=False)
    role_id: str = Field(foreign_key="role.id", nullable=False)
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE, nullable=False)
    added_at: str = Field(default=None, nullable=False)
    removed_at: Optional[str] = Field(default=None, nullable=True)
    role_expires_at: Optional[str] = Field(default=None, nullable=True)

    # Relationships
    organization: Organization = Relationship(back_populates="agents")
    agent: Agent = Relationship(back_populates="organization_agents")
    role: Role = Relationship(back_populates="agent_assignments")
