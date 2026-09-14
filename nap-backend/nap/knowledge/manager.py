import asyncio
from collections import defaultdict
import socket
from typing import Sequence

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
import portalocker

from nap.common.conf import CONF
from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.drivers.chromadb import ChromadbDriver
from nap.knowledge.parse_drivers.markitdown import MarkitdownDriver


def get_vector_driver():
    if CONF.vector.driver == "chromadb":
        return ChromadbDriver()

    raise Exception(f"{CONF.vector.driver} is not supported")


class KnowledgeManager:
    def __init__(self) -> None:
        self.hostname = socket.gethostname()
        self.vector_driver = get_vector_driver()
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.job_handle_saved, "interval", seconds=10)

        self.backgroup_scheduler = BackgroundScheduler()
        self.parse_driver = MarkitdownDriver()

    def start(self):
        self.scheduler.start()
        self.backgroup_scheduler.start()

    def list_documents(self, content_width: int | None = None):
        return self.vector_driver.list_knowledges()

    def _batch_update_knowledge_status(self, items: Sequence[Knowledge]):
        status_items = defaultdict(list)
        for item in items:
            if item.status == KnowledgeStatus.save_completed.value:
                item.status = KnowledgeStatus.parse_pending.value
            elif item.status == KnowledgeStatus.delete.value:
                item.status = KnowledgeStatus.delete_pending.value
            status_items[item.status].append(item.uuid)

        for status, uuids in status_items.items():
            logger.info("update {} knowledge(s) status to {}", len(uuids), status)
            Knowledge.batch_set_status(uuids, status)

    async def job_handle_saved(self):
        items = []
        if CONF.db.is_sqlite():
            db_file = CONF.db.url.lstrip("sqlite:///")
            logger.info("get lock ...")
            with portalocker.Lock(db_file + ".lock"):
                items = await asyncio.to_thread(Knowledge.get_todo)
                await asyncio.to_thread(self._batch_update_knowledge_status, items)

        logger.info("found {} knowledge(s) to handle", len(items))
        for item in items:
            self.backgroup_scheduler.add_job(self._handle_knowledge, args=(item,))

    def _handle_knowledge(self, knowledge: Knowledge):
        if knowledge.status == KnowledgeStatus.parse_pending.value:
            content = self.parse_driver.parse(knowledge)
            self.vector_driver.add_konwledge(knowledge, content)
            return
        if knowledge.status == KnowledgeStatus.delete_pending.value:
            self.vector_driver.delete_knowledge(knowledge)
            if knowledge.status == KnowledgeStatus.delete_completed.value:
                knowledge.delete()


MANAGER = KnowledgeManager()
