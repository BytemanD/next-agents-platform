from fastapi import APIRouter
from pydantic import BaseModel

from nap.master.manager import MANAGER

router = APIRouter(prefix="/sessions", tags=["会话"])


class SessionUpdate(BaseModel):
    name: str | None = None


class SessionResponse(BaseModel):
    uuid: str
    project_uuid: str
    name: str | None = None
    created_at: str
    updated_at: str


@router.get("")
async def list_sessions(agent: str):
    sessions = await MANAGER.list_agent_sessions(agent)
    return {"sessions": sessions}


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    await MANAGER.delete_agent_session(session_id)


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    messages = await MANAGER.list_agent_messages(session_id)
    return {"messages": messages}
