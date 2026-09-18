from datetime import date, datetime, timedelta
from enum import IntEnum, StrEnum, auto
import os
from pathlib import Path
from typing import Sequence

from nap.common.exceptions import AgentNotExists
from nap.db.types import AgentConfig, PydanticType
from pydantic import field_serializer
from pystonic.orm.models import DBModel, get_session
from sqlmodel import JSON, Column, Field, Text, col, desc, func, select, update
from pystonic.common import context


class KnowledgeStatus(IntEnum):
    pending_process = 0
    processing = auto()
    process_failed = auto()

    pending_delete = auto()
    deleting = auto()
    deleted = auto()

    active = auto()


class KnowledgeAction(StrEnum):
    save = "saving"
    parse = "parse"
    vector = "vector"
    enrich = "enrich"
    deleting = "delete"


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
    models: list[str] = Field(
        nullable=False, default=[], sa_type=JSON, description="支持的模型列表"
    )


class Agents(DBModel, table=True):
    __tablename__ = "agents"  # type: ignore

    name: str = Field(nullable=False, description="智能体名称")
    description: str = Field(nullable=False, description="智能体描述")
    instruction: str = Field(
        nullable=False, sa_type=Text, description="agent instruction"
    )
    llm: str = Field(nullable=False, description="LLM UUID")
    status: str = Field(nullable=False, default="draft", description="智能体状态")

    config: AgentConfig = Field(
        default_factory=AgentConfig,
        # nullable=False,
        sa_column=Column(
            PydanticType(AgentConfig),
            nullable=False,
        ),
        description="参数配置",
    )

    knowledge_bases: list[str] = Field(
        nullable=False, default=[], sa_type=JSON, description="知识库"
    )

    tools: list[str] = Field(
        nullable=False, default=[], sa_type=JSON, description="启用的工具列表"
    )

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

    keywords: list[str] = Field(
        nullable=False, sa_type=JSON, description="抽取的关键词列表"
    )
    summary: str = Field(nullable=False, description="文档摘要")


class Knowledge(DBModel, table=True):
    __tablename__ = "knowledges"  # type: ignore

    knowledge_base: str = Field(nullable=False, description="knowledge base UUID")
    creator: str = Field(nullable=False, description="knowledge creator")
    name: str = Field(nullable=False, description="文档文件名称")
    size: int = Field(nullable=False, description="文档文件大小(bytes)")
    raw_path: str | None = Field(nullable=True, description="源文档存储路径")
    convert_path: str | None = Field(nullable=True, description="转化后文档存储路径")
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

    def get_conver_path(self):
        if self.convert_path:
            return self.convert_path
        if not self.raw_path:
            raise ValueError("raw_path is missing")
        return str(Path("convert", self.uuid, os.path.basename(self.raw_path)))

    @classmethod
    def count(cls, *criterion, **filters):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = select(func.count(col(cls.id))).where(*criterion).filter_by(**filters)
        with get_session() as session:
            query = session.exec(stm)
            return query.one()

    @classmethod
    def get_pending_process(cls, limits: int = 100):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = (
            select(cls)
            .where(cls.status == KnowledgeStatus.pending_process.value)
            .limit(limits)
        )

        with get_session() as session:
            query = session.exec(stm)
            return query.all()

    @classmethod
    def get_pending_delete(cls, limits: int = 100):
        """返回一个 QueryBuilder 用于链式查询"""
        stm = (
            select(cls)
            .where(cls.status == KnowledgeStatus.pending_delete.value)
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

    def add_todo(self, name: str):
        item = KnowledgeTodo(knowlwdge_uuid=self.uuid, name=name, status="pending")
        item.create()
        return item

    def get_or_create_todo(self, name: str):
        items = KnowledgeTodo.query(
            KnowledgeTodo.knowlwdge_uuid == self.uuid, KnowledgeTodo.name == name
        )
        return items[0] if items else self.add_todo(name)

    def is_active(self):
        return self.status == KnowledgeStatus.active.value


class KnowledgeTodo(DBModel, table=True):
    __tablename__ = "knowledge_todos"  # type: ignore

    knowlwdge_uuid: str = Field(nullable=False, default="guest", description="知识UUID")
    name: str = Field(nullable=False, description="任务名称")
    status: str = Field(nullable=False, default="pending", description="代办状态")
    detail: str = Field(nullable=False, default="", description="待办详情")

    def is_completed(self):
        return self.status == "completed"

    def set_status(self, status: str):
        self.status = status
        self.save()

    def set_running(self):
        self.set_status("running")

    def set_failed(self, detail: str):
        self.detail = detail
        self.set_status("failed")

    def set_completed(self):
        self.detail = ""
        self.set_status("completed")


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


class AgentCallback(DBModel, table=True):
    __tablename__ = "agent_callbacks"  # type: ignore

    agent_uuid: str = Field(nullable=False, description="Agent UUID")
    session_uuid: str = Field(nullable=False, description="Session UUID")
    model: str = Field(nullable=False, description="Model name")
    total_tokens: int = Field(nullable=True, default=0, description="Total tokens")
    prompt_tokens: int = Field(nullable=True, default=0, description="Prompt_tokens")
    completion_tokens: int = Field(
        nullable=True, default=0, description="Completion tokens"
    )
    total_cost: float = Field(nullable=True, default=0.0, description="Total Fost")

    @classmethod
    def token_usage(cls, days: int = 7):
        since = datetime.now() - timedelta(days=days)
        stm = (
            select(
                func.date(AgentCallback.created_at).label("day"),
                func.coalesce(func.sum(AgentCallback.prompt_tokens), 0).label("prompt"),
                func.coalesce(func.sum(AgentCallback.completion_tokens), 0).label(
                    "completion"
                ),
                func.count(col(AgentCallback.id)).label("calls"),
            )
            .where(col(AgentCallback.created_at) >= since)
            .group_by(func.date(AgentCallback.created_at))
            .order_by(func.date(AgentCallback.created_at))
        )

        with get_session() as session:
            rows = session.exec(stm).all()
        daily = {
            row.day.isoformat() if isinstance(row.day, date) else str(row.day): {
                "prompt": int(row.prompt),
                "completion": int(row.completion),
                "calls": int(row.calls),
            }
            for row in rows
        }

        labels, prompt, completion = [], [], []
        for i in range(days - 1, -1, -1):
            day = (datetime.now() - timedelta(days=i)).date()
            key = day.isoformat()
            labels.append(day.strftime("%m-%d"))
            entry = daily.get(key, {"prompt": 0, "completion": 0, "calls": 0})
            prompt.append(entry["prompt"])
            completion.append(entry["completion"])

        totals = {
            "prompt": sum(v["prompt"] for v in daily.values()),
            "completion": sum(v["completion"] for v in daily.values()),
            "calls": sum(v["calls"] for v in daily.values()),
        }

        return {
            "days": labels,
            "prompt": prompt,
            "completion": completion,
            "total_prompt": totals["prompt"],
            "total_completion": totals["completion"],
            "total_tokens": totals["prompt"] + totals["completion"],
            "total_calls": totals["calls"],
        }
