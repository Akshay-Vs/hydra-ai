from dataclasses import dataclass
from datetime import datetime
from typing import List

from clerk_backend_api import EmailAddress
from clerk_backend_api.types import Nullable


@dataclass
class UserSession:
    """User session data structure"""

    user_id: str
    org_id: str
    username: Nullable[str]
    email: List[EmailAddress]
    roles: list
    permissions: set
    connected_at: datetime
    last_activity: datetime
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
