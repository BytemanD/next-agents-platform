from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import Knowledge, KnowledgeStatus
from pydantic import BaseModel

from nap.master.manager import MANAGER

router = APIRouter(prefix="/knowledges")


class KnowledgeCreate(BaseModel):
    knowledge: str
    name: str
    size: int = 0
    path: Optional[str] = None
    status: str = "pending"


class KnowledgeUpdate(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    path: Optional[str] = None
    status: Optional[int] = None


class KnowledgeResponse(BaseModel):
    uuid: str
    knowledge: str
    name: str
    size: int
    path: Optional[str]
    status: str
    created_at: str
    updated_at: str


@router.get("")
async def list_knowledge():
    return {
        "items": Knowledge.query(Knowledge.status != KnowledgeStatus.delete_completed)
    }


@router.get("/{uuid}")
async def get_knowledge(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return k


@router.put("/{uuid}")
async def update_knowledge(uuid: str, body: KnowledgeUpdate):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")

    if body.name is not None:
        k.name = body.name
    if body.size is not None:
        k.size = body.size
    if body.path is not None:
        k.path = body.path
    if body.status is not None:
        k.status = body.status

    k.save()
    return k


@router.delete("/{uuid}", status_code=204)
async def delete_knowledge(uuid: str):
    khm = Knowledge.get_by_uuid(uuid)
    if not khm:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    MANAGER.delete_knowledge(khm)
