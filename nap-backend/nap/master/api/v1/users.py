from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import Users
from pydantic import BaseModel

router = APIRouter(prefix="/users")


class UserCreate(BaseModel):
    account: str
    email: str


class UserUpdate(BaseModel):
    account: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    uuid: str
    account: str
    email: str
    created_at: str
    updated_at: str


def _to_response(u: Users) -> UserResponse:
    return UserResponse(
        uuid=u.uuid,
        account=u.account,
        email=u.email,
        created_at=u.created_at.isoformat(),
        updated_at=u.updated_at.isoformat(),
    )


@router.get("")
async def list_users():
    return {"users": [_to_response(u) for u in Users.query()]}


@router.get("/{uuid}")
async def get_user(uuid: str):
    u = Users.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(u)


@router.post("", status_code=201)
async def create_user(body: UserCreate):
    u = Users(account=body.account, email=body.email)
    u.create()
    return _to_response(u)


@router.put("/{uuid}")
async def update_user(uuid: str, body: UserUpdate):
    u = Users.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if body.account is not None:
        u.account = body.account
    if body.email is not None:
        u.email = body.email

    u.save()
    return _to_response(u)


@router.delete("/{uuid}", status_code=204)
async def delete_user(uuid: str):
    u = Users.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.delete()