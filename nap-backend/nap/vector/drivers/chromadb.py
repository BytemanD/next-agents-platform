from pathlib import Path
from typing import List, Optional

import chromadb
from loguru import logger
from nap.common.conf import CONF
from nap.common.exceptions import KnowledgeAlreadyExists
from nap.db.models import Knowledge
from nap.vector.models import RetrivalDoc
from pystonic.common import context

DEFAULT_COLLECTION_NAME = "DEFAULT"


class ChromadbDriver:
    def __init__(self):
        db_path = Path(CONF.chromadb.path)
        if not db_path.exists():
            db_path.mkdir(parents=True)
        self.client = chromadb.PersistentClient(path=db_path)

    def _get_collection(self, collection_name: Optional[str] = None):
        return self.client.get_or_create_collection(
            name=collection_name or context.project_id.get() or DEFAULT_COLLECTION_NAME
        )

    def import_file(self, doc: Knowledge, content: str):
        collection = self._get_collection()
        existing = collection.get(doc.uuid)
        if existing.get("ids"):
            raise KnowledgeAlreadyExists("document already exists")

        logger.info("add doc {} to collection {}", doc.file_path, collection.name)
        collection.add(
            ids=[doc.uuid],
            documents=[content],
            metadatas=[{"file_name": doc.name}],
        )

    def list_docs(self):
        logger.info("")
        collection = self._get_collection()
        logger.info("list docs, collection_name={}", collection.name)
        try:
            result = collection.get(include=["metadatas"])
        except Exception as e:
            logger.exception("list docs error, collection_name={}", collection.name)
            raise e

        logger.debug("result: {}", result)
        docs = [
            RetrivalDoc(
                id=doc_id,
                name=(result["metadatas"][index] or {}).pop("file_name", ""),
                metadata=result["metadatas"][index] or {},
            )
            for index, doc_id in enumerate(result["ids"])
            if result["metadatas"] and result["metadatas"][index]
        ]
        logger.success("return {} docs", len(docs))
        return docs

    def query(
        self,
        text: str,
        n_results=1,
        collection_name: Optional[str] = None,
    ) -> List[RetrivalDoc]:
        collection = self._get_collection(collection_name)
        results = collection.query(query_texts=[text], n_results=n_results)
        logger.info(
            "query, collection_name={}, n_results={}", collection_name, n_results
        )
        if not results["ids"]:
            logger.warning("no docs found")
            return []
        docs = [
            RetrivalDoc(
                id=id,
                name=(results["metadatas"][0][index] or {}).get("file_name"),
                metadata=results["metadatas"][0][index] or {},
                distance=results["distances"][0][index] or 0,
                content=results["documents"][0][index] or "",
            )
            for index, id in enumerate(results["ids"][0])
        ]
        logger.success("return {} docs", len(docs))
        return docs
