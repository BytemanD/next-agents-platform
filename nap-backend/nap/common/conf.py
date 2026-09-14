from pydantic import BaseModel
from pystonic.common.conf import BaseAppConfig


class VectorConfig(BaseModel):
    driver: str = "chromadb"


class ChromaDBConfig(BaseModel):
    data_path: str | None = None


class FSStorageConfig(BaseModel):
    path: str = "./data/raw"


class StorageConfig(BaseModel):
    driver: str = "fs"
    fs: FSStorageConfig = FSStorageConfig()


class AppConfig(BaseAppConfig):
    vector: VectorConfig = VectorConfig()
    chromadb: ChromaDBConfig = ChromaDBConfig()
    storage: StorageConfig = StorageConfig()


CONF = AppConfig()
