from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, SecretStr
from pystonic.common import context

from nap.common.utils import hashpw
from nap.db.models import User

router = APIRouter(prefix="/users", tags=["用户"])


class UserCreate(BaseModel):
    username: str
    password: SecretStr
    email: str | None = None


class UserUpdate(BaseModel):
    account: str | None = None
    email: str | None = None


class UserResponse(BaseModel):
    uuid: str
    username: str
    email: str | None = None
    created_at: datetime | None
    updated_at: datetime | None


@router.get("/me", response_model=UserResponse)
async def get_user():
    u = User.get_by_username(context.getvar("account") or "")
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
