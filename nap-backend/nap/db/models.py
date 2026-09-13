from enum import IntEnum

from nap.common.exceptions import AgentNotExists
from pystonic.orm.models import DBModel, get_session
from sqlmodel import JSON, Field, Text, col, desc, func, select
from pystonic.common import context


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


class KnowledgeStatus(IntEnum):
    queue = 0
    saving = 1
    saved = 2
    parsing = 3
    parsed = 4
    parse_failed = 5
    deleting = 100
    deleted = 101


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
        description=(
            "  0: queue, "
            "  1: saving, "
            "  2: saved, "
            "  3: parsing, "
            "  4: parsed, "
            "  5: parse_failed, "
            "100: deleting, "
            "101: deleted"
        ),
    )

    def __str__(self):
        return f"{self.uuid}({self.name})"

    @classmethod
    def count(cls, *criterion, **filters):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = select(func.count(col(cls.id))).where(*criterion).filter_by(**filters)
        with get_session() as session:
            query = session.exec(stm)
            return query.one()


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
