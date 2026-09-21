from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_chroma import Chroma
from loguru import logger
from nap.common.objects import DocumentMetadata, RetrivalDocument
from pydantic import BaseModel
from langchain_core.documents import Document as RawDocument
from nap.db.models import Knowledge
from nap.common.conf import CONF


class Collection(BaseModel):
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []


class VectorService:
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

    def list_knowledges(self, ids: list[str] | None = None):
        docs: list[RetrivalDocument] = []
        collection = Collection.model_validate(self.vectorstore.get(ids))
        for index, id in enumerate(collection.ids):
            docs.append(
                RetrivalDocument(
                    id=id,
                    metadata=DocumentMetadata.model_validate(
                        collection.metadatas[index]
                    ),
                    content=collection.documents[index],
                )
            )
        return docs

    def add_konwledge(self, knowledge: Knowledge, content: str):
        logger.info("ingest knowledge {}", knowledge)
        if len(content) >= 1000:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            logger.info("{} split ...", knowledge)
            md_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on, strip_headers=False
            )
            chunks = md_splitter.split_text(content)
            for chunk in chunks:
                chunk.metadata["knowledge_path"] = knowledge.raw_path
                chunk.metadata["knowledge_id"] = knowledge.uuid
                chunk.metadata["knowledge_name"] = knowledge.name

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
            )
            self.vectorstore.add_documents(text_splitter.split_documents(chunks))
        else:
            self.vectorstore.add_documents(
                [
                    RawDocument(
                        page_content=content,
                        metadata={
                            "knowledge_id": knowledge.uuid,
                            "knowledge_path": knowledge.raw_path,
                            "knowledge_name": knowledge.name,
                        },
                    )
                ]
            )
        logger.success("{} add documents success", knowledge)

    def delete_knowledge(self, knowledge: Knowledge):
        results = self.vectorstore.get(where={"knowledge_id": knowledge.uuid})
        logger.debug("get vector: {}", results)

        if results.get("ids"):
            logger.info("delete vector by ids: {}", results.get("ids"))
            self.vectorstore.delete(results.get("ids"))

    def retrieval(self, query: str, k: int = 3):
        logger.info("retrival({}): {}", k, query)
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        # print(results)
        # self.vectorstore.as_retriever()
        # results2 = self.vectorstore.similarity_search(query)
        # print(results2)
        return [
            RetrivalDocument(
                score=score,
                content=doc.page_content,
                metadata=DocumentMetadata.model_validate(doc.metadata),
            )
            for doc, score in results
        ]


VECTOR_SERVICE = VectorService()
