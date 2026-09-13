from nap.common.conf import CONF
from nap.vector.drivers.chromadb import ChromadbDriver
from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.drivers.chromadb import ChromadbDriver


def get_vector_driver():
    if CONF.vector.driver == "chromadb":
        return ChromadbDriver()

    raise Exception(f"{CONF.vector.driver} is not supported")


class KnowledgeManager:
    def __init__(self) -> None:
        self.driver = get_vector_driver()

    def list_documents(self, content_width: int | None = None):
        return self.driver.list_knowledges()

    def handle_saved(self):
        items = Knowledge.query(Knowledge.status == KnowledgeStatus.saved.value)
        for item in items:
            self.driver.add_konwledge(item)


MANAGER = KnowledgeManager()
