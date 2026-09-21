from fastapi import APIRouter
from nap.db.models import AgentCallback

router = APIRouter(prefix="/monitoring")


@router.get("/token-usage")
async def token_usage(days: int = 7, agent_uuid: str | None = None):
    return AgentCallback.token_usage(days=days, agent_uuid=agent_uuid)
