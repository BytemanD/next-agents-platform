from fastapi import APIRouter, HTTPException

from nap.db.models import KnowledgeBase
from nap.knowledge.manager import MANAGER
from nap.services.vector import RetrivalDocument
from pydantic import BaseModel
from starlette import status


router = APIRouter(prefix="/retrival", tags=["向量召回"])


class PostRetrival(BaseModel):
    query: str
    knowledge_base: str
    top_k: int = 3
    score_threshold: float = 1


class PostRetrivalResp(BaseModel):
    documents: list[RetrivalDocument] = []


@router.post(
    "", status_code=200, description="文档召回", response_model=PostRetrivalResp,
    response_model_exclude_none=True,
)
async def retrival(body: PostRetrival):
    try:
        kb = KnowledgeBase.get_by_uuid(body.knowledge_base)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="knowledge base not found"
        )
    results = MANAGER.retrival(kb, body.query, top_k=body.top_k)
    return PostRetrivalResp(
        documents=[x for x in results if (x.score and x.score <= body.score_threshold)]
    )
