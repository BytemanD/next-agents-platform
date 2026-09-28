from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from nap.db.models import (
    AgentCallback,
    Agents,
    Knowledge,
    KnowledgeStatus,
    LLMs,
    Session,
)
from nap.master.manager import MANAGER
from pydantic import BaseModel
from pystonic.common import context
from pystonic.orm.models import get_session, utcnow
from sqlmodel import col, func, select

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


class DashboardStat(BaseModel):
    key: str
    label: str
    value: int
    change: int


class DashboardAgent(BaseModel):
    uuid: str
    name: str
    description: str
    model: str
    status: str
    tools: list[str] = []


class DashboardActivity(BaseModel):
    type: str
    text: str
    time: str


class DashboardResponse(BaseModel):
    stats: list[DashboardStat]
    recent_agents: list[DashboardAgent]
    activities: list[DashboardActivity]


def _count_model(model, *criteria) -> int:
    stm = select(func.count(col(model.id))).where(*criteria)
    with get_session() as session:
        return int(session.exec(stm).one())


def _sum_tokens(
    since: Optional[datetime] = None, until: Optional[datetime] = None
) -> int:
    cond: list = []
    if since is not None:
        cond.append(AgentCallback.created_at >= since)
    if until is not None:
        cond.append(AgentCallback.created_at < until)
    stm = select(func.coalesce(func.sum(AgentCallback.total_tokens), 0))
    if cond:
        stm = stm.where(*cond)
    with get_session() as session:
        return int(session.exec(stm).one())


def _pct(cur: int, prev: int) -> int:
    return round((cur - prev) / prev * 100) if prev > 0 else 0


def _time_ago(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    secs = int((utcnow() - dt).total_seconds())
    if secs < 60:
        return "刚刚"
    if secs < 3600:
        return f"{secs // 60} 分钟前"
    if secs < 86400:
        return f"{secs // 3600} 小时前"
    if secs < 86400 * 7:
        return f"{secs // 86400} 天前"
    return dt.strftime("%Y-%m-%d")


@router.get("", response_model=DashboardResponse)
async def dashboard():
    account = context.getvar("account") or "guest"
    now = utcnow()
    week = now - timedelta(days=7)
    prev = now - timedelta(days=14)

    not_deleted = col(Knowledge.status).not_in(
        [KnowledgeStatus.deleted.value, KnowledgeStatus.deleting.value]
    )

    kb_total = _count_model(Knowledge, not_deleted)
    kb_cur = _count_model(Knowledge, not_deleted, Knowledge.created_at >= week)
    kb_prev = _count_model(
        Knowledge,
        not_deleted,
        Knowledge.created_at >= prev,
        Knowledge.created_at < week,
    )

    ses_total = _count_model(Session, Session.user == account)
    ses_cur = _count_model(Session, Session.user == account, Session.created_at >= week)
    ses_prev = _count_model(
        Session,
        Session.user == account,
        Session.created_at >= prev,
        Session.created_at < week,
    )

    ag_total = _count_model(Agents, Agents.creator == account)
    ag_cur = _count_model(Agents, Agents.creator == account, Agents.created_at >= week)
    ag_prev = _count_model(
        Agents,
        Agents.creator == account,
        Agents.created_at >= prev,
        Agents.created_at < week,
    )

    tok_total = _sum_tokens()
    tok_cur = _sum_tokens(since=week)
    tok_prev = _sum_tokens(since=prev, until=week)

    stats = [
        DashboardStat(
            key="knowledge_documents",
            label="知识文档",
            value=kb_total,
            change=_pct(kb_cur, kb_prev),
        ),
        DashboardStat(
            key="sessions",
            label="会话数",
            value=ses_total,
            change=_pct(ses_cur, ses_prev),
        ),
        DashboardStat(
            key="agents",
            label="智能体总数",
            value=ag_total,
            change=_pct(ag_cur, ag_prev),
        ),
        DashboardStat(
            key="total_tokens",
            label="总 Token 数",
            value=tok_total,
            change=_pct(tok_cur, tok_prev),
        ),
    ]

    agents = sorted(MANAGER.get_agents(), key=lambda a: a.created_at, reverse=True)[:4]
    llm_cache: dict[str, Optional[LLMs]] = {}

    def model_name(uuid: str) -> str:
        if not uuid:
            return ""
        if uuid not in llm_cache:
            items = LLMs.query(LLMs.uuid == uuid)
            llm_cache[uuid] = items[0] if items else None
        llm = llm_cache[uuid]
        return llm.models[0] if llm and llm.models else (llm.name if llm else uuid)

    recent_agents = [
        DashboardAgent(
            uuid=a.uuid,
            name=a.name,
            description=a.description,
            model=model_name(a.llm),
            status=a.status,
            tools=a.tools or [],
        )
        for a in agents
    ]

    events: list[tuple[str, str, datetime]] = []
    knowledges = Knowledge.query(not_deleted)
    for k in sorted(knowledges, key=lambda x: x.created_at, reverse=True)[:3]:
        events.append(("knowledge", f"知识库新增了文档「{k.name}」", k.created_at))

    sessions = Session.query(Session.user == account)
    for s in sorted(sessions, key=lambda x: x.created_at, reverse=True)[:3]:
        events.append(
            ("session", f"开始了新会话「{s.title or '新会话'}」", s.created_at)
        )

    agent_names = {a.uuid: a.name for a in Agents.query()}
    callbacks = sorted(AgentCallback.query(), key=lambda c: c.created_at, reverse=True)[
        :5
    ]
    for c in callbacks:
        name = agent_names.get(c.agent_uuid) or (c.agent_uuid or "")[:8]
        events.append(("agent", f"智能体「{name}」完成了一次调用", c.created_at))

    events.sort(key=lambda x: x[2], reverse=True)
    activities = [
        DashboardActivity(type=t, text=text, time=_time_ago(dt))
        for t, text, dt in events[:6]
    ]

    return DashboardResponse(
        stats=stats, recent_agents=recent_agents, activities=activities
    )
