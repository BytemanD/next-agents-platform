from collections.abc import Sequence

from fastapi import APIRouter
from pydantic import BaseModel

from nap.master.manager import MANAGER

router = APIRouter(prefix="/agent-suggestions", tags=["智能体建议"])


class AgentSugguestionsResponse(BaseModel):
    suggestions: Sequence[str]


@router.get(
    "",
    response_model=AgentSugguestionsResponse,
)
async def list_agent_suggestions(agent: str):
    return AgentSugguestionsResponse(
        suggestions=[x.suggestion for x in MANAGER.get_agent_suggestions(agent)]
    )
