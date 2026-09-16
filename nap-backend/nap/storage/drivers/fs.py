import os
from pathlib import Path

from loguru import logger
from nap.common.conf import CONF
from nap.db.models import Knowledge


class FSDriver:
    def __init__(self):
        self.root_path = Path(CONF.store)
        self.root_path.mkdir(parents=True, exist_ok=True)

    def save(self, file_path: str, content: bytes | str):
        save_path = self.root_path.joinpath(file_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            save_path.write_bytes(content)
        else:
            save_path.write_text(content)
        return save_path

    def delete(self, doc: Knowledge):
        if not doc.raw_path:
            logger.warning('knowledge {} raw_path is empty')
            return
        abs_path = self.root_path.joinpath(doc.raw_path)

        if not abs_path.exists():
            logger.warning("file {} does not exist", abs_path)

        logger.info("Deleting doc {}")
        os.remove(abs_path)

    def get_content(self, doc: Knowledge):
        if not doc.raw_path:
            raise FileExistsError('knowledge raw_path is empty')
        abs_path = self.root_path / doc.raw_path
        return abs_path.read_bytes()

    def get_path(self, file_path: str):
        return self.root_path / file_path
