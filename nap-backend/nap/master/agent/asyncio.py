import aiosqlite
from langchain.agents import create_agent
from langchain_community.callbacks import OpenAICallbackHandler
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import OpenAIRateLimitError
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from loguru import logger
from nap.common.conf import CONF
from nap.common.exceptions import LLMRateLimitError
from nap.common.objects import Message
from nap.db.models import AgentCallback, Session
from nap.master.agent.callbacks import TraceHandler
from nap.master.agent.context import RuntimeContext
from nap.master.agent.middlewares import RuntimeAgentMiddleware
from nap.master.agent.tools import user
from pystonic.common import context

INTERNAL_TOOLS = [
    user.get_username,
    user.get_available_knowledge_bases,
    user.get_attachments,
    user.get_attachment_content,
]
CUSTOM_TOOLS = [user.retrival, user.list_documents, user.tavily_hub_search]


class AsyncAgent:
    def __init__(self):
        self._conn = aiosqlite.connect(CONF.store + "/checkpoint.sqlite")
        self._saver = AsyncSqliteSaver(self._conn)
        self._agent = create_agent(
            ChatOpenAI(model="gpt", base_url="...", api_key="..."),
            checkpointer=self._saver,
            context_schema=RuntimeContext,
            middleware=[RuntimeAgentMiddleware()],
            # tools=[*INTERNAL_TOOLS, *CUSTOM_TOOLS],
            tools=[*INTERNAL_TOOLS],
        )

    async def stop(self):
        logger.info("close checkpointer connection")
        await self._conn.close()

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
        ctx.tools.extend(INTERNAL_TOOLS)
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
            model=ctx.model,
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
