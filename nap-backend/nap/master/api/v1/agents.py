from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from langchain_core.exceptions import ModelError
from loguru import logger
from nap.db.models import AgentConfig, AgentMCP, Agents, LLMs
from nap.master.api.v1.llms import LLMBrief, _to_brief
from nap.master.manager import MANAGER, ChatSSE, ToolModel
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
    tools: dict = {}
    mcp_uuids: list[str] = []


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    llm: Optional[str] = None
    status: Optional[str] = None
    config: Optional[AgentConfig | dict] = None
    knowledge_bases: Optional[list[str]] = None
    tools: Optional[dict] = None
    mcp_uuids: Optional[list[str]] = None


# class AgentResponse(BaseModel):
#     uuid: str
#     name: str
#     description: str
#     instruction: str
#     llm: str
#     status: str
#     config: dict
#     created_at: str
#     updated_at: str
#     knowledge_bases: list[str] = []
#     tools: list[str] = []


class AgentsResponse(BaseModel):
    agents: list[Agents]


class AgentDetail(BaseModel):
    """对话页用的智能体详情：工具与 MCP 元信息直接平铺进 agent 结构。

    与 Agents 的区别：
    - ``tools`` 由 ``{名称: 参数配置}`` 换成工具元信息列表（只含该 agent 已启用的）
    - ``mcps`` 直接给关联的 MCP 对象，不再需要 ``mcp_uuids``
    - ``llm`` 由 uuid 换成模型对象（不含 api_key）

    工具的参数配置值（如 tavily api_key）不在这里返回：它们由后端在对话时
    从库里直接读取（见 MANAGER.chat 的 tool_args），不需要下发给前端。
    """

    uuid: str
    name: str
    description: str
    instruction: str
    llm: LLMBrief
    status: str
    config: AgentConfig
    knowledge_bases: list[str] = []
    tools: list[ToolModel] = []
    mcps: list[AgentMCP] = []


class QueryRequest(BaseModel):
    text: str
    model: str = ""


class ChatRequest(BaseModel):
    query: str
    model: str = ""
    session: str | None = ""
    tools: list[str] | None = []
    knowledge_bases: list[str] | None = []
    mcp_uuids: list[str] | None = None
    attachments: list[str] = []


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


@router.get("/{uuid}/detail", response_model=AgentDetail)
async def get_agent_detail(uuid: str):
    agent = MANAGER.get_agent(uuid)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    enabled = set(agent.tools.keys())
    # 用 query 而非 get_by_uuid：后者在找不到时抛 ValueError，会让整个接口 500
    llm_items = LLMs.query(LLMs.uuid == agent.llm) if agent.llm else []
    llm = llm_items[0] if llm_items else None
    detail = AgentDetail(
        uuid=agent.uuid,
        name=agent.name,
        description=agent.description,
        instruction=agent.instruction,
        llm=_to_brief(llm) if llm else LLMBrief(uuid=agent.llm or ""),
        status=agent.status,
        config=agent.config,
        knowledge_bases=agent.knowledge_bases,
        # 已启用的工具，联网搜索也包含在内（前端自行决定是否展示）
        tools=[t for t in MANAGER.list_tools() if t.name in enabled],
        mcps=MANAGER.list_mcps(agent.mcp_uuids),
    )
    return detail


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
        mcp_uuids=body.mcp_uuids,
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
    if body.mcp_uuids is not None:
        a.mcp_uuids = body.mcp_uuids

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
                custom_tools=body.tools or [],
                knowledge_bases=body.knowledge_bases or [],
                attachments=body.attachments,
                mcp_uuids=body.mcp_uuids,
            ):
                if isinstance(delta, ChatSSE):
                    yield delta.model_dump_json()
                    continue
                reasoning_content = delta.additional_kwargs.get("reasoning_content")
                data = ChatSSE(
                    type="thinking" if reasoning_content else "text",
                    msg=reasoning_content if reasoning_content else str(delta.content),
                )
                if not data.msg:
                    continue
                yield data.model_dump_json()
        except (ModelError, httpx.ConnectError) as e:
            logger.error("request failed: {}", e)
            data = ChatSSE(
                type="error",
                msg=f"Error: request failed: {e}",
            )
            yield data.model_dump_json()
        except Exception as e:
            logger.error("chat failed: {}", e)
            data = ChatSSE(
                type="error",
                msg=f"Error: request failed: {e}",
            )
            yield data.model_dump_json()

    return EventSourceResponse(event_generator())
