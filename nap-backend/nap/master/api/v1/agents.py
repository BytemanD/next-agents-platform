from typing import Optional

from fastapi import APIRouter, HTTPException
from langchain_openai.chat_models.base import OpenAIInvalidRequestError
from loguru import logger
from nap.db.models import AgentConfig, Agents
from nap.master.manager import MANAGER
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

router = APIRouter(prefix="/agents", tags=["智能体"])


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    instruction: str = ""
    llm: str = ""
    status: str = "draft"
    config: AgentConfig = AgentConfig()
    knowledge_bases: list[str] = []
    tools: list[str] = []


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    llm: Optional[str] = None
    status: Optional[str] = None
    config: Optional[AgentConfig | dict] = None
    knowledge_bases: Optional[list[str]] = None
    tools: Optional[list[str]] = None


class AgentResponse(BaseModel):
    uuid: str
    name: str
    description: str
    instruction: str
    llm: str
    status: str
    config: dict
    created_at: str
    updated_at: str
    knowledge_bases: list[str] = []
    tools: list[str] = []


class AgentsResponse(BaseModel):
    agents: list[Agents]


class QueryRequest(BaseModel):
    text: str
    model: str = ""


class ChatRequest(BaseModel):
    query: str
    model: str = ""
    session: str | None = ""
    tools: list[str] | None = []
    knowledge_bases: list[str] | None = []


class ChatSSE(BaseModel):
    type: str
    msg: str = ""


@router.get(
    "",
    response_model=AgentsResponse,
    response_model_exclude={"agents": {"__all__": {"instruction", "id"}}},
)
async def list_agents():
    return AgentsResponse(agents=MANAGER.get_agents())


@router.get("/{uuid}", response_model=Agents)
async def get_agent(uuid: str):
    agent = MANAGER.get_agent(uuid)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("", status_code=201)
async def create_agent(body: AgentCreate):
    return MANAGER.create_agent(
        body.name,
        description=body.description,
        instruction=body.instruction,
        llm=body.llm,
        config=body.config,
        knowledge_bases=body.knowledge_bases,
        tools=body.tools,
    )


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
    if body.config is not None:
        a.config = (
            body.config
            if isinstance(body.config, AgentConfig)
            else AgentConfig.model_validate(body.config)
        )
    if body.knowledge_bases is not None:
        a.knowledge_bases = body.knowledge_bases
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
        try:
            async for delta in MANAGER.chat(
                Agents.get_by_uuid(agent_uuid),
                body.query,
                session_id=body.session,
                model=body.model,
                tools=body.tools or [],
                knowledge_bases=body.knowledge_bases or [],
            ):
                reasoning_content = delta.additional_kwargs.get("reasoning_content")
                data = ChatSSE(
                    type="thinking" if reasoning_content else "text",
                    msg=reasoning_content if reasoning_content else str(delta.content),
                )
                if not data.msg:
                    continue
                yield data.model_dump_json()
        except OpenAIInvalidRequestError as e:
            logger.error("openai invalid request: {}", e)
            data = ChatSSE(
                type="text",
                msg=f"Error: openai invalid request: {e}",
            )
            yield data.model_dump_json()

    return EventSourceResponse(event_generator())
