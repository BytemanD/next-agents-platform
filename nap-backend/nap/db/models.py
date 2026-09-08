from pystonic.orm.models import DBModel, get_session
from sqlmodel import JSON, Field, Text, col, func, select


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
    __tablename__ = "agents" # type: ignore

    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    instruction: str = Field(
        nullable=False, sa_type=Text, description="agent instruction"
    )
    llm: str = Field(nullable=False, description="LLM UUID")
    status: str = Field(nullable=False, default="draft")
    tools: list[str] = Field(nullable=False, default=[], sa_type=JSON)


class KnowledgeBase(DBModel, table=True):
    __tablename__ = "knowledge_bases" # type: ignore

    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    active: bool = Field(
        nullable=False, default=1, description="whether the knowledge base is active"
    )


class Knowledge(DBModel, table=True):
    __tablename__ = "knowledges" # type: ignore

    knowledge: str = Field(nullable=False, description="knowledge base UUID")
    name: str = Field(nullable=False)
    size: int = Field(nullable=False)
    path: str = Field(nullable=True)
    status: int = Field(
        nullable=False,
        default=0,
        description="0: saved, 1: parsing, 2: parsed, 3: parse_failed, 100: deleting, 101: deleted",
    )

    @classmethod
    def count(cls, *criterion, **filters):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = select(func.count(col(cls.id))).where(*criterion).filter_by(**filters)
        with get_session() as session:
            query = session.exec(stm)
            return query.one()
