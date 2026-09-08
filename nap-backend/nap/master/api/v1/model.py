from fastapi import APIRouter
from nap.master.manager import MANAGER

router = APIRouter(prefix="/models")


@router.get("")
async def query():
    return {"models": MANAGER.get_models()}
