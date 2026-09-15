from enum import IntEnum, auto
from typing import Sequence

from nap.common.exceptions import AgentNotExists
from pydantic import field_serializer
from pystonic.orm.models import DBModel, get_session
from sqlmodel import JSON, Field, Text, col, desc, func, select, update
from pystonic.common import context


class KnowledgeStatus(IntEnum):
    save_waiting = 0
    save_running = auto()
    save_completed = auto()
    save_failed = auto()

    parse_pending = 100
    parse_running = auto()
    parse_completed = auto()
    parse_failed = auto()

    vector_pending = 200
    vector_running = auto()
    vector_completed = auto()
    vector_failed = auto()

    enrich_pending = 300
    enrich_running = auto()
    enrich_completed = auto()
    enrich_failed = auto()

    delete = 900
    delete_pending = auto()
    delete_running = auto()
    delete_completed = auto()
    delete_failed = auto()

    @classmethod
    def describe(cls, v: "KnowledgeStatus") -> str:
        return {
            cls.save_waiting: "等待保存",
            cls.save_running: "保存中",
            cls.save_completed: "保存完成",
            cls.save_failed: "保存失败",
            cls.parse_pending: "等待解析",
            cls.parse_running: "解析中",
            cls.parse_completed: "解析完成",
            cls.parse_failed: "解析失败",
            cls.vector_pending: "等待向量化",
            cls.vector_running: "向量化中",
            cls.vector_completed: "向量化完成",
            cls.vector_failed: "向量化失败",
            cls.enrich_pending: "等待抽取",
            cls.enrich_running: "抽取中",
            cls.enrich_completed: "抽取完成",
            cls.enrich_failed: "抽取失败",
            cls.delete: "等待删除",
            cls.delete_pending: "等待删除",
            cls.delete_running: "删除中",
            cls.delete_completed: "删除完成",
            cls.delete_failed: "删除失败",
        }.get(v, str(v))


def _get_account():
    return context.getvar("account") or "guest"


class Users(DBModel, table=True):
    __tablename__ = "users"  # type: ignore

    account: str = Field(nullable=False, description="账号")
    email: str = Field(nullable=False, description="邮箱")


class LLMs(DBModel, table=True):
    __tablename__ = "llms"  # type: ignore

    user: str = Field(nullable=False, default="guest", description="所属用户")
    name: str = Field(nullable=False, default="", description="LLM 名称/备注")
    base_url: str = Field(nullable=False, description="API Base URL")
    api_key: str = Field(nullable=False, description="API Key")
    models: list[str] = Field(nullable=False, default=[], sa_type=JSON, description="支持的模型列表")


class Agents(DBModel, table=True):
    __tablename__ = "agents"  # type: ignore

    name: str = Field(nullable=False, description="智能体名称")
    description: str = Field(nullable=False, description="智能体描述")
    instruction: str = Field(
        nullable=False, sa_type=Text, description="agent instruction"
    )
    llm: str = Field(nullable=False, description="LLM UUID")
    status: str = Field(nullable=False, default="draft", description="智能体状态")
    tools: list[str] = Field(nullable=False, default=[], sa_type=JSON, description="启用的工具列表")

    @classmethod
    def get_first(cls, uuid: str):
        items = cls.query(cls.uuid == uuid)
        if not items:
            raise AgentNotExists(uuid)
        return items[0]


class KnowledgeBase(DBModel, table=True):
    __tablename__ = "knowledge_bases"  # type: ignore

    name: str = Field(nullable=False, description="知识库名称")
    description: str = Field(nullable=False, description="知识库描述")
    active: bool = Field(
        nullable=False, default=1, description="whether the knowledge base is active"
    )
    # enrich_llm: str = Field(nullable=True)



class KnowledgeEnrichmen(DBModel, table=True):
    __tablename__ = "knowledge_enrichments"  # type: ignore
    knowledge: str = Field(nullable=False, description="文档 UUID")

    keywords: list[str] = Field(nullable=False, sa_type=JSON, description="抽取的关键词列表")
    summary: str = Field(nullable=False, description="文档摘要")


class Knowledge(DBModel, table=True):
    __tablename__ = "knowledges"  # type: ignore

    knowledge_base: str = Field(nullable=False, description="knowledge base UUID")
    creator: str = Field(nullable=False, description="knowledge creator")
    name: str = Field(nullable=False, description="文档文件名称")
    size: int = Field(nullable=False, description="文档文件大小(bytes)")
    path: str = Field(nullable=True, description="文档存储路径")
    status: int = Field(
        nullable=False,
        default=0,
        description="知识状态(保存, 解析, 向量化, ...,  删除)",
    )

    @field_serializer("status")
    def serialize_created_at(self, value: int) -> str:
        return KnowledgeStatus(value).name

    def __str__(self):
        return f"{self.uuid}({self.name})"

    @classmethod
    def count(cls, *criterion, **filters):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = select(func.count(col(cls.id))).where(*criterion).filter_by(**filters)
        with get_session() as session:
            query = session.exec(stm)
            return query.one()

    @classmethod
    def get_saved(cls, limits: int = 100):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = (
            select(cls)
            .where(cls.status == KnowledgeStatus.save_completed.value)
            .limit(limits)
        )

        with get_session() as session:
            query = session.exec(stm)
            return query.all()

    @classmethod
    def get_todo(cls, limits: int = 100):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = (
            select(cls)
            .where(
                col(cls.status).in_(
                    [
                        KnowledgeStatus.save_completed.value,
                        KnowledgeStatus.delete,
                    ]
                )
            )
            .limit(limits)
        )

        with get_session() as session:
            query = session.exec(stm)
            return query.all()
    @classmethod
    def batch_set_status(cls, uuids: Sequence[str], status: KnowledgeStatus | int):
        stm = (
            update(cls).where(col(cls.uuid).in_(uuids)).values({"status": int(status)})
        )
        with get_session() as session:
            session.exec(stm)
            session.commit()

    def set_status(self, status: KnowledgeStatus):
        self.status = status.value
        self.save()

    def get_enrichment(self):
        items = KnowledgeEnrichmen.query(KnowledgeEnrichmen.knowledge == self.uuid)
        if not items:
            return None
        return items[0]


class Session(DBModel, table=True):
    __tablename__ = "sessions"  # type: ignore

    user: str = Field(nullable=False, default="guest", description="所属用户")
    agent: str = Field(nullable=False, description="智能体 UUID")
    title: str = Field(nullable=True, default="", description="会话标题")

    @classmethod
    def get_recent(cls, agent_uuid: str):
        stm = (
            select(cls)
            .where(
                cls.user == _get_account(),
                cls.agent == agent_uuid,
            )
            .order_by(desc(cls.created_at))
        )

        with get_session() as session:
            return session.exec(stm).all()
