from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile
from nap.db.models import Attachment
from nap.master.manager import MANAGER
from pydantic import BaseModel
from pystonic.common import context

router = APIRouter(prefix="/attachments", tags=["附件"])


class AttachmentItem(BaseModel):
    uuid: str
    name: str
    size: int
    created_at: datetime

    @classmethod
    def from_model(cls, att: Attachment) -> "AttachmentItem":
        return cls(
            uuid=att.uuid,
            name=att.name,
            size=att.size,
            created_at=att.created_at,
        )


class AttachmentResponse(BaseModel):
    attachment: AttachmentItem


class AttachmentListResponse(BaseModel):
    attachments: list[AttachmentItem]


@router.post("", response_model=AttachmentResponse)
async def upload_attachment(file: UploadFile):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    attachment = await MANAGER.save_attachment(file.filename, content)
    return AttachmentResponse(attachment=AttachmentItem.from_model(attachment))


@router.get("", response_model=AttachmentListResponse)
async def list_attachments():
    return AttachmentListResponse(
        attachments=[AttachmentItem.from_model(x) for x in MANAGER.list_attachments()]
    )


@router.delete("/{uuid}", status_code=204)
async def delete_attachment(uuid: str):
    try:
        attachment = Attachment.get_by_uuid(uuid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.creator != context.getvar("account"):
        raise HTTPException(status_code=403, detail="No permission")
    MANAGER.delete_attachment(attachment)
    return None
