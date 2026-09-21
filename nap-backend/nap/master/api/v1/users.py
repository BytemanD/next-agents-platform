from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.common.utils import hashpw
from nap.db.models import User
from pydantic import BaseModel, SecretStr

router = APIRouter(prefix="/users")


class UserCreate(BaseModel):
    username: str
    password: SecretStr
    email: str | None = None


class UserUpdate(BaseModel):
    account: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    uuid: str
    account: str
    email: str
    created_at: str
    updated_at: str


# @router.get("")
# async def list_users():
#     return {"users": User.query()}


@router.get("/{uuid}")
async def get_user(uuid: str):
    u = User.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.put("/{uuid}")
async def update_user(uuid: str, body: UserUpdate):
    u = User.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if body.account is not None:
        u.account = body.account
    if body.email is not None:
        u.email = body.email

    u.save()
    return u


@router.delete("/{uuid}", status_code=204)
async def delete_user(uuid: str):
    u = User.get_by_uuid(uuid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.delete()


@router.post("")
async def create_user(body: UserCreate):
    u = User.get_by_username(body.username)
    if u:
        raise HTTPException(status_code=400, detail="User already exists")
    u = User(
        username=body.username,
        password=hashpw(body.password.get_secret_value()).decode(),
    )
    u.create()
    return u
