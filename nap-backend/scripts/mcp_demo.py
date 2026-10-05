from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math", port=8888)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
