from pydantic import BaseModel


class Permission(BaseModel):
    id: str
    name: str
    description: str
    resource: str
    action: str
    created_at: str


class Role(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None = None
    is_default: bool = False
    is_system: bool = False
    level: int = 0
    permissions: list[Permission] = []
