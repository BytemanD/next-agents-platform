from typing import Sequence

from langchain_mcp_adapters.client import MultiServerMCPClient
from nap.db.models import AgentMCP
from pystonic.utils.funcutil import timeit


async def get_mcp_server_info(
    name: str, url: str, transport: str, api_key: str | None = None
):
    client = MultiServerMCPClient(
        {
            name: {
                "url": url,
                "transport": transport,
                "headers": {"Authorization": f"Bearer {api_key}"} if api_key else {},
            }
        }
    )
    return await client.get_server_info()


@timeit
async def get_tools(mcps: Sequence[AgentMCP]):
    client = MultiServerMCPClient(
        {
            mcp.name: {
                "url": mcp.url,
                "transport": mcp.transport,
                "headers": {"Authorization": f"Bearer {mcp.api_key}"}
                if mcp.api_key
                else {},
            }
            for mcp in mcps
        }
    )
    tools = await client.get_tools()
    print("server_info", await client.get_server_info())
    return tools
