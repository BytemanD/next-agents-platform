import contextlib
from pathlib import Path

from langchain.agents import create_agent
from langchain_community.callbacks import OpenAICallbackHandler
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import OpenAIRateLimitError
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.mysql.asyncmy import AsyncMySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from loguru import logger
from nap.common.conf import CONF
from nap.common.exceptions import LLMRateLimitError
from nap.common.objects import Message, Toolkit
from nap.db.models import AgentCallback, Session
from nap.master.agent.callbacks import TraceHandler
from nap.master.agent.context import RuntimeContext
from nap.master.agent.middlewares import RuntimeAgentMiddleware
from nap.master.agent.tools import mysql, web_search
from nap.master.agent.tools.builtin import BUILT_IN_TOOLKIT
from pydantic import SecretStr
from pystonic.common import context
from pystonic.orm.database import _engine


@contextlib.asynccontextmanager
async def get_checkpointer_saver():
    if (
        CONF.master.agent_checkpoint_driver in ["auto", "mysql"]
        and _engine.dialect.name == "mysql"
    ):
        logger.info("use mysql checkpoint saver")
        async with AsyncMySaver.from_conn_string(CONF.db.url) as saver:
            logger.debug("setup saver: {}", saver)
            await saver.setup()
            yield saver
        return

    if CONF.master.agent_checkpoint_driver == "mysql":
        raise RuntimeError('checkpoint driver is "mysql" but db config is not mysql ')

    logger.info("use sqlite checkpoint saver")
    saver_path = Path(CONF.store, "checkpoint.sqlite")
    saver_path.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(saver_path)) as saver:
        yield saver


class AsyncAgent:
    def __init__(self, saver: BaseCheckpointSaver):
        self._saver = saver
        self._agent = create_agent(
            ChatOpenAI(model="gpt", base_url="...", api_key=SecretStr("...")),
            checkpointer=saver,
            context_schema=RuntimeContext,
            middleware=[RuntimeAgentMiddleware()],
            # tools=[*INTERNAL_TOOLS, *CUSTOM_TOOLS],
            tools=[*BUILT_IN_TOOLKIT.get_tools()],
        )
        self.toolkits: list[type[Toolkit]] = [
            web_search.WebSearchToolkit,
            mysql.MysqlToolkit,
        ]
        # web_search.WebSearchToolkit.me

    # async def init(self):
    #     if _engine.dialect.name == "mysql":
    #         with  AIOMySQLSaver.from_conn_string(CONF.db.url) as saver:

    # @staticmethod
    # def _build_input(ctx: RuntimeContext, query: str) -> str:
    #     if not ctx.attachments:
    #         return query

    #     parts = [query]
    #     for attachment_uuid in ctx.attachments:
    #         parts.append(
    #             f"\n\n用户上传了附件（uuid: {attachment_uuid}）。"
    #             "如需回答附件相关内容，请调用 get_attachments 查看附件列表，"
    #             "再调用 get_attachment_content 获取对应附件内容。"
    #         )
    #     return "\n".join(parts)

    async def chat(self, ctx: RuntimeContext, query: str):
        ctx.tools.extend(BUILT_IN_TOOLKIT.get_tools())
        trace_handler = TraceHandler()
        openai_callback = OpenAICallbackHandler()
        stream = self._agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="messages",
            config={
                "configurable": {"thread_id": ctx.session_uuid},
                "metadata": {
                    "user": context.getvar("account"),
                    "agent": ctx.agent_uuid,
                },
                "callbacks": [trace_handler, openai_callback],
            },
            # version="v3"
            context=ctx,
        )

        try:
            async for event in stream:
                if isinstance(event, tuple) and isinstance(event[0], AIMessageChunk):
                    yield event[0]
                    continue
                logger.warning("unknowd event: {}", event)
        except OpenAIRateLimitError as e:
            logger.error("request failed because rate limit")
            raise LLMRateLimitError(str(e))

        yield AgentCallback(
            agent_uuid=ctx.agent_uuid,
            session_uuid=ctx.session_uuid,
            model=ctx.selected_model,
            creator=ctx.username,
            total_tokens=openai_callback.total_tokens,
            prompt_tokens=openai_callback.prompt_tokens,
            completion_tokens=openai_callback.completion_tokens,
            total_cost=openai_callback.total_cost,
            total_requests=trace_handler.total_requests,
            success_requests=trace_handler.successful_requests,
            failed_requests=trace_handler.failed_requests,
            total_latency=round(trace_handler.total_latency, 3),
            latencies=[round(x * 1000, 1) for x in trace_handler.latencies],
        )

    async def list_messages(self, session: Session | str):
        session = (
            session if isinstance(session, Session) else Session.get_by_uuid(session)
        )
        config = RunnableConfig(configurable={"thread_id": session.uuid})
        item = await self._saver.aget_tuple(config)
        if not item:
            return []

        return [
            Message(
                id=msg.id,
                type=msg.type,
                content=msg.content,
                thinking=msg.additional_kwargs.get("reasoning_content"),
            )
            for msg in item.checkpoint.get("channel_values", {}).get("messages", [])
            if msg.type in ["human", "ai"]
        ]
