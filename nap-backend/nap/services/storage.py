from enum import StrEnum
import os
from pathlib import Path

from loguru import logger
from nap.common.conf import CONF


from nap.db.models import Knowledge


class StorageSchema(StrEnum):
    local = "local://"


class StorageService:
    def __init__(self):
        self.local_root = Path(CONF.store)
        self.local_root.mkdir(parents=True, exist_ok=True)

    def _read_path(self, file_path: str):
        if file_path.startswith(StorageSchema.local.value):
            file_path = file_path.removeprefix(StorageSchema.local.value)
        return self.local_root / file_path

    def save_raw(self, knowledge: Knowledge, content: bytes | str):
        file_path = f"raw/{knowledge.creator}/{knowledge.name}"
        real_path = self._read_path(file_path)
        real_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            real_path.write_bytes(content)
        else:
            real_path.write_text(content)
        knowledge.raw_path = f"{StorageSchema.local}{file_path}"
        knowledge.save()

    def save_convert(self, knowledge: Knowledge, content: str):
        file_path = f"convert/{knowledge.knowledge_base}/{knowledge.name}"
        real_path = self._read_path(file_path)
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(content)
        knowledge.convert_path = f"{StorageSchema.local}{file_path}"
        knowledge.save()

    def remove(self, knowledge: Knowledge):
        for file_path in [knowledge.raw_path, knowledge.convert_path]:
            if not file_path:
                continue
            real_path = self._read_path(file_path)
            logger.info("remove file {}", real_path)
            if not real_path.exists():
                logger.warning("file {} does not exist", real_path)
                return
            os.remove(real_path)

    def get_raw(self, knowledge: Knowledge):
        if not knowledge.raw_path:
            raise ValueError("knowledge raw_path is missing")
        return self.get_raw_path(knowledge).read_bytes()

    def get_raw_path(self, knowledge: Knowledge):
        """"""
        if not knowledge.raw_path:
            raise ValueError("knowledge raw_path is missing")
        return self._read_path(knowledge.raw_path)


STORE_SERVICE = StorageService()
