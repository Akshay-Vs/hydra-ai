# app/models/role.py
from __future__ import annotations
from typing import TYPE_CHECKING  # Enables forward references
from sqlmodel import SQLModel, Field, Relationship
from cuid import cuid


if TYPE_CHECKING:
    from app.models.organization import (
        Organization,
        OrganizationInvite,
        OrganizationMember,
    )
    from app.models.organization import OrganizationAgent


class Role(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id", nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    is_default: bool = Field(default=False, nullable=False)
    is_system: bool = Field(default=False, nullable=False)
    level: int = Field(default=0, nullable=False)

    # Relationships
    organization: Organization = Relationship(back_populates="roles")
    members: list[OrganizationMember] = Relationship(back_populates="role")
    agent_assignments: list[OrganizationAgent] = Relationship(back_populates="role")

    permissions: list[RolePermission] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        },  # Role owns permissions
    )
    invites: list[OrganizationInvite] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    role_id: str = Field(
        foreign_key="role.id", nullable=False
    )  # Fixed foreign key reference
    name: str = Field(index=True, nullable=False)
    description: str = Field(default=None, nullable=True)
    resource: str = Field(index=True, nullable=False)
    action: str = Field(index=True, nullable=False)
    created_at: str = Field(default=None, nullable=False)

    # Relationship
    role: Role = Relationship(back_populates="permissions")
