import os
from pathlib import Path

from loguru import logger
from nap.common.conf import CONF
from nap.db.models import Knowledge, KnowledgeStatus


class FSDriver:
    def __init__(self):
        self.path = Path(CONF.storage.fs.path)
        self.path.mkdir(parents=True, exist_ok=True)

    def save(self, doc: Knowledge, content: bytes):
        file_path = self.path.joinpath(doc.creator or "default", doc.name)

        file_path.parent.mkdir(parents=True, exist_ok=True)
        doc.status = KnowledgeStatus.save_running
        doc.path = str(file_path)
        doc.save()
        file_path.write_bytes(content)
        doc.status = KnowledgeStatus.save_completed
        doc.save()

    def delete(self, doc: Knowledge):
        abs_path = self.path / doc.path

        if not abs_path.exists():
            logger.warning("file {} does not exist", abs_path)

        logger.info("Deleting doc {}")
        os.remove(abs_path)

    def get_content(self, doc: Knowledge):
        abs_path = self.path / doc.path
        return abs_path.read_bytes()

    def get_path(self, doc: Knowledge):
        return self.path / doc.path
