from fastapi import APIRouter
from nap.db.models import AgentCallback

router = APIRouter(prefix="/monitoring")


@router.get("/token-usage")
async def token_usage(days: int = 7):
    return AgentCallback.token_usage(days=days)
