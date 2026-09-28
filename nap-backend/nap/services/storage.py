import os
from enum import StrEnum
from pathlib import Path

from loguru import logger
from nap.common.conf import CONF
from nap.db.models import Attachment, Knowledge


class StorageSchema(StrEnum):
    local = "local://"


class StorageService:
    def __init__(self):
        self.local_root = Path(CONF.store)
        self.local_root.mkdir(parents=True, exist_ok=True)

    def _real_path(self, file_path: str):
        if file_path.startswith(StorageSchema.local.value):
            file_path = file_path.removeprefix(StorageSchema.local.value)
        return self.local_root / file_path

    def save_raw(self, knowledge: Knowledge, content: bytes | str):
        file_path = f"raw/{knowledge.creator}/{knowledge.name}"
        real_path = self._real_path(file_path)
        real_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            real_path.write_bytes(content)
        else:
            real_path.write_text(content)
        knowledge.raw_path = f"{StorageSchema.local}{file_path}"
        knowledge.save()

    def save_convert(self, knowledge: Knowledge, content: str):
        file_path = f"convert/{knowledge.knowledge_base}/{knowledge.name}"
        real_path = self._real_path(file_path)
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(content)
        knowledge.convert_path = f"{StorageSchema.local}{file_path}"
        knowledge.save()

    def remove(self, knowledge: Knowledge):
        for file_path in [knowledge.raw_path, knowledge.convert_path]:
            if not file_path:
                continue
            real_path = self._real_path(file_path)
            logger.info("remove file {}", real_path)
            if not real_path.exists():
                logger.warning("file {} does not exist", real_path)
                return
            os.remove(real_path)

    def remove_attachment(self, attachment: Attachment):
        paths = [attachment.raw_path, attachment.convert_path]
        for file_path in paths:
            if not file_path:
                continue
            real_path = self._real_path(file_path)
            if not real_path.exists():
                logger.warning("attachment file {} does not exist", real_path)
                continue
            os.remove(real_path)

    def get_raw(self, item: Knowledge | Attachment):
        if not item.raw_path:
            raise ValueError("knowledge raw_path is missing")
        logger.info("get knowledge raw content")
        return self.get_raw_path(item).read_bytes()

    def get_raw_path(self, item: Knowledge | Attachment):
        """"""
        if not item.raw_path:
            raise ValueError("knowledge raw_path is missing")
        return self._real_path(item.raw_path)

    def get_attachment_raw(self, file_key: str) -> bytes:
        real_path = self.local_root / f"tmp/attachments/{file_key}/raw"
        if not real_path.exists():
            raise FileNotFoundError(f"attachment {file_key} does not exist")
        return real_path.read_bytes()

    def get_attachment_path(self, file_key: str) -> Path:
        real_path = self.local_root / f"tmp/attachments/{file_key}/raw"
        if not real_path.exists():
            raise FileNotFoundError(f"attachment {file_key} does not exist")
        return real_path

    def save_attachment_raw(self, attachment: Attachment, content: bytes):
        file_path = f"raw/{attachment.creator}/{attachment.name}"
        real_path = self._real_path(file_path)
        real_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("save attachment: {}({})", attachment.uuid, attachment.name)
        real_path.write_bytes(content)
        attachment.raw_path = f"{StorageSchema.local}{file_path}"
        attachment.save()

    def save_attachment_convert(self, file_key: str, content: str):
        real_path = self.local_root / f"tmp/attachments/{file_key}/convert.txt"
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(content)

    def get_attachment_convert(self, file_key: str) -> str:
        real_path = self.local_root / f"tmp/attachments/{file_key}/convert.txt"
        if not real_path.exists():
            raise FileNotFoundError(f"attachment {file_key} has not been converted")
        return real_path.read_text()

    def save_attachment_name(self, file_key: str, name: str):
        real_path = self.local_root / f"tmp/attachments/{file_key}/name.txt"
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(name)

    def get_attachment_name(self, file_key: str) -> str:
        real_path = self.local_root / f"tmp/attachments/{file_key}/name.txt"
        if not real_path.exists():
            return ""
        return real_path.read_text().strip()

    def has_attachment(self, file_key: str) -> bool:
        return (self.local_root / f"tmp/attachments/{file_key}/raw").exists()


STORE_SERVICE = StorageService()
