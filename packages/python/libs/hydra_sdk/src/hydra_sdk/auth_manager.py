import httpx
import asyncio
import time
from typing import Optional, Dict, Any


class AuthManager:
    """
    A class to manage JWT token authentication with automatic refresh.

    This class handles:
    - Obtaining JWT tokens via client credentials flow
    - Calculating token expiry times
    - Automatic token refresh when expired
    - Thread-safe token retrieval
    """

    def __init__(self, base_url: str, org_id: str, cred_id: str, client_secret: str):
        """
        Initialize the AuthManager.

        Args:
            base_url (str): The base URL for the API
            org_id (str): Organization ID
            cred_id (str): Credential ID
            client_secret (str): Client secret for authentication
        """
        self.base_url = base_url
        self.org_id = org_id
        self.cred_id = cred_id
        self.client_secret = client_secret

        # Token storage
        self._access_token: Optional[str] = None
        self._token_type: str = "bearer"
        self._expires_at: float = 0

        # API endpoint
        self.token_endpoint = f"{self.base_url}/auth/m2m/token"

    async def _request_token(self) -> Dict[str, Any]:
        """
        Send a POST request to obtain a new JWT token.

        Returns:
            Dict containing the token response

        Raises:
            httpx.RequestError: If the token request fails
            ValueError: If the response format is invalid
        """
        payload = {
            "grant_type": "client_credentials",
            "organization_id": self.org_id,
            "credential_id": self.cred_id,
            "client_secret": self.client_secret,
        }

        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_endpoint, json=payload, headers=headers, timeout=30
                )
                response.raise_for_status()

                token_data = response.json()

                # Validate response format
                required_fields = ["access_token", "token_type", "expires_in"]
                if not all(field in token_data for field in required_fields):
                    raise ValueError(
                        f"Invalid token response format. Expected fields: {required_fields}"
                    )

                return token_data

        except httpx.RequestError as e:
            raise httpx.RequestError(f"Failed to obtain token: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid token response: {str(e)}")

    async def _refresh_token(self) -> None:
        """
        Refresh the JWT token by requesting a new one.

        Updates internal token storage with new token data.
        """
        token_data = await self._request_token()

        self._access_token = token_data["access_token"]
        self._token_type = token_data["token_type"]

        # Calculate expiry time (current time + expires_in seconds)
        expires_in = token_data["expires_in"]
        self._expires_at = time.time() + expires_in

    def _is_token_expired(self) -> bool:
        """
        Check if the current token is expired or will expire soon.

        Returns:
            bool: True if token is expired or will expire within 60 seconds
        """
        if not self._access_token:
            return True

        # Add 60-second buffer to avoid using tokens that expire very soon
        buffer_time = 60
        return time.time() >= (self._expires_at - buffer_time)

    async def get_token(self) -> str | None:
        """
        Get a valid JWT token, refreshing if necessary.

        This method:
        1. Checks if the current token is expired
        2. Refreshes the token if needed
        3. Returns the valid access token

        Returns:
            str: Valid JWT access token

        Raises:
            httpx.RequestError: If token refresh fails
            ValueError: If token response is invalid
        """
        if self._is_token_expired():
            await self._refresh_token()

        return self._access_token

    async def get_auth_header(self) -> Dict[str, str]:
        """
        Get the authorization header for API requests.

        Returns:
            Dict containing the Authorization header
        """
        token = await self.get_token()
        return {"Authorization": f"{self._token_type} {token}"}

    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current token.

        Returns:
            Dict containing token information
        """
        return {
            "has_token": self._access_token is not None,
            "token_type": self._token_type,
            "expires_at": self._expires_at,
            "is_expired": self._is_token_expired(),
            "seconds_until_expiry": max(0, self._expires_at - time.time())
            if self._access_token
            else 0,
        }


# Example usage
async def main():
    # Initialize the auth manager
    auth = AuthManager(
        base_url="http://localhost:8000",
        org_id="cmeuaoswx0000thg0ax87fdiz",
        cred_id="cmf0trd840000d0g0yndjlneq",
        client_secret="Ibt_d0Shba6peoIxBh9vf1qvwcTW0a5YY8DMI0lIiCU",
    )

    try:
        # Get a valid token (will automatically fetch if needed)
        token = await auth.get_token()
        if not token:
            print("Failed to obtain token")
            return

        print(f"Access token: {token[:50]}...")

        # Get authorization header for API requests
        auth_header = await auth.get_auth_header()
        print(f"Auth header: {auth_header}")

        # Get token information
        token_info = auth.get_token_info()
        print(f"Token info: {token_info}")

        # Example of using the token in an async API request
        headers = await auth.get_auth_header()
        headers.update({"Content-Type": "application/json"})

        # async with httpx.AsyncClient() as client:
        #     response = await client.get("https://api.example.com/some-endpoint", headers=headers)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
