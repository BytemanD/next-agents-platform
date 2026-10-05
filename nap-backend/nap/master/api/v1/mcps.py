from fastapi import APIRouter, HTTPException
from nap.db.models import AgentMCP
from nap.master.agent.tools import mcp
from nap.master.manager import MANAGER
from pydantic import BaseModel
from starlette import status

router = APIRouter(prefix="/mcps", tags=["MCP"])


class MCPCreate(BaseModel):
    url: str
    name: str | None = None
    transport: str = "streamable_http"
    api_key: str | None = None


class MCPUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    transport: str | None = None
    api_key: str | None = None


class MCPsResponse(BaseModel):
    mcps: list[AgentMCP] = []


@router.get("", response_model=MCPsResponse)
async def list_mcps():
    return MCPsResponse(mcps=MANAGER.list_mcps())


@router.get("/{mcp_uuid}", response_model=AgentMCP)
async def get_mcp(mcp_uuid: str):
    item = MANAGER.get_mcp(mcp_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"mcp {mcp_uuid} not exists"
        )
    return item


async def _get_mcp_name(url: str, transport: str, api_key: str | None = None):
    server_info = await mcp.get_mcp_server_info(
        "test_mcp", url, transport, api_key=api_key
    )
    if server_info and server_info.get("test_mcp"):
        return server_info.get("test_mcp").serverInfo.name


@router.post("", status_code=201, response_model=AgentMCP)
async def create_mcp(body: MCPCreate):
    if not body.name:
        body.name = await _get_mcp_name(body.url, body.transport, api_key=body.api_key)
    if not body.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="mcp name is required"
        )
    return MANAGER.create_mcp(body.name, body.url, body.transport, body.api_key)


@router.put("/{mcp_uuid}", response_model=AgentMCP)
async def update_mcp(mcp_uuid: str, body: MCPUpdate):
    item = MANAGER.get_mcp(mcp_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"mcp {mcp_uuid} not exists"
        )

    if body.name is not None:
        item.name = body.name
    if body.url is not None:
        item.url = body.url
    if body.transport is not None:
        item.transport = body.transport
    if body.api_key is not None:
        item.api_key = body.api_key

    if not item.name:
        item.name = await _get_mcp_name(item.url, item.transport, api_key=item.api_key)
    if not item.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="mcp name is required"
        )
    item.save()
    return item


@router.delete("/{mcp_uuid}", status_code=204)
async def delete_mcp(mcp_uuid: str):
    item = MANAGER.get_mcp(mcp_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"mcp {mcp_uuid} not exists"
        )
    item.delete()
