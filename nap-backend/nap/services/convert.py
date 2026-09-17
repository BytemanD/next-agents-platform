import io

from loguru import logger
from pydantic import BaseModel
import markitdown

from nap.db.models import Knowledge
from nap.services.storage import STORE_SERVICE


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

    def convert(self, knowledge: Knowledge):
        logger.info("convert io")

        content = self.md.convert_stream(
            io.BytesIO(STORE_SERVICE.get_raw(knowledge))
        ).text_content

        STORE_SERVICE.save_convert(knowledge, content)
        return content


CONVERT_SERVICE = ConvertService()
