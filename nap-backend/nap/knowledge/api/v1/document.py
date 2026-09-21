from fastapi import APIRouter, HTTPException, Header

from nap.common.exceptions import DocumentNotFound
from nap.db.models import KnowledgeBase
from nap.knowledge.manager import MANAGER
from nap.services.vector import RetrivalDocument
from pydantic import BaseModel
from starlette import status


router = APIRouter(prefix="/documents", tags=["向量库文档"])


class GetDocumentResp(BaseModel):
    document: RetrivalDocument


class ListDocumentResp(BaseModel):
    documents: list[RetrivalDocument]


@router.get(
    "",
    status_code=200,
    description="获取知识库向量中所有文档",
    response_model=ListDocumentResp,
    response_model_exclude_none=True,
)
async def list_documents(x_knowedge_id=Header()):
    try:
        kb = KnowledgeBase.get_by_uuid(x_knowedge_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="knowledge base not found"
        )

    items = MANAGER.list_documents(kb)
    return {"documents": items}


@router.get(
    "/{doc_id}",
    status_code=200,
    description="获取知识库向量中所有文档",
    response_model=GetDocumentResp,
    response_model_exclude_none=True,
)
async def get_document(doc_id: str, x_knowedge_id=Header()):
    item = MANAGER.get_document(doc_id)
    if not item:
        raise DocumentNotFound(doc_id)
    return {"document": item}
