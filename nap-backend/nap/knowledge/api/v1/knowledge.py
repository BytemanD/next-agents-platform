from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.manager import MANAGER

router = APIRouter(prefix="/knowledges")


@router.delete("/{uuid}", status_code=204)
async def delete_knowledge(uuid: str):
    knw = Knowledge.get_by_uuid(uuid)
    if not knw:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    MANAGER.delete_knowledge(knw)
