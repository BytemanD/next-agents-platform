from typing import Literal

from pystonic.common.conf import BaseAppConfig, FrozenBaseModel


class VectorConfig(FrozenBaseModel):
    driver: Literal["chroma", "milvus"] = "chroma"


class ChromaDBConfig(FrozenBaseModel):
    data_path: str | None = None


class FSStorageConfig(FrozenBaseModel):
    path: str = "./data/raw"


class StorageConfig(FrozenBaseModel):
    driver: str = "local"
    fs: FSStorageConfig = FSStorageConfig()


class MasterConfig(FrozenBaseModel):
    knowledge_base_url: str = "http://localhost:8001"


class AppConfig(BaseAppConfig):
    vector: VectorConfig = VectorConfig()
    chromadb: ChromaDBConfig = ChromaDBConfig()
    storage: StorageConfig = StorageConfig()

    master: MasterConfig = MasterConfig()


CONF = AppConfig()
