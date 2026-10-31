from loguru import logger

from nap.common.conf import CONF
from nap.db.models import Knowledge, KnowledgeBase


class VectorService:
    def __init__(self) -> None:
        if CONF.vector.driver == "milvus":
            from pystonic.infra.vector.milus import MilvusVector

            self.driver = MilvusVector()
        else:
            from pystonic.infra.vector.chroma import ChromaVector

            self.driver = ChromaVector()

    def list_knowledges(
        self, knowledge_base: KnowledgeBase, ids: list[str] | None = None
    ):
        if not ids:
            return self.driver.list_documents(
                collection=knowledge_base.collection_name()
            )

        docs = []
        for id in ids:
            docs.extend(self.driver.list_documents(metadata={"knowledge_id": id}))
        return docs

    def add_konwledge(self, knowledge: Knowledge, content: str):
        self.driver.add_document(
            content,
            collection=knowledge.collection_name(),
            metadata={"knowledge_id": knowledge.uuid, "knowledge_name": knowledge.name},
        )
        logger.success("{} add document success", knowledge.uuid)

    def delete_knowledge(self, knowledge: Knowledge):
        docs = self.driver.list_documents(
            metadata={"knowledge_id": knowledge.uuid},
            collection=knowledge.collection_name(),
        )
        for doc in docs:
            if not doc.id:
                continue
            logger.debug("delete vector document by id: {}", doc.id)
            self.driver.delete_document(doc.id, collection=knowledge.collection_name())

        logger.success("delete knowledge({}) success", knowledge)

    def retrieval(self, knowledge_base: KnowledgeBase, query: str, k: int = 3):
        logger.info("retrival(k={}): {}", k, query)
        return self.driver.retrieval(
            query, k=k, collection=knowledge_base.collection_name()
        )


VECTOR_SERVICE = VectorService()
