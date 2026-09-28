import asyncio
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from nap.db.models import Attachment, Knowledge, KnowledgeBase
from nap.master.manager import MANAGER
from pydantic import BaseModel
from pystonic.common import context
from starlette import status

router = APIRouter(prefix="/knowledge-bases", tags=["知识库"])


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


class UploadKnowledgeFromUrl(BaseModel):
    url: str


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
    response_model=Knowledge,
)
async def add_knowledge_from_file(kb_id: str, file: UploadFile = File(...)):
    kb = KnowledgeBase.get_by_uuid(kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"knowledge base {kb_id} not found",
        )
    item = await asyncio.to_thread(
        MANAGER.upload_knowledge,
        kb,
        file.filename or file.file.name,
        await file.read(),
    )
    return item


class UrlKnowledge(BaseModel):
    url: str
    name: str | None = None


class AddKnowledgeRequest(BaseModel):
    web_files: list[UrlKnowledge] = []
    attachments: list[str] = []


class KnowledgesResponse(BaseModel):
    knowledges: list[Knowledge] = []


@router.post(
    "/{kb_id}/knowledges",
    status_code=200,
    summary="从网络获取知识",
    description="从网络地址下载文件并添加到知识库",
    response_model=KnowledgesResponse,
)
async def add_knowledge(kb_id: str, body: AddKnowledgeRequest):
    kb = KnowledgeBase.get_by_uuid(kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"knowledge base {kb_id} not found",
        )
    if not body.web_files and not body.attachments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="urls or attachments is required",
        )

    attachments = []
    for attachment_uuid in body.attachments:
        attachment = Attachment.get_by_uuid(attachment_uuid)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"attachment {attachment_uuid} not found",
            )
        attachments.append(attachment)

    items = []
    for web_file in body.web_files:
        item = await asyncio.to_thread(
            MANAGER.add_knowledge_from_url,
            kb,
            context.getvar("account") or "guest",
            web_file.url,
            name=body.name,
        )
        items.append(item)

    for attachment in attachments:
        item = await asyncio.to_thread(
            MANAGER.add_knowledge_from_attachment, kb, attachment
        )
        items.append(item)

    return KnowledgesResponse(knowledges=items)
