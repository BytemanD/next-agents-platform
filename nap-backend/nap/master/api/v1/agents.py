from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from nap.db.models import Agents
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/agents")


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    instruction: str = ""
    llm: str = ""
    status: str = "draft"
    tools: list[str] = []


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    llm: Optional[str] = None
    status: Optional[str] = None
    tools: Optional[list[str]] = None


class AgentResponse(BaseModel):
    uuid: str
    name: str
    description: str
    instruction: str
    llm: str
    status: str
    tools: list[str]
    created_at: str
    updated_at: str


class QueryRequest(BaseModel):
    text: str
    model: str = ""


def _to_response(a: Agents) -> AgentResponse:
    return AgentResponse(
        uuid=a.uuid,
        name=a.name,
        description=a.description,
        instruction=a.instruction,
        llm=a.llm,
        status=a.status,
        tools=a.tools,
        created_at=a.created_at.isoformat(),
        updated_at=a.updated_at.isoformat(),
    )


@router.get("")
async def list_agents():
    return {"agents": [_to_response(a) for a in Agents.query()]}


@router.get("/{uuid}")
async def get_agent(uuid: str):
    a = Agents.get_by_uuid(uuid)
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")
    return a


@router.post("", status_code=201)
async def create_agent(body: AgentCreate):
    a = Agents(
        name=body.name,
        description=body.description,
        instruction=body.instruction,
        llm=body.llm,
        status=body.status,
        tools=body.tools,
    )
    a.create()
    return _to_response(a)


@router.put("/{uuid}")
async def update_agent(uuid: str, body: AgentUpdate):
    a = Agents.get_by_uuid(uuid)
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")

    if body.name is not None:
        a.name = body.name
    if body.description is not None:
        a.description = body.description
    if body.instruction is not None:
        a.instruction = body.instruction
    if body.llm is not None:
        a.llm = body.llm
    if body.status is not None:
        a.status = body.status
    if body.tools is not None:
        a.tools = body.tools

    a.save()
    return _to_response(a)


@router.delete("/{uuid}", status_code=204)
async def delete_agent(uuid: str):
    a = Agents.get_by_uuid(uuid)
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")
    a.delete()


@router.post("/{session_id}/chat")
async def query(
    session_id: str,
    req: QueryRequest,
):
    async def event_stream():
        async for chunk in MANAGER.streaming_llm_query(
            req.text, session_id=session_id, model=req.model
        ):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
