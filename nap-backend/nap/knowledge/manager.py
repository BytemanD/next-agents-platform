import asyncio
from datetime import UTC, datetime

from loguru import logger
from nap.common.manager import BaseManager
from nap.knowledge.graph import knowledge_process
import portalocker

from nap.common.conf import CONF
from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.vector_drivers.chromadb import ChromadbDriver
from nap.knowledge.parse_drivers.markitdown import MarkitdownDriver


def get_vector_driver():
    if CONF.vector.driver == "chromadb":
        return ChromadbDriver()

    raise Exception(f"{CONF.vector.driver} is not supported")


class KnowledgeManager(BaseManager):
    def __init__(self) -> None:
        super().__init__()
        self.vector_driver = get_vector_driver()

        self.asyncio_scheduler.add_job(
            self.job_process_knowledges, "interval", seconds=10
        )
        self.asyncio_scheduler.add_job(
            self.job_delete_knowledges, "interval", seconds=10
        )

        self.parse_driver = MarkitdownDriver()

    def list_documents(self, content_width: int | None = None):
        return self.vector_driver.list_knowledges()

    async def job_process_knowledges(self):
        items = []
        if CONF.db.is_sqlite():
            db_file = CONF.db.url.lstrip("sqlite:///")
            logger.info("get lock ...")
            with portalocker.Lock(db_file + ".process.lock"):
                items = await asyncio.to_thread(Knowledge.get_pending_process)
                Knowledge.batch_set_status(
                    [x.uuid for x in items], KnowledgeStatus.processing.value
                )

        logger.info("found {} knowledge(s) to process", len(items))
        for item in items:
            self.backgroup_scheduler.add_job(knowledge_process.run, args=(item,))

    async def job_delete_knowledges(self):
        items = []
        if CONF.db.is_sqlite():
            db_file = CONF.db.url.lstrip("sqlite:///")
            logger.info("get lock ...")
            with portalocker.Lock(db_file + ".delete.lock"):
                items = await asyncio.to_thread(Knowledge.get_pending_delete)
                Knowledge.batch_set_status(
                    [x.uuid for x in items], KnowledgeStatus.deleting.value
                )

        logger.info("found {} knowledge(s) to delete", len(items))
        for item in items:
            await asyncio.to_thread(self.delete_knowledge, item)

    def delete_knowledge(self, knowledge: Knowledge):
        try:
            self.vector_driver.delete_knowledge(knowledge)
        except:
            logger.exception("delete vector failed")
            raise
        else:
            knowledge.delete()

    def delete_knowledge_backgroup(self, knowledge: Knowledge):
        knowledge.set_status(KnowledgeStatus.deleting)
        self.backgroup_scheduler.add_job(
            self.delete_knowledge, args=(knowledge,), next_run_time=datetime.now(UTC)
        )


MANAGER = KnowledgeManager()
