from sqlmodel import SQLModel, Field, Relationship
from cuid import cuid

from app.models.organization import Organization, OrganizationMember


class Role(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    is_default: bool = Field(default=False, nullable=False)
    is_system: bool = Field(default=False, nullable=False)
    level: int = Field(default=0, nullable=False)

    organization: Organization = Relationship(
        back_populates="roles", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    members: list[OrganizationMember] = Relationship(
        back_populates="role", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class RolePermission(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    role_id: str = Field(foreign_key="organizationroles.id", nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    resource: str = Field(index=True, nullable=False)
    action: str = Field(index=True, nullable=False)
    role: Role = Relationship(back_populates="permissions")
    created_at: str = Field(default=None, nullable=False)

    role: Role = Relationship(
        back_populates="permissions",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
