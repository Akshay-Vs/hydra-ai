from fastmcp import FastMCP
from fastmcp.client import transports
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Create a basic server instance
mcp = FastMCP(name="MyAssistantServer")

# You can also add instructions for how to interact with the server
mcp_with_instructions = FastMCP(
    name="HelpfulAssistant",
    instructions="""
        This server provides data analysis tools.
        Call the appropriate tool for your needs.
    """,
)


@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b


@mcp.tool
def divide(a: float, b: float) -> float:
    """Divides one number by another."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@mcp.tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b


@mcp.tool
def subtract(a: float, b: float) -> float:
    """Subtracts one number from another."""
    return a - b


@mcp.resource("data://config")
def get_config() -> dict:
    """Provides the application configuration."""
    return {"theme": "dark", "version": "1.0"}


@mcp.prompt
def greet_user(name: str) -> str:
    """Generates a greeting message for the user."""
    return f"Hello, {name}! How can I assist you today?"


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=9000)
