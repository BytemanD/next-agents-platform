import asyncio
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from starlette import status
from pystonic.common import context

from nap.db.models import Knowledge, KnowledgeBase
from nap.master.manager import MANAGER

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


@router.get("/{kb_id}/stats", status_code=200)
async def get_kb_stats(kb_id: str):
    return {"total": Knowledge.count(Knowledge.knowledge_base == kb_id)}


@router.get("/{kb_id}/knowledges", status_code=200)
async def list_kb_knowledges(kb_id: str):
    knowledges = Knowledge.query(Knowledge.knowledge_base == kb_id)
    return {"items": knowledges}


@router.post(
    "/{kb_id}/knowledges/file",
    status_code=200,
    summary="添加知识文件",
    description="从本地上传文件并添加到知识库",
)
async def add_knowledge_from_file(kb_id: str, file: UploadFile = File(...)):
    kb = KnowledgeBase.get_by_uuid(kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"knowledge base {kb_id} not found",
        )
    item = await asyncio.to_thread(
        MANAGER.upload_doc,
        kb,
        context.getvar("account") or "guest",
        file.filename or file.file.name,
        await file.read(),
    )
    return item


@router.post(
    "/{kb_id}/knowledges/url",
    status_code=200,
    summary="从网络获取知识",
    description="从网络地址下载文件并添加到知识库",
)
async def add_knowledge_from_url(kb_id: str):
    pass
