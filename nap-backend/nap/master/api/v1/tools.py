from fastapi import APIRouter
from pydantic import BaseModel

from nap.common.objects import ToolkitMetadata
from nap.master.manager import MANAGER

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
            ToolkitResponse(metadata=x.metadata(), arg_schema=x.model_json_schema())
            for x in MANAGER.list_tools()
        ]
    )
