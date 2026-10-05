from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://localhost:8000/mcp",  # Streamable HTTP
            "transport": "streamable_http",
        },
    }
)


async def get_mcp_tools(url: str, name: str, transport: str = "streamable_http"):
    client = MultiServerMCPClient(
        {
            "weather": {
                "url": url,  # Streamable HTTP
                "transport": transport,
            },
        }
    )
    return await client.get_tools()
