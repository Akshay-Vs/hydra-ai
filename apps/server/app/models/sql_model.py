from datetime import datetime
from sqlmodel import JSON, Column, Index, SQLModel, Field, Relationship, String, Text
from typing import Any, ClassVar, Dict, List, Optional
from cuid import cuid

from app.models.enums import (
    AgentStatus,
    ExecutionStage,
    InvitationStatus,
    LogLevelEnum,
    MembershipStatus,
    MemoryType,
    Permissions,
    SeverityEnum,
    StatusEnum,
)


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
    name: str = Field(index=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    # Relationships
    agents: List["OrganizationAgent"] = Relationship(back_populates="organization")
    roles: List["Role"] = Relationship(back_populates="organization")
    incidents: List["Incident"] = Relationship(back_populates="organization")
    events: List["Event"] = Relationship(back_populates="organization")
    traces: List["Trace"] = Relationship(back_populates="organization")


class OrganizationMember(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    user_id: str = Field(foreign_key="user.id")
    role_id: str = Field(foreign_key="role.id")

    joined_at: str
    left_at: Optional[str] = Field(default=None)
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


class Agent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    agent_status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    is_system: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    # Relationships
    organization_agents: List["OrganizationAgent"] = Relationship(
        back_populates="agent"
    )
    config: Optional["AgentConfig"] = Relationship(back_populates="agent")
    incidents: List["Incident"] = Relationship(back_populates="assigned_agent")
    memories: List["AgentMemory"] = Relationship(back_populates="agent")
    execution_logs: List["AgentExecutionLog"] = Relationship(back_populates="agent")


class AgentConfig(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", unique=True)
    model: str
    version: str
    system_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    agent: Optional["Agent"] = Relationship(back_populates="config")


class OrganizationAgent(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    organization_id: str = Field(foreign_key="organization.id")
    agent_id: str = Field(foreign_key="agent.id")
    role_id: str = Field(foreign_key="role.id")
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE)
    added_at: datetime = Field(default_factory=datetime.now)
    removed_at: Optional[datetime] = None
    role_expires_at: Optional[datetime] = None

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
    agent_assignments: List["OrganizationAgent"] = Relationship(back_populates="role")
    permissions: List["RolePermission"] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    role_id: str = Field(foreign_key="role.id")
    action: Permissions = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="permissions")


###########################################################################
############### HTAP-NEEDED MODELS BELOW - HIGH VOLUME DATA ###############
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
        # TiDB-specific: Enable TiFlash replica via table comment
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    metric_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
    service_name: str = Field(max_length=128, index=True)
    metric_name: str = Field(max_length=64)
    value: float
    labels: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    unit: Optional[str] = Field(default=None, max_length=32)
    anomaly_score: float = Field(default=0.0)
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")

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
        # Vector index for semantic search (TiDB HNSW)
        Index("idx_embedding_hnsw", "embedding", mysql_using="HNSW"),
        # Full-text search
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    log_id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
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
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")

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
        # Vector similarity search index
        # Full-text search on title and description
        Index("ft_title_desc", "title", "description", mysql_using="FULLTEXT"),
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    incident_id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
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
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")
    assigned_agent_id: Optional[str] = Field(default=None, foreign_key="agent.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="incidents")
    assigned_agent: Optional["Agent"] = Relationship(back_populates="incidents")
    agent_memories: List["AgentMemory"] = Relationship(back_populates="incident")
    execution_logs: List["AgentExecutionLog"] = Relationship(back_populates="incident")


class AgentMemory(SQLModel, table=True):
    """
    MEDIUM VOLUME: Agent learning data
    HTAP NEEDED: Real-time pattern matching during incident resolution
    """

    __tablename__ = "agent_memory"  # type: ignore
    __table_args__ = (
        Index("idx_type_confidence", "memory_type", "confidence"),
        Index("idx_usage_success", "usage_count", "success_rate"),
        Index("idx_agent", "agent_id"),
        Index("idx_organization", "organization_id"),
        {"comment": "SET TIFLASH REPLICA 1"},
    )

    memory_id: str = Field(primary_key=True)
    incident_id: Optional[str] = Field(
        default=None, foreign_key="incidents.incident_id"
    )
    agent_id: str = Field(foreign_key="agent.id")
    memory_type: MemoryType
    content: Dict[str, Any] = Field(sa_column=Column(JSON))
    embedding: Optional[str] = Field(default=None, sa_column=Column(String(8192)))
    confidence: float
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    incident: Optional["Incident"] = Relationship(back_populates="agent_memories")
    agent: Optional["Agent"] = Relationship(back_populates="memories")


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

    id: Optional[int] = Field(default=None, primary_key=True)
    trace_id: str = Field(max_length=64, index=True)
    span_id: str = Field(max_length=64)
    parent_span_id: Optional[str] = Field(default=None, max_length=64)
    operation_name: str = Field(max_length=255)
    start_time: int  # Unix timestamp in microseconds
    end_time: Optional[int] = None
    duration_ms: Optional[float] = None
    status: str = Field(max_length=32)
    attributes: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    events: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    service_name: str = Field(max_length=128)
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="events")


class Event(SQLModel, table=True):
    __tablename__ = "events"  # type: ignore

    __table_args__ = (
        Index("idx_timestamp", "timestamp"),
        Index("idx_type_severity", "event_type", "severity"),
        Index("idx_source", "source"),
        Index("idx_organization", "organization_id"),
    )

    event_id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str = Field(max_length=64)
    source: str = Field(max_length=128)
    severity: SeverityEnum
    title: str = Field(max_length=512)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    event_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")

    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="events")


class AgentExecutionLog(SQLModel, table=True):
    __tablename__ = "agent_execution_log"  # type: ignore
    __table_args__ = (
        Index("idx_incident", "incident_id"),
        Index("idx_agent_time", "agent_id", "timestamp"),
        Index("idx_stage", "execution_stage"),
        Index("idx_success", "success"),
        Index("idx_organization", "organization_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    incident_id: str = Field(foreign_key="incidents.incident_id")
    agent_id: str = Field(foreign_key="agent.id")
    execution_stage: ExecutionStage
    action_type: str = Field(max_length=64)
    input_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    execution_time_ms: Optional[int] = None
    confidence_score: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    timestamp: datetime = Field(default_factory=datetime.now)
    organization_id: Optional[str] = Field(default=None, foreign_key="organization.id")

    # Relationships
    incident: Optional["Incident"] = Relationship(back_populates="execution_logs")
    agent: Optional["Agent"] = Relationship(back_populates="execution_logs")
