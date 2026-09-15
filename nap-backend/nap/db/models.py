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

    delete = 900
    delete_pending = auto()
    delete_running = auto()
    delete_completed = auto()
    delete_failed = auto()


def _get_account():
    return context.getvar("account") or "guest"


class Users(DBModel, table=True):
    __tablename__ = "users"  # type: ignore

    account: str = Field(nullable=False)
    email: str = Field(nullable=False)


class LLMs(DBModel, table=True):
    __tablename__ = "llms"  # type: ignore

    name: str = Field(nullable=False, default="")
    base_url: str = Field(nullable=False)
    api_key: str = Field(nullable=False)
    models: list[str] = Field(nullable=False, default=[], sa_type=JSON)


class Agents(DBModel, table=True):
    __tablename__ = "agents"  # type: ignore

    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    instruction: str = Field(
        nullable=False, sa_type=Text, description="agent instruction"
    )
    llm: str = Field(nullable=False, description="LLM UUID")
    status: str = Field(nullable=False, default="draft")
    tools: list[str] = Field(nullable=False, default=[], sa_type=JSON)

    @classmethod
    def get_first(cls, uuid: str):
        items = cls.query(cls.uuid == uuid)
        if not items:
            raise AgentNotExists(uuid)
        return items[0]


class KnowledgeBase(DBModel, table=True):
    __tablename__ = "knowledge_bases"  # type: ignore

    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    active: bool = Field(
        nullable=False, default=1, description="whether the knowledge base is active"
    )


class Knowledge(DBModel, table=True):
    __tablename__ = "knowledges"  # type: ignore

    knowledge_base: str = Field(nullable=False, description="knowledge base UUID")
    creator: str = Field(nullable=False, description="knowledge creator")
    name: str = Field(nullable=False)
    size: int = Field(nullable=False)
    path: str = Field(nullable=True)
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

    def set_status(self, status: KnowledgeStatus):
        self.status = status.value
        self.save()

    @classmethod
    def batch_set_status(cls, uuids: Sequence[str], status: KnowledgeStatus | int):
        stm = (
            update(cls).where(col(cls.uuid).in_(uuids)).values({"status": int(status)})
        )
        with get_session() as session:
            session.exec(stm)
            session.commit()


class Session(DBModel, table=True):
    __tablename__ = "sessions"  # type: ignore

    user: str = Field(nullable=False, default="guest")
    agent: str = Field(nullable=False)
    title: str = Field(nullable=True, default="")

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
