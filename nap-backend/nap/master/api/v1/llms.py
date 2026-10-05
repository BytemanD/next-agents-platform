from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import LLMs
from nap.master.manager import MANAGER
from pydantic import BaseModel

router = APIRouter(prefix="/llms", tags=["模型"])


class LLMCreate(BaseModel):
    name: str = ""
    base_url: str
    api_key: str
    models: list[str] = []


class LLMUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    models: Optional[list[str]] = None


class LLMResponse(BaseModel):
    uuid: str
    name: str
    base_url: str
    api_key: str
    models: list[str]
    created_at: str
    updated_at: str


class LLMBrief(BaseModel):
    """不含密钥的 LLM 信息，用于内嵌到其他响应里。

    全部字段都有默认值：agent 指向的 LLM 可能已被删除，此时也要能构造出来。
    """

    uuid: str = ""
    name: str = ""
    base_url: str = ""
    models: list[str] = []


def _to_brief(d: LLMs) -> LLMBrief:
    return LLMBrief(
        uuid=d.uuid,
        name=d.name,
        base_url=d.base_url,
        models=d.models,
    )


def _to_response(d: LLMs) -> LLMResponse:
    return LLMResponse(
        uuid=d.uuid,
        name=d.name,
        base_url=d.base_url,
        api_key=d.api_key,
        models=d.models,
        created_at=d.created_at.isoformat(),
        updated_at=d.updated_at.isoformat(),
    )


@router.get("")
async def list_llms():
    return {"llms": [_to_response(x) for x in LLMs.query()]}


@router.get("/{uuid}")
async def get_llm(uuid: str):
    d = LLMs.get_by_uuid(uuid)
    if not d:
        raise HTTPException(status_code=404, detail="LLM not found")
    return _to_response(d)


@router.post("", status_code=201, response_model=LLMs)
async def create_llm(body: LLMCreate):
    return MANAGER.create_llm(body.name, body.base_url, body.api_key, body.models)


@router.put("/{uuid}")
async def update_llm(uuid: str, body: LLMUpdate):
    d = LLMs.get_by_uuid(uuid)
    if not d:
        raise HTTPException(status_code=404, detail="LLM not found")

    if body.name is not None:
        d.name = body.name
    if body.base_url is not None:
        d.base_url = body.base_url
    if body.api_key is not None:
        d.api_key = body.api_key
    if body.models is not None:
        d.models = body.models

    d.save()
    return _to_response(d)


@router.delete("/{uuid}", status_code=204)
async def delete_llm(uuid: str):
    d = LLMs.get_by_uuid(uuid)
    if not d:
        raise HTTPException(status_code=404, detail="LLM not found")
    d.delete()
