from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import Knowledge, KnowledgeBase
from pydantic import BaseModel

router = APIRouter(prefix="/knowledge-bases")


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""
    active: bool = True


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class KnowledgeBaseResponse(BaseModel):
    uuid: str
    name: str
    description: str
    active: bool
    created_at: str
    updated_at: str


@router.get("")
async def list_kbs():
    return {"items": KnowledgeBase.query()}


@router.get("/{uuid}")
async def get_kb(uuid: str):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return kb


@router.post("", status_code=201)
async def create_kb(body: KnowledgeBaseCreate):
    kb = KnowledgeBase(
        name=body.name,
        description=body.description,
        active=body.active,
    )
    kb.create()
    return kb


@router.put("/{uuid}")
async def update_kb(uuid: str, body: KnowledgeBaseUpdate):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")

    if body.name is not None:
        kb.name = body.name
    if body.description is not None:
        kb.description = body.description
    if body.active is not None:
        kb.status = body.active

    kb.save()
    return kb


@router.delete("/{uuid}", status_code=204)
async def delete_kb(uuid: str):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    kb.delete()


@router.get("/{kb_id}/stats", status_code=204)
async def get_kb_stats(kb_id: str):
    return {"total": Knowledge.count(Knowledge.knowledge == kb_id)}

@router.get("/{kb_id}/knowledges", status_code=204)
async def list_kb_knowledges(kb_id: str):
    knowledges = Knowledge.query(Knowledge.knowledge == kb_id)
    return {"items": knowledges}