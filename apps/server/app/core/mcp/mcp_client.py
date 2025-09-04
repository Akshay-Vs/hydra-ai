from fastmcp.client import BearerAuth, Client
from fastmcp.client.transports import StreamableHttpTransport

from app.core.types.mcp import MCPServerConfig, ServerConnection, ServerStatus
from app.utils.logging import create_logger

from typing import Any, Dict, List, Optional

logger = create_logger(__name__)


class MCPClient:
    def __init__(self):
        self.servers: Dict[str, ServerConnection] = {}
        self._request_id = 0

    def _get_next_request_id(self) -> int:
        """Generate next request ID"""
        self._request_id += 1
        return self._request_id

    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add a new MCP server to connect to"""
        try:
            transport = StreamableHttpTransport(
                url=config.url,
                headers=config.headers,
                auth=BearerAuth(token=config.auth_token if config.auth_token else ""),
            )
            client = Client(transport=transport)
            connection = ServerConnection(config=config, client=client)

            connection.tools = []
            connection.resources = []
            connection.prompts = []
            connection.status = ServerStatus.CONNECTING

            self.servers[config.name] = connection
            logger.info(f"Added server {config.name} at {config.url}")
            return True

        except Exception as e:
            logger.error(f"Failed to add server {config.name}: {e}")
            return False

    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server and fetch its capabilities"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return False

        connection = self.servers[server_name]

        if not connection.client:
            logger.error(f"Client for server {server_name} is not initialized")
            return False

        if connection.status == ServerStatus.CONNECTED:
            logger.info(f"Server {server_name} is already connected")
            return True

        try:
            async with connection.client as client:
                await client._connect()
                logger.info(f"Connection established with server {server_name}")
                connection.status = ServerStatus.CONNECTED
                return True
        except Exception as e:
            connection.status = ServerStatus.ERROR
            connection.error_message = str(e)
            logger.error(f"Failed to connect to server {server_name}: {e}")
            return False

    async def get_tools(self, server_name: str) -> Optional[List[Any]]:
        """Fetch available tools from the MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return None

        connection = self.servers[server_name]

        if connection.status != ServerStatus.CONNECTED:
            logger.error(f"Server {server_name} is not connected")
            return None

        try:
            tools = await connection.client.list_tools()
            connection.tools = tools
            logger.info(f"Fetched {len(tools)} tools from server {server_name}")
            return tools
        except Exception as e:
            logger.error(f"Failed to fetch tools from server {server_name}: {e}")
            return None

    async def get_resources(self, server_name: str) -> Optional[List[Any]]:
        """Fetch available resources from the MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return None

        connection = self.servers[server_name]

        if connection.status != ServerStatus.CONNECTED:
            logger.error(f"Server {server_name} is not connected")
            return None

        try:
            resources = await connection.client.list_resources()
            connection.resources = resources
            logger.info(f"Fetched {len(resources)} resources from server {server_name}")
            return resources
        except Exception as e:
            logger.error(f"Failed to fetch resources from server {server_name}: {e}")
            return None

    async def get_prompts(self, server_name: str) -> Optional[List[Any]]:
        """Fetch available prompts from the MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return None

        connection = self.servers[server_name]

        if connection.status != ServerStatus.CONNECTED:
            logger.error(f"Server {server_name} is not connected")
            return None

        try:
            prompts = await connection.client.list_prompts()
            connection.prompts = prompts
            logger.info(f"Fetched {len(prompts)} prompts from server {server_name}")
            return prompts
        except Exception as e:
            logger.error(f"Failed to fetch prompts from server {server_name}: {e}")
            return None

    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return False

        connection = self.servers[server_name]

        if connection.status != ServerStatus.CONNECTED:
            logger.info(f"Server {server_name} is not connected")
            return True

        try:
            await connection.client._disconnect()
            connection.status = ServerStatus.DISCONNECTED
            logger.info(f"Disconnected from server {server_name}")
            return True
        except Exception as e:
            connection.status = ServerStatus.ERROR
            connection.error_message = str(e)
            logger.error(f"Failed to disconnect from server {server_name}: {e}")
            return False

    async def get_client(
        self, server_name: str
    ) -> Optional[Client[StreamableHttpTransport]]:
        """Get the MCP client for a connected server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return None

        connection = self.servers[server_name]

        if connection.status != ServerStatus.CONNECTED:
            logger.error(f"Server {server_name} is not connected")
            return None

        return connection.client
