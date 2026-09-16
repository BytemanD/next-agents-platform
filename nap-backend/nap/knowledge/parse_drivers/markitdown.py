from loguru import logger
from nap.common.exceptions import KnowledgeProcessFailed
from pydantic import BaseModel
import markitdown

from nap.db.models import Knowledge, KnowledgeStatus


class Collection(BaseModel):
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []


class Document(BaseModel):
    id: str = ""
    path: str = ""
    content: str = ""


class MarkitdownDriver:
    def __init__(self) -> None:
        self.md = markitdown.MarkItDown()

    def convert(self, file_path: str):
        logger.info("convert file {}", file_path)
        content = self.md.convert(file_path).text_content
        return content
