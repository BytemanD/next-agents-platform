from enum import StrEnum

from loguru import logger
from nap.common.conf import CONF
from nap.db.models import Attachment, Knowledge
from pystonic.infra.storage.local import LocalStorage
from pystonic.infra.storage.s3 import S3Storage
from pystonic.utils import funcutil


class StorageSchema(StrEnum):
    local = "local://"
    s3 = "s3://"


class StorageService:
    def __init__(self):
        if CONF.storage.driver == "local":
            self.driver = LocalStorage(CONF.store)
            self.storage_schema = StorageSchema.local.value
        else:
            self.driver = S3Storage()
            self.storage_schema = StorageSchema.s3.value

    # def _real_path(self, file_path: str):
    #     if file_path.startswith(self.storage_schema):
    #         file_path = file_path.removeprefix(self.storage_schema)
    #     return self.local_root / file_path

    def save_raw(self, knowledge: Knowledge, content: bytes | str):
        file_path = f"users/{knowledge.creator}/raw/{knowledge.name}"
        self.driver.write(file_path, content)
        knowledge.raw_path = f"{self.storage_schema}{file_path}"
        knowledge.save()

    def save_convert(self, knowledge: Knowledge, content: str):
        file_path = f"users/{knowledge.creator}/convert/{knowledge.knowledge_base}/{knowledge.name}"
        self.driver.write(file_path, content)
        knowledge.convert_path = f"{self.storage_schema}{file_path}"
        knowledge.save()

    def remove(self, knowledge: Knowledge):
        for file_path in [knowledge.raw_path, knowledge.convert_path]:
            if not file_path:
                continue
            self.driver.delete(file_path.removeprefix(self.storage_schema))

    def remove_attachment(self, attachment: Attachment):
        paths = [attachment.raw_path, attachment.convert_path]
        for file_path in paths:
            if not file_path:
                continue
            self.driver.delete(file_path.removeprefix(self.storage_schema))

    def get_raw(self, item: Knowledge | Attachment):
        if not item.raw_path:
            raise ValueError("knowledge raw_path is missing")
        logger.info("get knowledge raw content")
        return self.driver.read(self.get_raw_path(item))

    def get_raw_path(self, item: Knowledge | Attachment):
        if not item.raw_path:
            raise ValueError("knowledge raw_path is missing")
        return item.raw_path.removeprefix(self.storage_schema)

    # def get_attachment_raw(self, file_key: str) -> bytes:
    #     real_path = self.local_root / f"tmp/attachments/{file_key}/raw"
    #     if not real_path.exists():
    #         raise FileNotFoundError(f"attachment {file_key} does not exist")
    #     return real_path.read_bytes()

    # def get_attachment_path(self, file_key: str) -> Path:
    #     real_path = self.local_root / f"tmp/attachments/{file_key}/raw"
    #     if not real_path.exists():
    #         raise FileNotFoundError(f"attachment {file_key} does not exist")
    #     return real_path

    def save_attachment_raw(self, attachment: Attachment, content: bytes):
        file_path = f"users/{attachment.creator}/attachments/{attachment.name}"
        self.driver.write(file_path, content)
        attachment.raw_path = f"{self.storage_schema}{file_path}"
        attachment.save()

    # def save_attachment_convert(self, file_key: str, content: str):
    #     real_path = self.local_root / f"tmp/attachments/{file_key}/convert.txt"
    #     real_path.parent.mkdir(parents=True, exist_ok=True)
    #     real_path.write_text(content)

    # def has_attachment(self, file_key: str) -> bool:
    #     return (self.local_root / f"tmp/attachments/{file_key}/raw").exists()

    @funcutil.timeit
    def save_text(
        self,
        attachment: Attachment,
        content: str,
        encoding="utf-8-sig",
        overwrite: bool = False,
    ):
        file_path = f"users/{attachment.creator}/attachments/{attachment.name}"
        try:
            self.driver.get_file(file_path)
            raise FileExistsError()
        except FileNotFoundError:
            pass

        logger.info("save attachment: {}({})", attachment.uuid, attachment.name)
        self.driver.write(file_path, content)
        logger.success("write text success")

        attachment.raw_path = f"{self.storage_schema}{file_path}"
        attachment.size = len(content)


STORE_SERVICE = StorageService()
