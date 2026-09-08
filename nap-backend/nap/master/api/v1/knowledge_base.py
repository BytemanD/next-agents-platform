from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import KnowledgeBase
from pydantic import BaseModel

router = APIRouter(prefix="/knowledge-bases")


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""
    file_size: int = 0
    file_path: Optional[str] = None
    status: str = "pending"


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    file_size: Optional[int] = None
    file_path: Optional[str] = None
    status: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    uuid: str
    name: str
    description: str
    file_size: int
    file_path: Optional[str]
    status: str
    created_at: str
    updated_at: str


def _to_response(kb: KnowledgeBase) -> KnowledgeBaseResponse:
    return KnowledgeBaseResponse(
        uuid=kb.uuid,
        name=kb.name,
        description=kb.description,
        file_size=kb.file_size,
        file_path=kb.file_path,
        status=kb.status,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat(),
    )


@router.get("")
async def list_kbs():
    return {"items": [_to_response(kb) for kb in KnowledgeBase.query()]}


@router.get("/{uuid}")
async def get_kb(uuid: str):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return _to_response(kb)


@router.post("", status_code=201)
async def create_kb(body: KnowledgeBaseCreate):
    kb = KnowledgeBase(
        name=body.name,
        description=body.description,
        file_size=body.file_size,
        file_path=body.file_path,
        status=body.status,
    )
    kb.create()
    return _to_response(kb)


@router.put("/{uuid}")
async def update_kb(uuid: str, body: KnowledgeBaseUpdate):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")

    if body.name is not None:
        kb.name = body.name
    if body.description is not None:
        kb.description = body.description
    if body.file_size is not None:
        kb.file_size = body.file_size
    if body.file_path is not None:
        kb.file_path = body.file_path
    if body.status is not None:
        kb.status = body.status

    kb.save()
    return _to_response(kb)


@router.delete("/{uuid}", status_code=204)
async def delete_kb(uuid: str):
    kb = KnowledgeBase.get_by_uuid(uuid)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    kb.delete()