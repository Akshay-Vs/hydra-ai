from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Session

from app.core.database.mcp_server_store import MCPServerStore
from app.core.helpers.ensure_membership import ensure_org_membership
from app.core.helpers.ensure_permissions import ensure_org_permissions
from app.core.helpers.get_user import get_current_user
from app.models.enums import Permissions
from app.models.sql_model import MCPServer, User
from app.services.database_service import get_db_session
from app.utils.logging import create_logger


router = APIRouter()
logger = create_logger(__name__)


class ServerCreateRequest(SQLModel):
    name: str
    description: str | None = None
    url: str
    auth_token: str
    icon: str | None = None
    is_active: bool | None = True


@router.get("/{org_id}")
async def get_servers(
    org_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        logger.debug(f"Received request for org_id: {org_id} by user: {user.id}")
        membership = ensure_org_membership(session, org_id, user)

        logger.debug(f"User {user.id} is a member of organization {org_id}")
        ensure_org_permissions(
            session,
            membership,
            required_permissions=[Permissions.READ, Permissions.WRITE],
        )

        logger.debug(
            f"User {user.id} has READ or WRITE permission for organization {org_id}"
        )

        mcp_store = MCPServerStore(session)
        servers = mcp_store.get_mcp_servers_by_organization(org_id)
        logger.debug(f"Retrieved {len(servers)} servers for organization {org_id}")

        return [
            {
                "id": server.id,
                "name": server.name,
                "description": server.description,
                "url": server.url,
                "icon": server.icon,
                "is_active": server.is_active,
                "organization_id": server.organization_id,
                "created_at": server.created_at,
                "updated_at": server.updated_at,
            }
            for server in servers
            if server is not None
        ]

    except Exception as e:
        logger.error(f"Error in getting mcp servers: {e}")
        raise e


@router.post("/{org_id}")
def create_server(
    org_id: str,
    server_request: ServerCreateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        logger.debug(
            f"Received create server request for org_id: {org_id} by user: {user.id}"
        )
        membership = ensure_org_membership(session, org_id, user)

        logger.debug(f"User {user.id} is a member of organization {org_id}")
        ensure_org_permissions(
            session,
            membership,
            required_permissions=[Permissions.WRITE],
        )

        logger.debug(f"User {user.id} has WRITE permission for organization {org_id}")

        mcp_store = MCPServerStore(session)
        new_server = MCPServer(
            name=server_request.name,
            description=server_request.description,
            url=server_request.url,
            icon=server_request.icon,
            auth_token=server_request.auth_token.encode(),
            organization_id=org_id,
        )
        created_server = mcp_store.create_mcp_server(new_server)
        logger.debug(
            f"Created new server with id {created_server.id} for organization {org_id}"
        )

        return {
            "id": created_server.id,
            "name": created_server.name,
            "description": created_server.description,
            "url": created_server.url,
            "icon": created_server.icon,
            "organization_id": created_server.organization_id,
            "created_at": created_server.created_at,
            "updated_at": created_server.updated_at,
        }

    except Exception as e:
        logger.error(f"Error in create_server: {e}")
        raise e


@router.delete("/{org_id}/{server_name}")
def delete_server(
    org_id: str,
    server_name: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        logger.debug(
            f"Received delete server request for org_id: {org_id} by user: {user.id}"
        )
        membership = ensure_org_membership(session, org_id, user)

        logger.debug(f"User {user.id} is a member of organization {org_id}")
        ensure_org_permissions(
            session,
            membership,
            required_permissions=[Permissions.WRITE],
        )

        logger.debug(f"User {user.id} has WRITE permission for organization {org_id}")

        mcp_store = MCPServerStore(session)
        deleted_server = mcp_store.delete_mcp_server(server_name)
        if deleted_server:
            logger.debug(f"Deleted server {server_name} for organization {org_id}")
            return JSONResponse(
                content={"message": "Server deleted successfully"}, status_code=200
            )

        else:
            logger.debug(
                f"Server with id {server_name} for organization {org_id} not found"
            )
            raise HTTPException(status_code=500, detail="Failed to delete server")
    except Exception as e:
        logger.error(f"Error in delete_server: {e}")
        raise e
