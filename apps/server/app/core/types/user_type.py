from typing import List
from cuid import Optional
from pydantic import BaseModel
from clerk_backend_api import EmailAddress
from clerk_backend_api.types import Nullable
from datetime import datetime


class BaseUser(BaseModel):
    clerk_id: str


class UserPreferenceRequest(BaseModel):
    theme: str = "light"
    timezone: str = "UTC"
    language: str = "en"
    show_notification: bool = True
    user_id: str


class UserCreateRequest(BaseUser, UserPreferenceRequest): ...


class UserPreferenceUpdateRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    theme: str | None = None
    language: str | None = None
    show_notification: bool | None = None
    timezone: str | None = None


class UserSession(BaseModel):
    user_id: str
    org_id: str
    username: Nullable[str]
    email: List[EmailAddress]
    roles: list
    permissions: set
    connected_at: datetime
    last_activity: datetime
    metadata: Optional[dict] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
