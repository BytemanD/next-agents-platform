from fastapi import APIRouter
from nap.common.objects import ToolkitMetadata
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/toolkits", tags=["工具"])


class ToolkitResponse(BaseModel):
    metadata: ToolkitMetadata
    arg_schema: dict = {}


class ToolkitsResponse(BaseModel):
    tools: list[ToolkitResponse] = []


class ToolsResponse(BaseModel):
    tools: list[dict] = []


@router.get("", response_model=ToolkitsResponse)
async def list_tools():
    return ToolkitsResponse(
        tools=[
            ToolkitResponse(
                metadata=tool.metadata(), arg_schema=tool.model_json_schema()
            )
            for tool in MANAGER.list_tools()
        ]
    )
