from fastapi import APIRouter
from nap.master.manager import MANAGER, ToolModel
from pydantic import BaseModel

router = APIRouter(prefix="/tools", tags=["工具"])


class ToolsResponse(BaseModel):
    tools: list[ToolModel] = []


@router.get("", response_model=ToolsResponse)
async def list_tools():
    return ToolsResponse(tools=MANAGER.list_tools())
