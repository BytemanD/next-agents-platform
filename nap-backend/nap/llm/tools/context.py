from typing import Sequence

from langchain_core.tools import BaseTool
from nap.db.models import KnowledgeBase
from nap.db.types import AgentConfig
from pydantic import BaseModel


class RuntimeContext(BaseModel):
    model: str
    model_base_url: str
    model_api_key: str

    agent_config: AgentConfig
    system_prompt: str = ""
    tools: list[BaseTool] = []
    knowledge_bases: Sequence[KnowledgeBase] = []
