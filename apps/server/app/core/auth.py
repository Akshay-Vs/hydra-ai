from typing import Dict, Any
from clerk_backend_api import Clerk, AuthenticateRequestOptions, RequestState
from app.utils.logging import create_logger
import httpx

logger = create_logger("clerk-socketio-auth")


class ClerkSocketIOAuth:
    def __init__(self, secret_key: str):
        self.clerk_sdk = Clerk(bearer_auth=secret_key)

    async def authenticate_socket_request(
        self, environ: dict, token: str
    ) -> Dict[str, Any]:
        """
        Authenticate Socket.IO connection using the actual ASGI environ.

        Args:
            environ: ASGI environ dict from Socket.IO connection

        Returns:
            Dict with user information

        Raises:
            Exception: If authentication fails
        """
        try:
            logger.debug("Authenticating Socket.IO request with Clerk SDK")
            # Extract headers from ASGI environ
            headers = {}
            for key, value in environ.items():
                if key.startswith("HTTP_"):
                    # Convert HTTP_AUTHORIZATION to Authorization
                    header_name = key[5:].replace("_", "-").title()
                    headers[header_name] = value

            headers["Authorization"] = f"Bearer {token}"

            # Create real httpx request from ASGI environ
            scheme = environ.get("wsgi.url_scheme", "https")
            host = environ.get("HTTP_HOST", "localhost")
            path = environ.get("PATH_INFO", "/socket.io/")
            query = environ.get("QUERY_STRING", "")

            url = f"{scheme}://{host}{path}"
            if query:
                url += f"?{query}"

            # Create actual request object (not mock!)
            real_request = httpx.Request(
                method=environ.get("REQUEST_METHOD", "GET"), url=url, headers=headers
            )

            # Authenticate using real request
            auth_options = AuthenticateRequestOptions()
            request_state: RequestState = self.clerk_sdk.authenticate_request(
                real_request, auth_options
            )

            if not request_state.is_signed_in:
                logger.error(f"Authentication failed: {request_state.reason}")
                raise Exception(f"Authentication failed: {request_state.reason}")

            # Extract and return user information
            payload = request_state.payload

            if not payload:
                logger.error("No user information found in payload")
                raise Exception("No user information found in payload")

            logger.debug("Authentication successful")
            return payload
        except Exception as e:
            logger.error(f"Socket authentication failed: {str(e)}")
            raise Exception(f"Socket authentication failed: {str(e)}")
