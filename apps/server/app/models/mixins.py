from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"onupdate": datetime.now}
    )
