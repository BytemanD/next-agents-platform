import httpx
from loguru import logger
from langchain.agents import create_agent
from pydantic import BaseModel, SecretStr
from langchain_openai import ChatOpenAI
from pystonic.common import context
from langchain_openai.chat_models.base import OpenAIRateLimitError
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables.config import RunnableConfig
from langchain_community.callbacks import get_openai_callback
from pystonic.utils.strutil import text_shorten
from pystonic.utils.httpclient import default_client

from nap.common.conf import CONF
from nap.common.manager import BaseManager
from nap.db.models import AgentCallback, KnowledgeStatus, Session
from nap.llm.tools import vector
from nap.services.storage import STORE_SERVICE

from nap.common.exceptions import (
    LLMIsInvalid,
    LLMRateLimitError,
)
from nap.db.models import Agents, Knowledge, KnowledgeBase, LLMs


class Message(BaseModel):
    id: str
    type: str
    content: str | None = None
    thinking: str | None = None


class ReasoningChatOpenAI(ChatOpenAI):
    """保留 reasoning_content 字段的 ChatOpenAI 包装器"""

    def _convert_chunk_to_generation_chunk(
        self, chunk, default_chunk_class, base_generation_info
    ):
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )
        if generation_chunk is None:
            return None

        # 从原始 delta 中提取 reasoning_content
        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {})
            reasoning = delta.get("reasoning_content") or delta.get("reasoning")
            if reasoning and isinstance(generation_chunk.message, AIMessageChunk):
                # breakpoint()
                prev = generation_chunk.message.additional_kwargs.get(
                    "reasoning_content", ""
                )
                generation_chunk.message.additional_kwargs["reasoning_content"] = (
                    prev + reasoning
                )
        return generation_chunk


class MasterManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.knowledge_client = default_client(
            base_url=CONF.master.knowledge_base_url, raise_for_status=True
        )

    def upload_knowledge(
        self, kb: KnowledgeBase, creator: str, filename: str, content: bytes
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        knowledge = Knowledge(
            knowledge_base=kb.uuid,
            creator=creator,
            name=filename,
            size=len(content),
            raw_path="",
            convert_path="",
            status=KnowledgeStatus.pending_process.value,
        )
        knowledge.create()

        STORE_SERVICE.save_raw(knowledge, content)

        knowledge.add_todo("convert")
        knowledge.add_todo("vector")
        knowledge.add_todo("enrich")
        return knowledge

    def list_session(self):
        """Project manager"""
        return Session.query()

    def _build_agent(
        self,
        agent: Agents,
        model: str | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
        temperature: float | None = None,
    ):
        llm = LLMs.get_by_uuid(agent.llm)
        if not llm.models:
            raise LLMIsInvalid(llm.uuid)

        agent_model = ReasoningChatOpenAI(
            model=model or llm.models[0],
            api_key=SecretStr(llm.api_key),
            base_url=llm.base_url,
            temperature=agent.config.temperature,
            stream_usage=True,
            model_kwargs={"stream_options": {"include_usage": True}},
            # use_responses_api=True,
            # reasoning_effort="medium",
            # use_responses_api=False,
        )

        return create_agent(
            model=agent_model,
            system_prompt=agent.instruction,
            checkpointer=checkpointer,
            tools=[vector.retrival],
        )

    async def chat(
        self,
        db_agent: Agents,
        query: str,
        session_id: str | None = None,
        model: str | None = None,
        temperature: int | None = None,
    ):
        if session_id:
            session = Session.get_by_uuid(session_id)
        else:
            session = Session(
                user=context.getvar("account", "guest"),
                agent=db_agent.uuid,
                title=text_shorten(query, wide=10),
            )
            session.create()

        with get_openai_callback() as cb:
            async for event in self._chat(
                db_agent, session, query, model=model, temperature=temperature
            ):
                yield event

            callback = AgentCallback(
                agent_uuid=db_agent.uuid,
                session_uuid=session.uuid,
                total_tokens=cb.total_tokens,
                prompt_tokens=cb.prompt_tokens,
                completion_tokens=cb.completion_tokens,
                total_cost=cb.total_cost,
            )
            self.run_background_job(callback.create)

    async def _chat(
        self,
        db_agent: Agents,
        session: Session,
        query: str,
        model: str | None = None,
        temperature: int | None = None,
    ):
        async with AsyncSqliteSaver.from_conn_string(
            CONF.store + "/checkpoint.sqlite"
        ) as checkpointer:
            agent = self._build_agent(
                db_agent,
                model=model,
                temperature=temperature,
                checkpointer=checkpointer,
            )
            stream = agent.astream(
                {"messages": [{"role": "user", "content": query}]},
                stream_mode="messages",
                config={
                    "configurable": {
                        "thread_id": session.uuid,
                    },
                    "metadata": {
                        "account": "guest",
                        "agent": db_agent.uuid,
                    },
                },
                # version="v3"
                context=vector.Context(),
            )

            try:
                async for event in stream:
                    if isinstance(event, tuple) and isinstance(
                        event[0], AIMessageChunk
                    ):
                        yield event[0]
                        continue

                    logger.warning("unknowd event: {}", event)
            except OpenAIRateLimitError as e:
                logger.error("request failed because rate limit")
                raise LLMRateLimitError(str(e))

    async def list_sessions(self, agent_uuid: str):
        return Session.get_recent(agent_uuid)

    async def delete_session(self, session_id: str):
        return Session.delete_by_uuid(session_id)

    async def list_messages(self, session: Session):
        messages = []
        async with AsyncSqliteSaver.from_conn_string(
            "data/checkpoint.sqlite"
        ) as checkpointer:
            config = RunnableConfig(configurable={"thread_id": session.uuid})
            item = await checkpointer.aget_tuple(config)
            if item:
                for msg in item.checkpoint.get("channel_values", {}).get(
                    "messages", []
                ):
                    messages.append(
                        Message(
                            id=msg.id,
                            type=msg.type,
                            content=msg.content,
                            thinking=msg.additional_kwargs.get("reasoning_content"),
                        )
                    )

        return messages

    def delete_knowledge(self, knowledge: Knowledge):
        try:
            self.knowledge_client.delete(f"/api/v1/knowledges/{knowledge.uuid}")
        except httpx.HTTPError as e:
            logger.error("CALL knowledge service failed: {}", e)
            knowledge.set_status(KnowledgeStatus.pending_delete)


MANAGER = MasterManager()
