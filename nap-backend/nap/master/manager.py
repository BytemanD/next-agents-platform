from typing import Optional

from fastapi import HTTPException
from loguru import logger
from langchain.agents import create_agent
from nap.db.models import Session
from pydantic import BaseModel, SecretStr
from langchain_openai import ChatOpenAI

from pystonic.common import context
from langchain_openai.chat_models.base import OpenAIRateLimitError
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.runnables.config import RunnableConfig

from nap.common.exceptions import (
    LLMIsInvalid,
    LLMRateLimitError,
)
from pystonic.utils.strutil import text_shorten

from nap.db.models import Agents, Knowledge, KnowledgeBase, LLMs
from nap.research.ai import ResearchAI
from nap.storage.manager import get_storage_driver
from nap.vector.manager import get_vector_driver

from langchain_core.messages import AIMessageChunk


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


class MasterManager:
    def __init__(self):
        self.vector_driver = get_vector_driver()
        self.storage_driver = get_storage_driver()
        self.llm = ResearchAI()

    def list_docs(self):
        pid = context.project_id.get()
        if pid:
            return Knowledge.query(Knowledge.project_uuid == pid)
        return Knowledge.query()

    def get_doc_path(self, path: str):
        logger.info("get doc path: {}", path)
        docs = Knowledge.query(Knowledge.path == path)
        if not docs:
            return None
        return self.storage_driver.get_path(docs[0])

    def upload_doc(
        self, kb: KnowledgeBase, creator: str, filename: str, content: bytes
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        doc = Knowledge(
            knowledge_base=kb.uuid,
            creator=creator,
            name=filename,
            size=len(content),
            path="",
            status=0,
        )
        doc.create()
        self.storage_driver.save(doc, content)
        return doc

    def create_project(self, name: str, description: Optional[str]):
        item = Project(name=name, description=description)
        item.create()
        return item

    def list_project(self):
        return Project.query()

    def delete_project(self, uuid: str):
        db_model = Project.get_by_uuid(uuid)
        if not db_model:
            raise Exception(f"Project {uuid} not found")
        db_model.delete()

    def list_session(self):
        """Project manager"""
        return Session.query()

    def create_session(self, name: str, project: Optional[str]):
        db_project = Project.get_by_uuid(project)
        if not db_project:
            raise Exception(f"Project {project} not found")
        item = Session(project_uuid=project, name=name)
        item.create()
        return item

    def retrival(self, text: str):
        return self.vector_driver.query(text)

    async def delete_session(self, session_id: str):
        session = Session.get_by_uuid(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session.delete()
        await self.llm.clear_session_items(session_id)

    def get_models(self):
        return self.llm.list_model()

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
            temperature=temperature,
            # use_responses_api=True,
            # reasoning_effort="medium",
            # use_responses_api=False,
        )

        return create_agent(model=agent_model, checkpointer=checkpointer)

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

        async with AsyncSqliteSaver.from_conn_string(
            "data/checkpoint.sqlite"
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

    async def list_messages(self, session: Session):
        messages = []
        async with AsyncSqliteSaver.from_conn_string(
            "data/checkpoint.sqlite"
        ) as checkpointer:
            config = RunnableConfig(configurable={"thread_id": session.uuid})
            item = await checkpointer.aget_tuple(config)
            if item:
                print("===============================")
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


MANAGER = MasterManager()
