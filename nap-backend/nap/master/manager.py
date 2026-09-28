import httpx
from loguru import logger
from nap.common.conf import CONF
from nap.common.exceptions import LLMIsInvalid
from nap.common.manager import BaseManager
from nap.common.objects import ToolModel
from nap.db.models import (
    AgentCallback,
    Agents,
    Attachment,
    Knowledge,
    KnowledgeBase,
    KnowledgeStatus,
    LLMs,
    Session,
)
from nap.db.types import AgentConfig
from nap.master.agent.asyncio import AsyncAgent
from nap.master.agent.context import RuntimeContext
from nap.master.agent.tools import user
from nap.services.storage import STORE_SERVICE
from pydantic import BaseModel
from pystonic.common import context
from pystonic.utils.httpclient import default_client
from pystonic.utils.strutil import text_shorten

RUNTIME_TOOLS = [user.retrival, user.list_documents]


def _resolve_attachments(file_keys: list[str]) -> list[dict]:
    """将 file_key 解析为 agent 可用的附件元数据"""
    resolved = []
    for key in file_keys:
        if not STORE_SERVICE.has_attachment(key):
            logger.warning("attachment {} not found, skip", key)
            continue
        resolved.append(
            {
                "file_key": key,
                "name": STORE_SERVICE.get_attachment_name(key),
                "filename": STORE_SERVICE.get_attachment_name(key),
            }
        )
    return resolved


class Message(BaseModel):
    id: str
    type: str
    content: str | None = None
    thinking: str | None = None


class MasterManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.knowledge_client = default_client(
            base_url=CONF.master.knowledge_base_url, raise_for_status=True
        )
        self._agent: AsyncAgent = None

    async def start(self):
        await super().start()
        self._agent = AsyncAgent()

    async def stop(self):
        await super().stop()
        await self._agent.stop()

    def create_llm(self, name: str, base_url: str, api_key: str, models: list[str]):
        item = LLMs(
            user=context.getvar("account"),
            name=name,
            base_url=base_url,
            api_key=api_key,
            models=models,
        )
        item.create()
        return item

    def get_agents(self):
        return Agents.query(Agents.creator == context.getvar("account"))

    def get_agent(self, uuid: str):
        items = Agents.query(
            Agents.creator == context.getvar("account"), Agents.uuid == uuid
        )
        if not items:
            return None
        return items[0]

    def create_agent(
        self,
        name: str,
        description: str = "",
        instruction: str = "",
        llm: str = "",
        config: AgentConfig = AgentConfig(),
        knowledge_bases: list[str] = [],
        tools: list[str] = [],
    ):
        a = Agents(
            creator=context.getvar("account", "guest"),
            name=name,
            description=description,
            instruction=instruction,
            llm=llm,
            status="active",
            config=config,
            knowledge_bases=knowledge_bases,
            tools=tools,
        )
        a.create()
        return a

    def upload_knowledge(
        self, kb: KnowledgeBase, filename: str, content: bytes
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        knowledge = Knowledge(
            knowledge_base=kb.uuid,
            creator=context.getvar("account") or "guest",
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

    def add_knowledge_from_url(
        self,
        kb: KnowledgeBase,
        url: str,
        name: str | None = None,
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        logger.info("fetch from: {}", url)
        resp = httpx.get(url)
        resp.raise_for_status()
        content = resp.content

        knowledge = Knowledge(
            knowledge_base=kb.uuid,
            creator=context.getvar("account") or "guest",
            name=name or "unknown",
            size=len(content),
            raw_path="",
            convert_path="",
            status=KnowledgeStatus.pending_process.value,
        )
        knowledge.create()

        STORE_SERVICE.save_raw(knowledge, content)

        knowledge.add_todos("convert", "vector", "enrich")
        return knowledge

    def add_knowledge_from_attachment(
        self,
        kb: KnowledgeBase,
        attachment: Attachment,
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        knowledge = Knowledge(
            knowledge_base=kb.uuid,
            creator=context.getvar("account") or "guest",
            name=attachment.name,
            size=0,
            raw_path=attachment.raw_path,
            convert_path="",
            status=KnowledgeStatus.pending_process.value,
        )
        knowledge.create()
        knowledge.add_todos("convert", "vector", "enrich")
        return knowledge

    def list_session(self):
        return Session.query()

    async def chat(
        self,
        db_agent: Agents,
        query: str,
        session_id: str | None = None,
        model: str | None = None,
        tools: list[str] = [],
        knowledge_bases: list[str] | None = None,
        attachments: list[str] = [],
    ):
        llm = LLMs.get_by_uuid(db_agent.llm)
        if not llm.models:
            raise LLMIsInvalid(llm.uuid)
        if session_id:
            session = Session.get_by_uuid(session_id)
        else:
            session = Session(
                user=context.getvar("account", context.getvar("account")),
                agent=db_agent.uuid,
                title=text_shorten(query, wide=10),
            )
            session.create()

        kb_uuids = knowledge_bases or db_agent.knowledge_bases
        runtime_context = RuntimeContext(
            model=model or llm.models[0],
            model_base_url=llm.base_url,
            model_api_key=llm.api_key,
            agent_uuid=db_agent.uuid,
            agent_config=db_agent.config,
            session_uuid=session.uuid,
            username=context.getvar("account") or "guest",
            system_prompt=db_agent.instruction,
            tools=[
                user.get_username,
                user.get_available_knowledge_bases,
                user.get_attachments,
                user.get_attachment_content,
                *[x for x in RUNTIME_TOOLS if x.name in tools],
            ],
            knowledge_bases=KnowledgeBase.get_by_uuids(kb_uuids) if kb_uuids else [],
            attachments=attachments,
        )

        async for event in self._agent.chat(runtime_context, query):
            if isinstance(event, AgentCallback):
                self.run_background_job(event.create)
                continue
            yield event

    async def list_sessions(self, agent_uuid: str):
        return Session.get_recent(agent_uuid)

    async def delete_session(self, session_id: str):
        return Session.delete_by_uuid(session_id)

    def delete_knowledge(self, knowledge: Knowledge):
        try:
            self.knowledge_client.delete(f"/api/v1/knowledges/{knowledge.uuid}")
        except httpx.HTTPError as e:
            logger.error("CALL knowledge service failed: {}", e)
            knowledge.set_status(KnowledgeStatus.pending_delete)

    def list_tools(self):
        tools = [user.retrival, user.list_documents]
        return [ToolModel.from_llm_tool(x) for x in tools]

    async def list_messages(self, session: Session | str):
        return await self._agent.list_messages(session)

    async def save_attachment(self, name: str, content: bytes):
        attachment = Attachment(
            creator=context.getvar("account") or "guest",
            name=name,
            size=len(content),
        )
        attachment.create()
        STORE_SERVICE.save_attachment_raw(attachment, content)
        return attachment

    def list_attachments(self):
        creator = context.getvar("account")
        return sorted(
            Attachment.query(Attachment.creator == creator),
            key=lambda a: a.created_at,
            reverse=True,
        )

    def delete_attachment(self, attachment: Attachment):
        STORE_SERVICE.remove_attachment(attachment)
        attachment.delete()


MANAGER = MasterManager()
