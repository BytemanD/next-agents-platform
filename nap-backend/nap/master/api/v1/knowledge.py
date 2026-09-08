from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import Knowledge
from pydantic import BaseModel

router = APIRouter(prefix="/knowledge")


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
    status: Optional[str] = None


class KnowledgeResponse(BaseModel):
    uuid: str
    knowledge: str
    name: str
    size: int
    path: Optional[str]
    status: str
    created_at: str
    updated_at: str


def _to_response(k: Knowledge) -> KnowledgeResponse:
    return KnowledgeResponse(
        uuid=k.uuid,
        knowledge=k.knowledge,
        name=k.name,
        size=k.size,
        path=k.path,
        status=k.status,
        created_at=k.created_at.isoformat(),
        updated_at=k.updated_at.isoformat(),
    )


@router.get("")
async def list_knowledge():
    return {"items": [_to_response(k) for k in Knowledge.query()]}


@router.get("/{uuid}")
async def get_knowledge(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return _to_response(k)


@router.post("", status_code=201)
async def create_knowledge(body: KnowledgeCreate):
    k = Knowledge(
        knowledge=body.knowledge,
        name=body.name,
        size=body.size,
        path=body.path,
        status=body.status,
    )
    k.create()
    return _to_response(k)


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
    return _to_response(k)


@router.delete("/{uuid}", status_code=204)
async def delete_knowledge(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    k.delete()