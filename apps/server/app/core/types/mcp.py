from enum import Enum
from typing import Any, Dict, List, Optional
from fastmcp.client import Client
from pydantic import BaseModel, ConfigDict

from fastmcp.client.transports import StreamableHttpTransport


class ServerStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server"""

    name: str
    url: str
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    auth_token: Optional[str] = None


class ServerConnection(BaseModel):
    """Represents a connection to an MCP server"""

    config: MCPServerConfig
    client: Client[StreamableHttpTransport]
    status: ServerStatus = ServerStatus.DISCONNECTED
    capabilities: Optional[Dict[str, Any]] = None
    tools: Optional[List[Any]] = None
    resources: Optional[List[Any]] = None
    prompts: Optional[List[Any]] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
