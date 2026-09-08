import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

import dotenv
import openai
from agents import Agent, Runner, SQLiteSession, stream_events
from loguru import logger
from nap.research import tools
from openai.types.responses import (
    ResponseFailedEvent,
)
from pystonic.utils.strutil import text_shorten
from rich.console import Console

from .const import instructions

dotenv.load_dotenv()

# instructions = """
# 你是一个文档分析专家, 你的任务是根据用户的问题, 从ChromaDB知识库中检索出最相关的文档，并给出答案。
# 你的回答必须遵循以下规则：
# 1. 必须基于检索到的文档
# 2. 如果找不到相关的文档，请返回 "没有找到相关的文档"
# 3. 你的回答必须标注是根据哪个文档得出的结论

# 你的回答。
# """


class ResearchAI:
    def __init__(self):
        self.session_store_path = Path("data", "conversation.db")
        # atexit.register(self.agent.)
        # set_default_openai_client(self.openai, use_for_tracing=False)
        # if conf.CONF.agent.openai_api:
        #     set_default_openai_api(conf.CONF.agent.openai_api)
        # set_tracing_disabled(True)
        self.models = [
            "qwen3.7-plus",
            "qwen3.7-max-2026-05-17",
            "qwen3.7-max-2026-06-08",
            "qwen3.7-max-preview",
        ]
        self.console = Console()

    def _create_agent(self, model: str):
        return Agent(
            name="Research AI",
            instructions=instructions,
            model=model,
            tools=[
                tools.list_docs,
                tools.query,
            ],
        )

    def set_model(self, model: str):
        if model and model != self.agent.model:
            self.agent.model = model

    def list_model(self):
        """获取模型列表"""
        # TODO
        return self.models

    def _get_session(self, session_id: Optional[str] = None):
        return SQLiteSession(
            session_id or str(uuid4()),
            db_path=self.session_store_path,
        )

    async def streaming_query(
        self,
        text: str,
        session_id: Optional[str] = None,
    ):
        logger.info("[{} {}] query: {}", session_id, self.agent.model, text)
        try:
            result = Runner.run_streamed(
                self.agent,
                text,
                session=self._get_session(session_id),
                max_turns=102400,
            )
            async for event in result.stream_events():
                if isinstance(event, stream_events.AgentUpdatedStreamEvent):
                    yield json.dumps(
                        {
                            "type": "info",
                            "content": f"切换Agent: {event.new_agent.name}",
                        }
                    )
                    continue
                elif isinstance(event, stream_events.RawResponsesStreamEvent):
                    if hasattr(event.data, "delta") and event.data.delta:
                        yield json.dumps(
                            {"type": "thinking", "content": event.data.delta}
                        )
                    elif isinstance(event.data, ResponseFailedEvent):
                        logger.warning(
                            "received response failed event: {}",
                            event.data.response.error,
                        )
                        yield json.dumps(
                            {"type": "error", "content": str(event.data.response.error)}
                        )
                    continue
                elif event.name == "tool_called":
                    logger.info(
                        "选择工具: {}, 参数: {}",
                        event.item.raw_item.name,
                        event.item.raw_item.arguments,
                    )
                    yield json.dumps(
                        {
                            "type": "info",
                            "content": f"使用工具: {event.item.raw_item.name}",
                        }
                    )
                    continue
                elif event.name == "tool_output":
                    logger.info("工具输出: {}", text_shorten(event.item.output))
                    continue
                elif isinstance(event, stream_events.RunItemStreamEvent):
                    if event.item.raw_item.content:
                        for content in event.item.raw_item.content:
                            if not content.text:
                                continue
                            yield json.dumps({"type": "text", "content": content.text})
                    continue
        except openai.APIStatusError as e:
            logger.error("streaming query failed: {}", e)
            yield json.dumps({"type": "error", "content": str(e.response.text)})
        except Exception as e:
            logger.error("streaming query failed: {}", e)
            yield json.dumps({"type": "error", "content": "internal error"})
        yield "[DONE]"

    async def list_messages(self, session_id: Optional[str] = None):
        logger.debug("list messages of session {}", session_id)
        session = self._get_session(session_id=session_id)
        return await session.get_items()

    async def clear_session_items(self, session_id: str):
        logger.debug("clear session {}", session_id)
        session = self._get_session(session_id=session_id)
        await session.clear_session()
