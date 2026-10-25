from fastapi import APIRouter

router = APIRouter(prefix="/knowledges")


# @router.delete("/{uuid}", status_code=204)
# async def delete_knowledge(uuid: str):
#     knw = Knowledge.get_by_uuid(uuid)
#     if not knw:
#         raise HTTPException(status_code=404, detail="Knowledge not found")
#     MANAGER.delete_knowledge_backgroup(knw)
