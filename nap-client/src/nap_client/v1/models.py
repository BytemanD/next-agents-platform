from typing import Any

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base model for API responses; ignores unknown fields."""

    model_config = ConfigDict(extra="ignore")


# ---------- auth / user ----------


class TokenResp(APIModel):
    token: str


class User(APIModel):
    uuid: str = ""
    username: str = ""
    email: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ---------- llm ----------


class LLM(APIModel):
    uuid: str = ""
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    models: list[str] = []
    created_at: str | None = None
    updated_at: str | None = None


class LLMBrief(APIModel):
    uuid: str = ""
    name: str = ""
    base_url: str = ""
    models: list[str] = []


class LLMsResponse(APIModel):
    llms: list[LLM] = []


# ---------- mcp ----------


class MCP(APIModel):
    uuid: str = ""
    name: str = ""
    url: str = ""
    transport: str = "streamable_http"
    api_key: str | None = None
    creator: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class MCPsResponse(APIModel):
    mcps: list[MCP] = []


# ---------- agent ----------


class AgentConfig(APIModel):
    temperature: float = 1
    max_tokens: int | None = None


class ToolExtras(APIModel):
    title: str = ""
    type: str = ""
    requires: dict[str, Any] = {}
    help: str | None = None


class ToolModel(APIModel):
    name: str = ""
    description: str = ""
    extras: ToolExtras = ToolExtras()
    args: dict[str, Any] = {}


class Agent(APIModel):
    uuid: str = ""
    creator: str = ""
    name: str = ""
    description: str = ""
    instruction: str = ""
    llm: str = ""
    status: str = ""
    config: AgentConfig = AgentConfig()
    knowledge_bases: list[str] = []
    tools: dict[str, Any] = {}
    mcp_uuids: list[str] = []
    created_at: str | None = None
    updated_at: str | None = None


class AgentDetail(APIModel):
    uuid: str = ""
    name: str = ""
    description: str = ""
    instruction: str = ""
    llm: LLMBrief = LLMBrief()
    status: str = ""
    config: AgentConfig = AgentConfig()
    knowledge_bases: list[str] = []
    tools: list[ToolModel] = []
    mcps: list[MCP] = []


class AgentsResponse(APIModel):
    agents: list[Agent] = []


class ChatEvent(APIModel):
    type: str = ""
    msg: str = ""


# ---------- session ----------


class Session(APIModel):
    uuid: str = ""
    user: str = ""
    agent: str = ""
    title: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class SessionsResponse(APIModel):
    sessions: list[Session] = []


class Message(APIModel):
    id: str = ""
    type: str = ""
    content: str | None = None
    thinking: str | None = None


class MessagesResponse(APIModel):
    messages: list[Message] = []


# ---------- knowledge base / knowledge ----------


class KnowledgeBase(APIModel):
    uuid: str = ""
    name: str = ""
    description: str = ""
    active: bool = True
    creator: str = ""
    created_at: str | None = None
    updated_at: str | None = None
    shared_with: list[Any] = []


class KnowledgeBasesResponse(APIModel):
    items: list[KnowledgeBase] = []


class Knowledge(APIModel):
    uuid: str = ""
    knowledge_base: str = ""
    creator: str = ""
    name: str = ""
    size: int = 0
    raw_path: str | None = None
    convert_path: str | None = None
    status: int | str = 0
    created_at: str | None = None
    updated_at: str | None = None
    enrichment: dict[str, Any] = {}


class KnowledgesResponse(APIModel):
    items: list[Knowledge] = []


class KnowledgeTodo(APIModel):
    uuid: str = ""
    knowlwdge_uuid: str = ""
    name: str = ""
    status: str = ""
    detail: str = ""


class KnowledgeTodosResponse(APIModel):
    items: list[KnowledgeTodo] = []


class KBStats(APIModel):
    total: int = 0


class AddedKnowledgesResponse(APIModel):
    knowledges: list[Knowledge] = []


# ---------- attachment ----------


class Attachment(APIModel):
    uuid: str = ""
    name: str = ""
    size: int = 0
    creator: str = ""
    created_at: str | None = None
    raw_path: str | None = None
    convert_path: str | None = None


class AttachmentResponse(APIModel):
    attachment: Attachment


class AttachmentsResponse(APIModel):
    attachments: list[Attachment] = []


# ---------- toolkit ----------


class ToolkitMetadata(APIModel):
    name: str = ""
    title: str = ""
    type: str = ""
    help: str = ""


class Toolkit(APIModel):
    metadata: ToolkitMetadata = ToolkitMetadata()
    arg_schema: dict[str, Any] = {}


class ToolkitsResponse(APIModel):
    tools: list[Toolkit] = []


# ---------- monitoring / dashboard ----------


class TokenUsage(APIModel):
    days: list[str] = []
    prompt: list[int] = []
    completion: list[int] = []
    total_prompt: int = 0
    total_completion: int = 0
    total_tokens: int = 0
    total_calls: int = 0


class Latency(APIModel):
    days: list[str] = []
    p50: list[float] = []
    p95: list[float] = []
    p99: list[float] = []


class MonitoringModels(APIModel):
    models: list[str] = []


class DashboardStat(APIModel):
    key: str = ""
    label: str = ""
    value: int = 0
    change: int = 0


class DashboardAgent(APIModel):
    uuid: str = ""
    name: str = ""
    description: str = ""
    model: str = ""
    status: str = ""
    tools: list[str] = []


class DashboardActivity(APIModel):
    type: str = ""
    text: str = ""
    time: str = ""


class Dashboard(APIModel):
    stats: list[DashboardStat] = []
    recent_agents: list[DashboardAgent] = []
    activities: list[DashboardActivity] = []
