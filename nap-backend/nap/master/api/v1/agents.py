from typing import Optional

from fastapi import APIRouter, HTTPException
from pystonic.common import context
from pystonic.utils.strutil import text_shorten
from nap.db.models import Agents, Session
from nap.master.manager import MANAGER
from pydantic import BaseModel
from sse_starlette import EventSourceResponse


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


class ChatRequest(BaseModel):
    query: str
    model: str = ""
    session: str | None = ""


class ChatSSE(BaseModel):
    type: str
    msg: str = ""


@router.get("")
async def list_agents():
    return {"agents": Agents.query()}


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
    return a


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
    return a


@router.delete("/{uuid}", status_code=204)
async def delete_agent(uuid: str):
    a = Agents.get_by_uuid(uuid)
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")
    a.delete()


@router.post("/{agent_uuid}/chat")
async def chat(agent_uuid: str, body: ChatRequest):

    async def event_generator():
        async for delta in MANAGER.chat(
            Agents.get_by_uuid(agent_uuid), body.query, session_id=body.session
        ):
            reasoning_content = delta.additional_kwargs.get("reasoning_content")
            data = ChatSSE(
                type="thinking" if reasoning_content else "text",
                msg=reasoning_content if reasoning_content else str(delta.content),
            )
            if not data.msg:
                continue
            yield data.model_dump_json()

    return EventSourceResponse(event_generator())
