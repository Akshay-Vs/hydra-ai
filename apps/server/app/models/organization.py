from cuid import cuid
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import InvitationStatus, MembershipStatus
from app.models.role import Role
from app.models.user import User


class Organization(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    avatar_url: str = Field(default=None, nullable=True)
    website: str = Field(default=None, nullable=True)

    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    deleted_at: str = Field(default=None, nullable=True)

    members: list["OrganizationMember"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    invites: list["OrganizationInvite"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    roles: list["Role"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrganizationMember(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    role_id: str = Field(foreign_key="organizationroles.id", nullable=False)
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE, nullable=False)

    joined_at: str = Field(default=None, nullable=False)
    left_at: str = Field(default=None, nullable=True)

    granted_by: str = Field(foreign_key="user.id", nullable=True)
    role_expires_at: str = Field(default=None, nullable=True)

    organization: Organization = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    user: User = Relationship(
        back_populates="organizations",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    role: "Role" = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrganizationInvite(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    sender_id: str = Field(foreign_key="user.id", nullable=False)
    recipient_email: str = Field(index=True, nullable=False)
    role_id: str = Field(foreign_key="organizationroles.id", nullable=False)
    status: MembershipStatus = Field(default=InvitationStatus.PENDING, nullable=False)
    message: str = Field(default=None, nullable=True)

    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    expires_at: str = Field(default=None, nullable=True)

    organization: Organization = Relationship(
        back_populates="invites",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    sender: User = Relationship(
        back_populates="sent_invites",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    role: Role = Relationship(
        back_populates="invites",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
