from clerk_backend_api import Clerk, AuthenticateRequestOptions, RequestState, User
from app.utils.logging import create_logger
import httpx
from typing import Optional, Union
from fastapi import Request, HTTPException
from starlette.requests import Request as StarletteRequest

logger = create_logger("clerk-socketio-auth")


class ClerkAuth:
    def __init__(self, secret_key: str):
        self.clerk_sdk = Clerk(bearer_auth=secret_key)

    async def authenticate_ASGI(self, environ: dict, token: str) -> User:
        """
        Authenticate Socket.IO connection using the actual ASGI environ.
        Args:
            environ: ASGI environ dict from Socket.IO connection
            token: Bearer token for authentication
        Returns:
            User object from Clerk
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

            return await self._authenticate_request(real_request)

        except Exception as e:
            logger.error(f"Socket authentication failed: {str(e)}")
            raise Exception(f"Socket authentication failed: {str(e)}")

    async def authenticate_HTTP(
        self, request: Union[Request, StarletteRequest]
    ) -> User:
        """
        Authenticate HTTP request using FastAPI/Starlette Request object.
        Args:
            request: FastAPI Request or Starlette Request object
        Returns:
            User object from Clerk
        Raises:
            HTTPException: If authentication fails
        """
        try:
            logger.debug("Authenticating HTTP request with Clerk SDK")

            # Extract authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header:
                logger.error("No authorization header found")
                raise HTTPException(
                    status_code=401, detail="No authorization header found"
                )

            # Create httpx request from FastAPI/Starlette request
            headers = dict(request.headers)

            real_request = httpx.Request(
                method=request.method, url=str(request.url), headers=headers
            )
            logger.info("Authenticating...")
            return await self._authenticate_request(real_request)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"HTTP authentication failed: {str(e)}")
            raise HTTPException(
                status_code=401, detail=f"Authentication failed: {str(e)}"
            )

    async def authenticate_with_token(
        self, token: str, request_url: str = "https://localhost/"
    ) -> User:
        """
        Authenticate using just a token string (useful for manual token validation).
        Args:
            token: Bearer token (without 'Bearer ' prefix)
            request_url: Optional URL to use for the request (defaults to localhost)
        Returns:
            User object from Clerk
        Raises:
            Exception: If authentication fails
        """
        try:
            logger.debug("Authenticating token with Clerk SDK")

            headers = {"Authorization": f"Bearer {token}"}

            real_request = httpx.Request(method="GET", url=request_url, headers=headers)

            return await self._authenticate_request(real_request)

        except Exception as e:
            logger.error(f"Token authentication failed: {str(e)}")
            raise Exception(f"Token authentication failed: {str(e)}")

    async def _authenticate_request(self, request: httpx.Request) -> User:
        """
        Internal method to authenticate an httpx.Request object.
        Args:
            request: httpx.Request object with headers
        Returns:
            User object from Clerk
        Raises:
            Exception: If authentication fails
        """
        try:
            # Authenticate using real request
            auth_options = AuthenticateRequestOptions()
            request_state: RequestState = self.clerk_sdk.authenticate_request(
                request, auth_options
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

            # Get clerk user
            user = self.clerk_sdk.users.get(user_id=payload["sub"])
            if not user:
                logger.error("User not found in Clerk")
                raise Exception("User not found in Clerk")

            return user

        except Exception as e:
            logger.error(f"Request authentication failed: {str(e)}")
            raise
