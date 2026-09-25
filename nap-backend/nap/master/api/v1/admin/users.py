from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import User
from pydantic import BaseModel, SecretStr

router = APIRouter(prefix="/users", tags=["用户"])


class UserCreate(BaseModel):
    username: str
    password: SecretStr
    email: str | None = None


class UserUpdate(BaseModel):
    account: Optional[str] = None
    email: Optional[str] = None


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
