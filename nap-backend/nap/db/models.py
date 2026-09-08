from pystonic.orm.models import DBModel
from sqlmodel import JSON, Field, Text


class Users(DBModel, table=True):
    account: str = Field(nullable=False)
    email: str = Field(nullable=False)


class LLMs(DBModel, table=True):
    name: str = Field(nullable=False, default="")
    base_url: str = Field(nullable=False)
    api_key: str = Field(nullable=False)
    models: list[str] = Field(nullable=False, default=[], sa_type=JSON)


class Agents(DBModel, table=True):
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    instruction: str = Field(
        nullable=False, sa_type=Text, description="agent instruction"
    )
    llm: str = Field(nullable=False, description="LLM UUID")
    status: str = Field(nullable=False, default="draft")
    tools: list[str] = Field(nullable=False, default=[], sa_type=JSON)


class KnowledgeBase(DBModel, table=True):
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    file_path: str = Field(nullable=True)
    status: str = Field(nullable=False, default="pending")


class Knowledge(DBModel, table=True):
    knowledge: str = Field(nullable=False, description="knowledge base UUID")
    name: str = Field(nullable=False)
    size: int = Field(nullable=False)
    path: str = Field(nullable=True)
    status: str = Field(nullable=False, default="pending")
