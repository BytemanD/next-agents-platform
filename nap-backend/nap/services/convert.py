import io

import markitdown
from loguru import logger
from nap.db.models import Attachment, Knowledge
from nap.services.storage import STORE_SERVICE
from pydantic import BaseModel


class Collection(BaseModel):
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []


class Document(BaseModel):
    id: str = ""
    metadata: dict = {}


class ConvertService:
    def __init__(self) -> None:
        self.md = markitdown.MarkItDown()

    def convert(
        self,
        knowledge: Knowledge | Attachment,
        raw_content: bytes | None = None,
        save_convert: bool = True,
    ):
        raw_content = raw_content or STORE_SERVICE.get_raw(knowledge)
        logger.info("convert io")
        content = self.md.convert_stream(io.BytesIO(raw_content)).text_content
        if save_convert:
            STORE_SERVICE.save_convert(knowledge, content)
        return content

    def convert_bytes_to_text(self, content: bytes, name: str = ""):
        """将文件内容转为纯文本（用于会话临时附件，不入知识库）"""
        logger.info("convert attachment bytes")
        return self.md.convert_stream(io.BytesIO(content)).text_content


CONVERT_SERVICE = ConvertService()
