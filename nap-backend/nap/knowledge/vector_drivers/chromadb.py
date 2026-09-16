from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_chroma import Chroma
from loguru import logger
from pydantic import BaseModel

from nap.db.models import Knowledge, KnowledgeStatus
from nap.common.conf import CONF


class Collection(BaseModel):
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []


class Document(BaseModel):
    id: str = ""
    metadata: dict = {}


class ChromadbDriver:
    def __init__(self) -> None:
        if CONF.chromadb.data_path:
            self.data_path = Path(CONF.chromadb.data_path)
        else:
            self.data_path = Path(CONF.store, "knowledge")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore = Chroma(
            collection_name="default",
            persist_directory=str(self.data_path),
        )

    def list_knowledges(self):
        docs: list[Document] = []
        collection = Collection.model_validate(self.vectorstore.get())
        for index, id in enumerate(collection.ids):
            docs.append(
                Document(
                    id=id,
                    metadata=collection.metadatas[index],
                )
            )
        return docs

    def add_konwledge(self, knowledge: Knowledge, content: str):
        logger.info("ingest knowledge {}", knowledge)
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        logger.info("{} split ...", knowledge)
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        chunks = md_splitter.split_text(content)
        for chunk in chunks:
            chunk.metadata["knowledge_path"] = knowledge.raw_path
            chunk.metadata["knowledge_id"] = knowledge.uuid

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.vectorstore.add_documents(text_splitter.split_documents(chunks))
        logger.success("{} add documents success", knowledge)

    def delete_knowledge(self, knowledge: Knowledge):
        results = self.vectorstore.get(where={"knowledge_id": knowledge.uuid})
        logger.debug("get vector: {}", results)

        if results.get("ids"):
            logger.info("delete vector by ids: {}", results.get("ids"))
            self.vectorstore.delete(results.get("ids"))

    def retrieve(self, query: str, k: int = 2):
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        for doc, score in results:
            print(f"相似度分数: {score:.4f}")
            print(f"内容: {doc.page_content[:100]}...")
