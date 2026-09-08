import os
from pathlib import Path

from loguru import logger
from nap.common.conf import CONF
from nap.db.models import Knowledge


class FSDriver:
    def __init__(self):
        self.path = Path(CONF.storage.fs.path)
        self.path.mkdir(parents=True, exist_ok=True)

    def save(self, doc: Knowledge, content: bytes):
        doc.file_path = str(Path(doc.project_uuid or "default", doc.name))

        abs_path = self.path / doc.file_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        doc.status = "saving"
        doc.update()
        abs_path.write_bytes(content)
        doc.status = "saved"
        doc.update()

    def delete(self, doc: Knowledge):
        abs_path = self.path / doc.file_path

        if not abs_path.exists():
            logger.warning("file {} does not exist", abs_path)

        logger.info("Deleting doc {}")
        os.remove(abs_path)

    def get_content(self, doc: Knowledge):
        abs_path = self.path / doc.file_path
        return abs_path.read_bytes()

    def get_path(self, doc: Knowledge):
        return self.path / doc.file_path
