from collections.abc import Sequence
from pathlib import Path

import httpx
from apscheduler.triggers.cron import CronTrigger
from langchain.messages import AIMessage
from langchain_core.tools.base import BaseTool, BaseToolkit
from langgraph.checkpoint.base import BaseCheckpointSaver
from loguru import logger
from pydantic import BaseModel, SecretStr
from pystonic.agents.langchain_agent.agent import AsyncAgent
from pystonic.agents.langchain_agent.callbacks import RequestHandler, get_openai_handler
from pystonic.agents.langchain_agent.tools import builtin, mcp
from pystonic.common import context
from pystonic.common.conf import LLMProviderConfig
from pystonic.infra.messaging.redis import RedisMessaingQueue
from pystonic.utils.httpclient import default_client
from pystonic.utils.strutil import text_shorten
from sqlmodel import col

from nap.common.conf import CONF
from nap.common.exceptions import (
    AttachmentNotExists,
    KnowledgeBaseAlreadyExists,
    LLMIsInvalid,
    NoPermission,
)
from nap.common.manager import BaseManager
from nap.db.models import (
    LLM,
    Agent,
    AgentCallback,
    AgentMCP,
    AgentSuggestion,
    Attachment,
    Knowledge,
    KnowledgeBase,
    KnowledgeBaseShared,
    KnowledgeStatus,
)
from nap.db.types import AgentConfig
from nap.master.agent.context import NapRuntimeContext
from nap.master.agent.tools import base, job, knowledge, mysql, web_search
from nap.services.storage import STORE_SERVICE


class Message(BaseModel):
    id: str
    type: str
    content: str | None = None
    thinking: str | None = None


class ChatSSE(BaseModel):
    type: str
    msg: str = ""


class MasterManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.knowledge_client = default_client(
            base_url=CONF.master.knowledge_base_url, raise_for_status=True
        )
        self._agent: AsyncAgent | None = None
        self.messaging_driver = RedisMessaingQueue()
        self.toolkits = [web_search.WebSearchToolkit, mysql.MysqlToolkit]
        self.builtin_tools = (
            builtin.WorkToolkit(
                enable_read=False,
                enable_write=False,
                enable_execute_shell=False,
                enable_web_get=False,
                enable_get_platform_info=False,
            ).get_tools()
            + base.TOOLKIT.get_tools()
            + knowledge.TOOLKIT.get_tools()
        )

    async def setup(self, saver: BaseCheckpointSaver):
        self._agent = AsyncAgent(saver, context_schema=NapRuntimeContext)

    async def start(self):
        await super().start()
        # self._agent = AsyncAgent()
        self.add_async_job(
            CronTrigger.from_crontab(CONF.master.job_create_agent_suggestions_cron),
            self.job_create_agent_suggestions,
        )

    @property
    def agent(self):
        if not self._agent:
            raise RuntimeError("agent is null, please call setup first")

        return self._agent

    async def stop(self):
        await super().stop()

    def list_llm(self):
        return LLM.query(LLM.user == context.account())

    def create_knowledge_base(
        self, name: str, description: str = "", active: bool = True
    ):
        items = KnowledgeBase.get_first(
            name=name,
            creator=context.account() or "guest",
        )
        if items:
            raise KnowledgeBaseAlreadyExists(name)
        item = KnowledgeBase(
            name=name,
            description=description,
            creator=context.account() or "guest",
            active=active,
        )
        item.create()
        return item

    def list_knowledge_base(self, shared: bool = True):
        if not shared:
            return KnowledgeBase.query(KnowledgeBase.creator == context.account())
        return KnowledgeBase.query(
            col(KnowledgeBase.uuid).in_(
                KnowledgeBaseShared.get_knowledge_base_uuids_by_shared_with(
                    context.account()
                )
            )
        )

    def create_llm(self, name: str, base_url: str, api_key: str, models: list[str]):
        item = LLM(
            user=context.account(),
            name=name,
            base_url=base_url,
            api_key=api_key,
            models=models,
        )
        item.create()
        return item

    def get_agents(self):
        return Agent.query(Agent.creator == context.account())

    def get_agent(self, uuid: str):
        items = Agent.query(Agent.creator == context.account(), Agent.uuid == uuid)
        if not items:
            return None
        return items[0]

    def create_agent(
        self,
        name: str,
        description: str = "",
        instruction: str = "",
        llm: str = "",
        config: AgentConfig | None = None,
        knowledge_bases: list[str] | None = None,
        tools: dict | None = None,
        mcp_uuids: list[str] | None = None,
    ):
        if mcp_uuids is None:
            mcp_uuids = []
        if tools is None:
            tools = {}
        if knowledge_bases is None:
            knowledge_bases = []
        a = Agent(
            creator=context.getvar("account", "guest"),
            name=name,
            description=description,
            instruction=instruction,
            llm=llm,
            status="active",
            config=config or AgentConfig(),
            knowledge_bases=knowledge_bases,
            tools=tools,
            mcp_uuids=mcp_uuids,
        )
        a.create()
        return a

    def upload_knowledge(
        self, kb: KnowledgeBase, filename: str, content: bytes
    ) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        knowledge = Knowledge(
            knowledge_base=kb.uuid,
            creator=context.account() or "guest",
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
        self.messaging_driver.publish("knowledges", knowledge)
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
            creator=context.account() or "guest",
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
            creator=context.account() or "guest",
            name=attachment.name,
            size=attachment.size,
            raw_path=attachment.raw_path,
            convert_path="",
            status=KnowledgeStatus.pending_process.value,
        )
        knowledge.create()
        knowledge.add_todos("convert", "vector", "enrich")
        return knowledge

    async def _get_chat_tools(
        self,
        db_agent: Agent,
        mcp_uuids: list[str] | None = None,
        disable_retrival=False,
        custom_toolkits: Sequence[str | BaseToolkit] | None = None,
    ):
        mcp_tools = []
        try:
            mcp_tools = await mcp.get_tools(
                [
                    mcp.MCP(
                        url=x.url,
                        transport=x.transport,
                        name=x.name,
                        api_key=x.api_key,
                    )
                    for x in self.list_mcps(
                        mcp_uuids if mcp_uuids is not None else db_agent.mcp_uuids
                    )
                ]
            )
        except ExceptionGroup as e:
            logger.error("get mcp tools failed: {}", e.exceptions)
        logger.debug("mcp tools: {}", [t.name for t in mcp_tools])

        custom_toolkits = custom_toolkits or []
        custom_toolkit_tools: list[BaseTool] = []
        for toolkit in custom_toolkits or []:
            if isinstance(toolkit, str):
                if toolkit == "web_search":
                    custom_toolkit_tools.extend(
                        web_search.WebSearchToolkit.model_validate(
                            db_agent.tools.get("web_search", {})
                        ).get_tools()
                    )
                elif toolkit == "mysql":
                    custom_toolkit_tools.extend(
                        mysql.MysqlToolkit.model_validate(
                            db_agent.tools.get("mysql", {})
                        ).get_tools()
                    )
                else:
                    logger.warning("unknown toolkit: {}", toolkit)
            else:
                custom_toolkit_tools.extend(toolkit.get_tools())
        return [
            *builtin.WorkToolkit(
                enable_read=False,
                enable_write=False,
                enable_execute_shell=False,
                enable_web_get=False,
                enable_get_platform_info=False,
            ).get_tools(),
            *base.TOOLKIT.get_tools(),
            *knowledge.KnowledgeToolkit(disable_retrival=disable_retrival).get_tools(),
            *mcp_tools,
            *custom_toolkit_tools,
        ]

    async def chat(
        self,
        db_agent: Agent,
        query: str,
        session_id: str | None = None,
        knowledge_bases: list[str] | None = None,
        attachments: list[str] | None = None,
        mcp_uuids: list[str] | None = None,
        custom_toolkits: Sequence[str | BaseToolkit] | None = None,
        disable_retrival: bool = False,
    ):
        attachments = attachments or []
        custom_tools = custom_toolkits or []
        llm = LLM.get_by_uuid(db_agent.llm)
        if not llm.models:
            raise LLMIsInvalid(llm.uuid)
        session = self.agent.get_or_create_session(
            session_id=session_id,
            user=context.getvar("account", context.account()),
            agent=db_agent.uuid,
            title=text_shorten(query, wide=10),
        )

        runtime_tools = await self._get_chat_tools(
            db_agent,
            mcp_uuids,
            disable_retrival=disable_retrival,
            custom_toolkits=custom_tools,
        )

        kb_uuids = knowledge_bases or db_agent.knowledge_bases
        ctx = NapRuntimeContext(
            providers={
                llm.name: LLMProviderConfig(
                    base_url=llm.base_url,
                    api_key=SecretStr(llm.api_key),
                    models=llm.models,
                )
            },
            thread_id=session.uuid,
            temperature=db_agent.config.temperature,
            system_prompt=db_agent.instruction,
            tools=runtime_tools,
            workspace=Path(CONF.store, "agent_workspace", context.account()),
            username=context.account() or "guest",
            agent_uuid=db_agent.uuid,
            # agent_config=db_agent.config,
            knowledge_bases=KnowledgeBase.get_by_uuids(kb_uuids) if kb_uuids else [],
            attachments=attachments,
        )
        trace_handler = RequestHandler()
        openai_callback = get_openai_handler()
        async for event in self.agent.astream(
            ctx,
            query,
            callbacks=[trace_handler, openai_callback],
            event_types=(AIMessage,),
        ):
            yield event

        agent_callback = AgentCallback(
            agent_uuid=db_agent.uuid,
            session_uuid=session.uuid,
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
        agent_callback.create()

    async def list_agent_sessions(self, agent_uuid: str):
        return self.agent.list_session(
            user=self.get_request_account(), agent=agent_uuid
        )

    async def delete_agent_session(self, session_id: str):
        return self.agent.delete_session(session_id)

    async def list_agent_messages(self, session_id: str):
        return await self.agent.list_messages(session_id)

    def delete_knowledge(self, knowledge: Knowledge):
        knowledge.set_status(KnowledgeStatus.pending_delete)
        self.messaging_driver.publish("knowledges", knowledge)

    def get_knowledge_content(self, knowledge: Knowledge) -> bytes:
        return STORE_SERVICE.get_raw(knowledge)

    def list_tools(self):
        return self.toolkits

    async def save_attachment(self, name: str, content: bytes):
        attachment = Attachment(
            creator=context.account() or "guest",
            name=name,
            size=len(content),
            raw_path=None,
            convert_path=None,
        )
        attachment.create()
        STORE_SERVICE.save_attachment_raw(attachment, content)
        return attachment

    def list_attachments(self):
        creator = context.account()
        return sorted(
            Attachment.query(Attachment.creator == creator),
            key=lambda a: a.created_at,
            reverse=True,
        )

    def delete_attachment(self, attachment: Attachment):
        STORE_SERVICE.remove_attachment(attachment)
        attachment.delete()

    def get_attachment(self, attachment_uuid: str):
        try:
            attachment = Attachment.get_by_uuid(attachment_uuid)
        except ValueError:
            raise AttachmentNotExists(attachment_uuid)
        if attachment.creator != context.account():
            raise NoPermission()
        return attachment

    def get_attachment_content(self, attachment: Attachment):
        return STORE_SERVICE.get_raw(attachment)

    def list_mcps(self, uuids: list[str] | None = None):
        criterion = [col(AgentMCP.creator) == context.account()]
        # 用 `is not None` 而非真值判断：空列表代表"本次不启用任何 MCP"，
        # 不能退化成返回全部
        if uuids is not None:
            criterion.append(col(AgentMCP.uuid).in_(uuids))

        return AgentMCP.query(*criterion)

    def create_mcp(
        self, name: str, url: str, transport: str, api_key: str | None = None
    ):
        item = AgentMCP(
            creator=context.account(),
            name=name,
            url=url,
            transport=transport,
            api_key=api_key,
        )

        item.create()
        return item

    def get_mcp(self, mcp_uuid: str):
        items = AgentMCP.query(
            AgentMCP.creator == context.account(), AgentMCP.uuid == mcp_uuid
        )
        if not items:
            return None
        return items[0]

    async def _refresh_agent_suggestions(self, agent: Agent):
        if agent.suggestion_max() <= 0:
            return
        logger.info("start to refresh suggestions for agent: {}", agent.uuid)
        async for _ in self.chat(
            agent,
            (
                f"根据知识库文档**摘要**生成最多 {agent.suggestion_max()} 个简短的建议, "
                "并使用工具保存到数据库. 禁止读取文档的完整内容."
            ),
            custom_toolkits=[job.TOOLKIT],
            disable_retrival=True,
        ):
            pass
        logger.success("refresh suggestions success for agent: {}", agent.uuid)

    async def job_create_agent_suggestions(self):
        context.set_account("MASTER")
        for db_agent in Agent.query():
            if self.shutdown_event.is_set():
                break
            await self._refresh_agent_suggestions(db_agent)

    def get_agent_suggestions(self, agent_uuid: str):
        return AgentSuggestion.get_by_agent(agent_uuid)


MANAGER = MasterManager()
