from typing import Optional

from fastapi import APIRouter
from nap.db.models import Session
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["会话"])


class SessionUpdate(BaseModel):
    name: Optional[str] = None


class SessionResponse(BaseModel):
    uuid: str
    project_uuid: str
    name: Optional[str] = None
    created_at: str
    updated_at: str


@router.get("")
async def list_sessions(agent: str):
    sessions = await MANAGER.list_sessions(agent)
    return {"sessions": sessions}


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    await MANAGER.delete_session(session_id)


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    messages = await MANAGER.list_messages(Session.get_by_uuid(session_id))
    return {"messages": messages}
