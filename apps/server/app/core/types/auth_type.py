from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "client_credentials"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str = "api_access"


class ClientInfo(BaseModel):
    client_id: str
    name: str
    issued_at: datetime
    expires_at: datetime


class SessionClient(BaseModel):
    session_id: str
    organization_id: str
    organization_name: Optional[str]
    expires_at: datetime
    last_used_at: Optional[datetime]
