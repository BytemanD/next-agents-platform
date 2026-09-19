from fastapi import APIRouter
from nap.master.manager import MANAGER, ToolModel
from pydantic import BaseModel
from langchain_core.tools.base import BaseTool

from nap.llm.tools import vector

router = APIRouter(prefix="/tools")


class ToolsResponse(BaseModel):
    tools: list[ToolModel] = []


@router.get("", response_model=ToolsResponse)
async def list_tools():
    return ToolsResponse(tools=MANAGER.list_tools())
