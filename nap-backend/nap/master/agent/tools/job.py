from langchain.tools import ToolRuntime
from langchain_core.tools import BaseToolkit, tool
from loguru import logger

from nap.db.models import AgentSuggestion
from nap.master.agent.context import NapRuntimeContext


@tool
def refresh_agent_suggestions(
    runtime: ToolRuntime[NapRuntimeContext], suggestions: list[str]
):
    """保存智能体建议问题列表到数据库

    当需要更新智能体建议问题列表时调用
    """
    AgentSuggestion.set_by_agent(runtime.context.agent_uuid, suggestions)
    logger.success(
        "add {} suggestions for agent: {}",
        len(suggestions),
        runtime.context.agent_uuid,
    )


class Toolkit(BaseToolkit):
    """知识库工具集"""

    def get_tools(self) -> list:
        return [
            refresh_agent_suggestions,
        ]


TOOLKIT = Toolkit()
