import asyncio
from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.core.database.mcp_server_store import MCPServerStore
from app.core.mcp.mcp_client import MCPClient
from sqlmodel import Session

from app.core.types.mcp import MCPServerConfig, ToolExecute
from app.utils.cipher_key import decrypt
from app.utils.logging import create_logger

logger = create_logger(__name__)


class MCPServerRes(BaseModel):
    name: str
    url: str
    icon: str | None
    is_active: bool
    auth_token: str
    organization_id: str
    created_at: datetime
    updated_at: datetime | None


class MCPService:
    def __init__(self, session: Session):
        self.session = session
        self.mcp_client = MCPClient()

    async def fetch_servers(self, org_id: str):
        """
        Fetch MCP servers for an organization,
        add them to the MCP client and return decoded servers
        """
        mcp_store = MCPServerStore(self.session)
        mcp_servers = mcp_store.get_mcp_servers_by_organization(org_id)
        decoded_servers = []

        for server in mcp_servers:
            if server:
                server_data = server.model_dump()
                server_data["auth_token"] = decrypt(server.auth_token)
                decoded_servers.append(MCPServerRes(**server_data))

                await self.mcp_client.add_server(MCPServerConfig(**server_data))
                logger.debug(f"Added server {server_data['name']} to MCP client")

        return decoded_servers

    async def connect_all_servers(self):
        """
        Connect to all MCP servers and return the connection status
        """
        logger.debug("Connecting to all MCP servers")

        server_names = await self.mcp_client.get_servers_names()

        connected_servers = await asyncio.gather(
            *(self.mcp_client.connect_server(name) for name in server_names),
            return_exceptions=True,  # Don't fail all if one server fails
        )

        return connected_servers

    async def fetch_tools(self):
        """
        Fetch tools from an MCP server and return them
        """
        tools = await asyncio.gather(
            *(
                self.mcp_client.get_tools(name)
                for name in await self.mcp_client.get_servers_names()
            )
        )
        return tools

    async def fetch_resources(self):
        """
        Fetch resources from an MCP server and return them
        """
        server_names = await self.mcp_client.get_servers_names()
        resources = await asyncio.gather(
            *(self.mcp_client.get_resources(name) for name in server_names)
        )

        return resources

    async def fetch_prompts(self):
        """
        Fetch prompts from an MCP server and return them
        """
        server_names = await self.mcp_client.get_servers_names()
        prompts = await asyncio.gather(
            *(self.mcp_client.get_prompts(name) for name in server_names)
        )

        return prompts

    async def ping_servers(self):
        """
        Ping all MCP servers and return the ping status
        """
        server_names = await self.mcp_client.get_servers_names()
        pinged_servers = await asyncio.gather(
            *(self.mcp_client.ping_server(name) for name in server_names)
        )
        return pinged_servers

    async def execute_tools(self, tools: List[ToolExecute]):
        """
        Execute tools on all MCP servers and return the execution status
        """
        executed_tools = await asyncio.gather(
            *(self.mcp_client.execute_tool(tool) for tool in tools)
        )
        return executed_tools
