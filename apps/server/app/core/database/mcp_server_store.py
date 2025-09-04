from typing import Optional, List, Any
from fastapi import HTTPException
from sqlmodel import Session, except_, select, desc
from cryptography.fernet import Fernet

from app.models.sql_model import MCPServer
from app.config.settings import settings


class MCPServerStore:
    """Class to handle MCP Server operations using MCPServer model"""

    def __init__(self, db_session: Session):
        self.db = db_session

        if not settings.encryption_key:
            raise ValueError("Encryption key is not set in settings.")

        self.cipher = Fernet(settings.encryption_key)

    def _with_decrypt(self, result: MCPServer | None) -> Optional[MCPServer]:
        """Decrypt the auth_token of an MCPServer instance"""
        if not result:
            return None

        auth_token = result.auth_token if result else None
        if not auth_token:
            return result

        result.auth_token = self.cipher.decrypt(auth_token)
        return result

    def create_mcp_server(
        self,
        data: MCPServer,
    ) -> MCPServer:
        """
        Create a new MCP server entry with encrypted api_key

        Args:
            name: Name of the MCP server
            auth_token: Authentication token
            url: Server URL
            api_key: API key for the server
            organization_id: Optional organization identifier
            description: Optional server description
            icon: Optional server icon
            is_active: Whether the server is active (defaults to True)

        Returns:
            Created MCPServer object
        """
        try:
            encrypted_key = self.cipher.encrypt(data.auth_token)
            data.auth_token = encrypted_key

            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return data
        except Exception as e:
            if "Duplicate entry" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="MCP Server with the same name or URL already exists.",
                )
            raise HTTPException(status_code=500, detail="Database error.")

    def get_mcp_server(self, server_id: str) -> Optional[MCPServer]:
        """Get MCP server by ID"""
        result = self.db.get(MCPServer, server_id)
        if not result:
            return None

        return self._with_decrypt(result)

    def get_mcp_server_by_name(self, name: str) -> Optional[MCPServer]:
        """Get MCP server by name"""
        statement = select(MCPServer).where(MCPServer.name == name)
        result = self.db.exec(statement).first()
        if not result:
            return None

        return self._with_decrypt(result)

    def get_mcp_server_by_url(self, url: str) -> Optional[MCPServer]:
        """Get MCP server by URL"""
        statement = select(MCPServer).where(MCPServer.url == url)
        result = self.db.exec(statement).first()
        if not result:
            return None

        return self._with_decrypt(result)

    def get_mcp_servers_by_organization(
        self,
        organization_id: str,
        is_active: Optional[bool] = None,
        limit: int = 1000,
    ) -> List[MCPServer | None]:
        """
        Get MCP servers for a specific organization

        Args:
            organization_id: Organization identifier
            is_active: Optional filter by active status
            limit: Maximum number of records to return

        Returns:
            List of MCPServer objects
        """
        statement = select(MCPServer).where(
            MCPServer.organization_id == organization_id
        )

        if is_active is not None:
            statement = statement.where(MCPServer.is_active == is_active)

        statement = statement.order_by(desc(MCPServer.created_at)).limit(limit)
        results = list(self.db.exec(statement).all())
        if not results:
            return []
        return [self._with_decrypt(result) for result in results]

    def update_mcp_server(
        self,
        server_id: str,
        **kwargs: Any,
    ) -> Optional[MCPServer]:
        """
        Update an MCP server

        Args:
            server_id: ID of the server to update
            **kwargs: Fields to update

        Returns:
            Updated MCPServer object or None if not found
        """
        server = self.get_mcp_server(server_id)
        if not server:
            return None

        for key, value in kwargs.items():
            if key == "auth_token" and value is not None:
                encrypted_key = self.cipher.encrypt(value.encode())
                setattr(server, key, encrypted_key)
            elif hasattr(server, key) and value is not None:
                setattr(server, key, value)

        self.db.add(server)
        self.db.commit()
        self.db.refresh(server)
        return server

    def activate_mcp_server(self, server_id: str) -> Optional[MCPServer]:
        """
        Activate an MCP server

        Args:
            server_id: ID of the server to activate

        Returns:
            Updated MCPServer object or None if not found
        """
        return self.update_mcp_server(server_id, is_active=True)

    def deactivate_mcp_server(self, server_id: str) -> Optional[MCPServer]:
        """
        Deactivate an MCP server

        Args:
            server_id: ID of the server to deactivate

        Returns:
            Updated MCPServer object or None if not found
        """
        return self.update_mcp_server(server_id, is_active=False)

    def delete_mcp_server(self, server_id: str) -> bool:
        """
        Delete an MCP server

        Args:
            server_id: ID of the server to delete

        Returns:
            True if deleted, False if not found
        """
        server = self.get_mcp_server(server_id)
        if not server:
            return False

        self.db.delete(server)
        self.db.commit()
        return True
