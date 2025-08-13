from __future__ import annotations
from enum import unique
from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field
from cuid import cuid

from app.models.enums import AgentStatus

if TYPE_CHECKING:
    from app.models.organization import OrganizationAgent


class Agent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    agent_status: AgentStatus = Field(default=AgentStatus.ACTIVE, nullable=False)
    is_system: bool = Field(default=False, nullable=False)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
    deleted_at: Optional[str] = Field(default=None, nullable=True)

    # Relationships
    organizations: list[OrganizationAgent] = Relationship(
        back_populates="agent", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    config: Optional["AgentConfig"] = Relationship(
        back_populates="agent",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },  # One-to-one relationship
    )


class AgentConfig(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", nullable=False, unique=True)
    model: str = Field(default=None, nullable=False)
    version: str = Field(default=None, nullable=False)
    system_prompt: str = Field(default=None, nullable=True)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)

    # Relationships
    agent: Optional[Agent] = Relationship(back_populates="config")
