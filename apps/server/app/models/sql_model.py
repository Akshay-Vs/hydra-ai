from datetime import datetime
from operator import index
from sqlmodel import JSON, Column, Index, SQLModel, Field, Relationship, String, Text
from typing import Any, Dict, List, Optional
from cuid import cuid

from app.models.enums import (
    AgentStatus,
    ExecutionStage,
    InvitationStatus,
    LogLevelEnum,
    MembershipStatus,
    MemoryType,
    Permissions,
    SessionStatus,
    SeverityEnum,
    StatusEnum,
)
from app.models.mixins import TimestampMixin


def now():
    return datetime.now


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    clerk_id: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    deleted_at: Optional[datetime] = None

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
    granted_memberships: List["OrganizationMember"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.granted_by]"}
    )


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True)
    theme: Optional[str] = Field(default="light")
    timezone: Optional[str] = Field(default="UTC")
    language: Optional[str] = Field(default="en")
    show_notification: Optional[bool] = Field(default=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="preferences")


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    deleted_at: Optional[datetime] = None

    # Relationships
    members: List["OrganizationMember"] = Relationship(back_populates="organization")
    invites: List["OrganizationInvite"] = Relationship(back_populates="organization")
    credentials: List["OrganizationCredential"] = Relationship(
        back_populates="organization"
    )
    agents: List["OrganizationAgent"] = Relationship(back_populates="organization")
    roles: List["Role"] = Relationship(back_populates="organization")
    incidents: List["Incident"] = Relationship(back_populates="organization")
    events: List["Event"] = Relationship(back_populates="organization")
    traces: List["Trace"] = Relationship(back_populates="organization")
    sessions: List["Session"] = Relationship(back_populates="organization")
    metrics: List["Metric"] = Relationship(back_populates="organization")
    logs: List["Log"] = Relationship(back_populates="organization")
    agent_memories: List["AgentMemory"] = Relationship(back_populates="organization")
    execution_logs: List["AgentExecutionLog"] = Relationship(
        back_populates="organization"
    )


class OrganizationMember(SQLModel, table=True):
    __tablename__ = "organization_members"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id")
    user_id: str = Field(foreign_key="users.id")
    role_id: str = Field(foreign_key="roles.id")

    joined_at: datetime = Field(default_factory=now)
    left_at: Optional[datetime] = Field(default=None)
    granted_by: Optional[str] = Field(default=None, foreign_key="users.id")
    role_expires_at: Optional[datetime] = None

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
    __tablename__ = "organization_invites"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id")
    sender_id: str = Field(foreign_key="users.id")
    recipient_email: str = Field(index=True)
    role_id: str = Field(foreign_key="roles.id")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    expires_at: Optional[datetime] = None

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="invites")
    sender: Optional["User"] = Relationship(
        back_populates="sent_invites",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationInvite.sender_id]"},
    )
    role: Optional["Role"] = Relationship(back_populates="invites")


class OrganizationCredential(TimestampMixin, table=True):
    __tablename__ = "organization_credentials"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id")
    secret_hash: str = Field(nullable=False, index=True)
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None)

    # composite index
    __table_args__ = (Index("idx_org_active", "organization_id", "is_active"),)

    organization: Optional["Organization"] = Relationship(back_populates="credentials")


class Agent(SQLModel, table=True):
    __tablename__ = "agents"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    agent_status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    is_system: bool = Field(default=False)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    deleted_at: Optional[datetime] = None

    # Relationships
    organization_agents: List["OrganizationAgent"] = Relationship(
        back_populates="agent"
    )
    config: Optional["AgentConfig"] = Relationship(
        back_populates="agent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    incidents: List["Incident"] = Relationship(back_populates="assigned_agent")
    memories: List["AgentMemory"] = Relationship(back_populates="agent")
    execution_logs: List["AgentExecutionLog"] = Relationship(back_populates="agent")


class AgentConfig(SQLModel, table=True):
    __tablename__ = "agent_configs"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    agent_id: str = Field(foreign_key="agents.id", unique=True)
    model: str
    version: str
    system_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)

    # Relationships
    agent: Optional["Agent"] = Relationship(back_populates="config")


class OrganizationAgent(SQLModel, table=True):
    __tablename__ = "organization_agents"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id")
    agent_id: str = Field(foreign_key="agents.id")
    role_id: str = Field(foreign_key="roles.id")
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE)
    added_at: datetime = Field(default_factory=now)
    removed_at: Optional[datetime] = None
    role_expires_at: Optional[datetime] = None

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="agents")
    agent: Optional["Agent"] = Relationship(back_populates="organization_agents")
    role: Optional["Role"] = Relationship(back_populates="agent_assignments")


class Role(SQLModel, table=True):
    __tablename__ = "roles"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organizations.id")
    name: str = Field(index=True)
    description: Optional[str] = None
    is_default: bool = Field(default=False)
    is_system: bool = Field(default=False)
    level: int = Field(default=0)

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="roles")
    members: List["OrganizationMember"] = Relationship(back_populates="role")
    agent_assignments: List["OrganizationAgent"] = Relationship(back_populates="role")
    permissions: List["RolePermission"] = Relationship(back_populates="role")
    invites: List["OrganizationInvite"] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    role_id: str = Field(foreign_key="roles.id")
    action: Permissions = Field(index=True)
    created_at: datetime = Field(default_factory=now)

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="permissions")


###########################################################################
############################## SEESSION DATA ##############################
###########################################################################
class Session(TimestampMixin, table=True):
    __tablename__ = "sessions"  # type: ignore

    id: str = Field(default_factory=cuid, primary_key=True)
    token_jti: str = Field(unique=True, index=True, max_length=255)
    organization_id: str = Field(foreign_key="organizations.id", index=True)
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, index=True)
    expires_at: datetime = Field(index=True)
    last_used_at: Optional[datetime] = Field(default=None)
    ip_address: Optional[str] = Field(default=None, max_length=45)

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="sessions")


# Revoked tokens - for immediate token revocation
class RevokedToken(SQLModel, table=True):
    __tablename__ = "revoked_tokens"  # type: ignore

    token_jti: str = Field(primary_key=True, max_length=255)
    organization_id: str = Field(
        foreign_key="organizations.id", index=True
    )  # Fixed: organizations table
    revoked_at: datetime = Field(default_factory=now)
    expires_at: datetime = Field(index=True)

    # Relationships
    organization: Optional["Organization"] = Relationship()


###########################################################################
##################### HTAP-NEEDED - HIGH VOLUME DATA ######################
###########################################################################


class Metric(SQLModel, table=True):
    """
    HIGH VOLUME: Millions of metrics per day
    HTAP NEEDED: Real-time anomaly detection while ingesting
    """

    __tablename__ = "metrics"  # type: ignore
    __table_args__ = (
        Index("idx_service_time", "service_name", "timestamp"),
        Index("idx_metric_time", "metric_name", "timestamp"),
        Index("idx_anomaly_score", "anomaly_score"),
        # TiDB-specific: TiFlash replica
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    id: str = Field(primary_key=True)
    metric_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=now(), index=True)
    service_name: str = Field(max_length=128, index=True)
    metric_name: str = Field(max_length=64)
    value: float
    labels: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    unit: Optional[str] = Field(default=None, max_length=32)
    anomaly_score: float = Field(default=0.0)
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="metrics")


class Log(SQLModel, table=True):
    """
    HIGH VOLUME: Millions of logs per day
    HTAP NEEDED: Real-time log analysis and semantic search
    """

    __tablename__ = "logs"  # type: ignore
    __table_args__ = (
        Index("idx_service_time", "service_name", "timestamp"),
        Index("idx_level_time", "level", "timestamp"),
        Index("idx_trace", "trace_id", "span_id"),
        # Full-text search
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    id: str = Field(primary_key=True)
    log_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=now(), index=True)
    service_name: str = Field(max_length=128, index=True)
    level: LogLevelEnum
    message: str = Field(sa_column=Column(Text))
    trace_id: Optional[str] = Field(default=None, max_length=64)
    span_id: Optional[str] = Field(default=None, max_length=64)
    structured_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    # Vector embedding for semantic search (1536 dimensions)
    embedding: Optional[str] = Field(default=None, sa_column=Column(String(8192)))
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="logs")


class Incident(SQLModel, table=True):
    """
    MEDIUM VOLUME: Thousands of incidents
    HTAP NEEDED: Real-time pattern matching and similarity search
    """

    __tablename__ = "incidents"  # type: ignore
    __table_args__ = (
        Index("idx_timestamp_service", "timestamp", "service_name"),
        Index("idx_status_severity", "status", "severity"),
        Index("idx_confidence", "confidence_score"),
        Index("idx_organization", "organization_id"),
        Index("idx_assigned_agent", "assigned_agent_id"),
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    id: str = Field(primary_key=True)
    incident_id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=now(), index=True)
    service_name: str = Field(max_length=128, index=True)
    severity: SeverityEnum
    status: StatusEnum = Field(default=StatusEnum.OPEN)
    title: str = Field(max_length=512)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_signature: Optional[str] = Field(default=None, max_length=256, index=True)

    # Vector embedding for semantic similarity (1536 dimensions)
    embedding: Optional[str] = Field(default=None, sa_column=Column(String(8192)))
    context_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    resolution_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    root_cause: Optional[str] = Field(default=None, sa_column=Column(Text))
    resolution_time_seconds: Optional[int] = None
    confidence_score: Optional[float] = None
    auto_resolved: bool = Field(default=False)
    organization_id: str = Field(foreign_key="organizations.id")
    assigned_agent_id: Optional[str] = Field(default=None, foreign_key="agents.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="incidents")
    assigned_agent: Optional["Agent"] = Relationship(back_populates="incidents")
    agent_memories: List["AgentMemory"] = Relationship(back_populates="incident")
    execution_logs: List["AgentExecutionLog"] = Relationship(back_populates="incident")


class AgentMemory(TimestampMixin, table=True):
    """
    MEDIUM VOLUME: Agent learning data
    HTAP NEEDED: Real-time pattern matching during incident resolution
    """

    __tablename__ = "agent_memories"  # type: ignore
    __table_args__ = (
        Index("idx_type_confidence", "memory_type", "confidence"),
        Index("idx_usage_success", "usage_count", "success_rate"),
        Index("idx_agent", "agent_id"),
        Index("idx_organization", "organization_id"),
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    id: str = Field(
        default_factory=cuid, primary_key=True
    )  # ? Not write heavy as telemetries, so cuid is fine here

    incident_id: Optional[str] = Field(
        default=None,
        foreign_key="incidents.id",
    )
    agent_id: str = Field(foreign_key="agents.id")
    memory_type: MemoryType
    content: Dict[str, Any] = Field(sa_column=Column(JSON))
    embedding: Optional[str] = Field(default=None, sa_column=Column(String(8192)))
    confidence: float
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    incident: Optional["Incident"] = Relationship(back_populates="agent_memories")
    agent: Optional["Agent"] = Relationship(back_populates="memories")
    organization: Optional["Organization"] = Relationship(
        back_populates="agent_memories"
    )


###########################################################################
###################### Optional - Audit & Debug DATA ######################
###########################################################################


class Trace(SQLModel, table=True):
    __tablename__ = "traces"  # type: ignore

    __table_args__ = (
        Index("idx_trace_id", "trace_id"),
        Index("idx_service_time", "service_name", "start_time"),
        Index("idx_parent_span", "parent_span_id"),
    )

    id: str = Field(primary_key=True)
    trace_id: str = Field(max_length=64, index=True)
    span_id: str = Field(max_length=64)
    parent_span_id: Optional[str] = Field(default=None, max_length=64)
    operation_name: str = Field(max_length=255)
    start_time: int
    end_time: Optional[int] = None
    duration_ms: Optional[float] = None
    status: str = Field(max_length=32)
    attributes: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    events: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    service_name: str = Field(max_length=128)
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="traces")


class Event(SQLModel, table=True):
    __tablename__ = "events"  # type: ignore

    __table_args__ = (
        Index("idx_timestamp", "timestamp"),
        Index("idx_type_severity", "event_type", "severity"),
        Index("idx_source", "source"),
        Index("idx_organization", "organization_id"),
    )

    id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=now)
    event_type: str = Field(max_length=64)
    source: str = Field(max_length=128)
    severity: SeverityEnum
    title: str = Field(max_length=512)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    event_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="events")


class AgentExecutionLog(SQLModel, table=True):
    __tablename__ = "agent_execution_logs"  # type: ignore

    __table_args__ = (
        Index("idx_incident", "incident_id"),
        Index("idx_agent_time", "agent_id", "timestamp"),
        Index("idx_stage", "execution_stage"),
        Index("idx_success", "success"),
        Index("idx_organization", "organization_id"),
    )

    id: str = Field(primary_key=True)
    incident_id: str = Field(foreign_key="incidents.id")
    agent_id: str = Field(foreign_key="agents.id")
    execution_stage: ExecutionStage
    action_type: str = Field(max_length=64)
    input_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    execution_time_ms: Optional[int] = None
    confidence_score: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    timestamp: datetime = Field(default_factory=now)
    organization_id: str = Field(foreign_key="organizations.id")

    # Relationships
    incident: Optional["Incident"] = Relationship(back_populates="execution_logs")
    agent: Optional["Agent"] = Relationship(back_populates="execution_logs")
    organization: Optional["Organization"] = Relationship(
        back_populates="execution_logs"
    )
