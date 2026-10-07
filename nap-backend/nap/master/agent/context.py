from typing import Sequence

from langchain_core.tools import BaseTool
from nap.db.models import KnowledgeBase
from nap.db.types import AgentConfig
from pydantic import BaseModel


class RuntimeContext(BaseModel):
    models: list[str]
    model_base_url: str
    model_api_key: str

    agent_uuid: str
    agent_config: AgentConfig
    session_uuid: str
    username: str

    model: str | None = None
    system_prompt: str = ""
    tools: list[BaseTool] = []
    knowledge_bases: Sequence[KnowledgeBase] = []
    attachments: list[str] = []

    tool_args: dict = {}

    selected_model: str = ""
