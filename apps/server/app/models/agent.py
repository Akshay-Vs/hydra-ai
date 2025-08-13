from sqlmodel import SQLModel, Field
from cuid import cuid


class AgentConfig(SQLModel, table=True):
    id: str = Field(default_factory=cuid, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    model: str = Field(default=None, nullable=False)
    version: str = Field(default=None, nullable=False)
    system_prompt: str = Field(default=None, nullable=True)
    created_at: str = Field(default=None, nullable=False)
    updated_at: str = Field(default=None, nullable=False)
