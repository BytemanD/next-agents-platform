from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from loguru import logger
from nap.db.models import Session
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/sessions")


class SessionCreate(BaseModel):
    project_uuid: str
    name: Optional[str] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = None


class SessionResponse(BaseModel):
    uuid: str
    project_uuid: str
    name: Optional[str] = None
    created_at: str
    updated_at: str


def _to_response(d: Session) -> SessionResponse:
    return SessionResponse(
        uuid=d.uuid,
        project_uuid=d.project_uuid,
        name=d.name,
        created_at=d.created_at.isoformat(),
        updated_at=d.updated_at.isoformat(),
    )


@router.get("")
async def list_sessions(x_project_id: str = Header(None)):
    logger.info("list sessions with project: {}", x_project_id)
    sessions = Session.get_by_project(x_project_id)
    return {"sessions": sessions}


@router.get("/{uuid}")
async def get_session(uuid: str):
    session = Session.get_by_uuid(uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _to_response(session)


@router.post("", status_code=201)
async def create_session(body: SessionCreate, x_project_id: str = Header(None)):
    session = Session(project_uuid=x_project_id, name=body.name)
    session.create()
    logger.success("created session: {} with project: {}", session.uuid, x_project_id)
    return _to_response(session)


@router.put("/{uuid}")
async def update_session(uuid: str, body: SessionUpdate):
    session = Session.get_by_uuid(uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if body.name is not None:
        session.name = body.name

    session.update()
    return _to_response(session)


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    await MANAGER.delete_session(session_id)


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    messages = await MANAGER.list_messages(session_id)
    return {"messages": messages}
