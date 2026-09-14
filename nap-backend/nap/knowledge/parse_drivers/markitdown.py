from loguru import logger
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

    def parse(self, knowledge: Knowledge):
        logger.info("ingest knowledge {}", knowledge)

        logger.info("{} parsing ...", knowledge)
        knowledge.set_status(KnowledgeStatus.save_running)
        content = self.md.convert(knowledge.path).text_content
        knowledge.set_status(KnowledgeStatus.parse_completed)
        return content
