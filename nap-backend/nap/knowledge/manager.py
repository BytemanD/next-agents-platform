import asyncio
from datetime import UTC, datetime

from loguru import logger
from nap.common.manager import BaseManager
from nap.db.models import Knowledge, KnowledgeBase, KnowledgeStatus
from nap.knowledge.graph import knowledge_process
from nap.services.storage import STORE_SERVICE
from nap.services.vector import VECTOR_SERVICE
from pystonic.infra.messaging.redis import RedisMessaingQueue


class KnowledgeManager(BaseManager):
    def __init__(self) -> None:
        super().__init__()

        self.run_background_job(self.job_process_knowledges, after_seconds=1)
        # self.asyncio_scheduler.add_job(
        #     self.job_delete_knowledges,
        #     "interval",
        #     seconds=10,
        #     max_instances=1,
        #     coalesce=True,
        # )
        self.messaging_driver = RedisMessaingQueue()

    async def stop(self):
        await asyncio.to_thread(self.messaging_driver.shutdown)
        await super().stop()

    def list_documents(
        self,
        knowledge_base: KnowledgeBase | None = None,
        content_width: int | None = None,
    ):
        return VECTOR_SERVICE.list_knowledges()

    def get_document(self, doc_id: str):
        docs = VECTOR_SERVICE.list_knowledges(ids=[doc_id])
        return docs[0] if docs else None

    def job_process_knowledges(self):
        for knowledge in self.messaging_driver.consume(
            "knowledges", response_model=Knowledge
        ):
            if not isinstance(knowledge, Knowledge):
                logger.warning("item {} is not Knowledge, skip", knowledge)
                continue

            if knowledge.status == KnowledgeStatus.pending_delete.value:
                self.backgroup_scheduler.add_job(
                    self.delete_knowledge, args=(knowledge,)
                )
            else:
                self.backgroup_scheduler.add_job(
                    knowledge_process.run, args=(knowledge,)
                )
                knowledge.set_status(KnowledgeStatus.processing)

    def delete_knowledge(self, knowledge: Knowledge):
        knowledge.set_status(KnowledgeStatus.deleting)
        try:
            VECTOR_SERVICE.delete_knowledge(knowledge)
        except:
            logger.exception("delete knowledge vector failed")
            raise
        try:
            STORE_SERVICE.remove(knowledge)
        except:
            logger.exception("remove knowledge storage failed")
            raise
        knowledge.delete()

    def delete_knowledge_backgroup(self, knowledge: Knowledge):
        knowledge.set_status(KnowledgeStatus.deleting)
        self.backgroup_scheduler.add_job(
            self.delete_knowledge, args=(knowledge,), next_run_time=datetime.now(UTC)
        )

    def retrival(self, knowledge_base: KnowledgeBase, query: str, top_k: int = 3):
        logger.info(
            "retrival for knowledge base: {}, query={}, top_k={}",
            knowledge_base.uuid,
            query,
            top_k,
        )
        return VECTOR_SERVICE.retrieval(query, k=top_k)


MANAGER = KnowledgeManager()
