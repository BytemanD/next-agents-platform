from datetime import timedelta

from fastapi import APIRouter
from nap.db.models import AgentCallback
from pystonic.orm.models import utcnow
from sqlmodel import col

router = APIRouter(prefix="/monitoring", tags=["监控"])


@router.get("/token-usage")
async def token_usage(days: int = 7, agent_uuid: str | None = None):
    return AgentCallback.token_usage(days=days, agent_uuid=agent_uuid)


@router.get("/latency")
async def latency(days: int = 7, agent_uuid: str | None = None):
    since = utcnow() - timedelta(days=days)
    filters = [col(AgentCallback.created_at) >= since]
    if agent_uuid:
        filters.append(col(AgentCallback.agent_uuid) == agent_uuid)
    rows = AgentCallback.query(*filters)

    per_day: dict[str, list[float]] = {}
    for row in rows:
        samples = row.latencies
        if not samples:
            samples = [row.total_latency * 1000] if row.total_latency else []
        key = row.created_at.date().isoformat()
        per_day.setdefault(key, []).extend(samples)

    def percentile(values: list[float], p: float) -> float:
        if not values:
            return 0.0
        s = sorted(values)
        idx = min(len(s) - 1, max(0, round((p / 100) * (len(s) - 1))))
        return round(s[idx], 1)

    labels, p50, p95, p99 = [], [], [], []
    for i in range(days - 1, -1, -1):
        day = (utcnow() - timedelta(days=i)).date()
        labels.append(day.strftime("%m-%d"))
        samples = per_day.get(day.isoformat(), [])
        p50.append(percentile(samples, 50))
        p95.append(percentile(samples, 95))
        p99.append(percentile(samples, 99))

    return {"days": labels, "p50": p50, "p95": p95, "p99": p99}
