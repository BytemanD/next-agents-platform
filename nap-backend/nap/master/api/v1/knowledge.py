import asyncio
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Response
from nap.db.models import Knowledge, KnowledgeStatus, KnowledgeTodo
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/knowledges", tags=["知识"])


class KnowledgeResponse(BaseModel):
    uuid: str
    name: str
    size: int
    status: str
    created_at: datetime
    updated_at: datetime
    enrichment: dict = {}


class KnowledgeCreate(BaseModel):
    knowledge: str
    name: str
    size: int = 0
    path: str | None = None
    status: str = "pending"


class KnowledgeUpdate(BaseModel):
    name: str | None = None
    size: int | None = None
    path: str | None = None
    status: int | None = None


@router.get("")
async def list_knowledge():
    return {"items": Knowledge.query(Knowledge.status != KnowledgeStatus.deleted)}


@router.get("/{uuid}")
async def get_knowledge(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    enrichment = k.get_enrichment()
    data = KnowledgeResponse(
        uuid=k.uuid,
        name=k.name,
        size=k.size,
        status=k.status_name(),
        created_at=k.created_at,
        updated_at=k.updated_at,
        enrichment={
            "keywords": enrichment.keywords,
            "summary": enrichment.summary,
        }
        if enrichment
        else {},
    )
    return data


@router.get("/{uuid}/todos")
async def get_knowledge_todos(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    items = KnowledgeTodo.query(KnowledgeTodo.knowlwdge_uuid == uuid)
    return {"items": items}


@router.get("/{uuid}/content")
async def get_knowledge_content(uuid: str):
    k = Knowledge.get_by_uuid(uuid)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    try:
        content = await asyncio.to_thread(MANAGER.get_knowledge_content, k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(k.name, safe='')}"
        },
    )


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
