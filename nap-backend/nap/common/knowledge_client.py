from nap.common.conf import CONF
from nap.common.objects import RetrivalDocument
from pystonic.utils.httpclient import default_client


class KnowledgeClient:
    def __init__(self) -> None:
        self.client = default_client(
            base_url=CONF.master.knowledge_base_url,
            raise_for_status=True,
        )

    def retrival(self, knowledge_base: str, query: str, top_k=10):
        resp = self.client.post(
            "/api/v1/retrival",
            json={
                "knowledge_base": knowledge_base,
                "query": query,
                "top_k": top_k,
            },
        )
        return [
            RetrivalDocument.model_validate(x) for x in resp.json().get("documents", [])
        ]

    def list_documents(self, knowledge_base: str):
        resp = self.client.get(
            "/api/v1/documents", headers={"x-knowledge-base": knowledge_base}
        )
        return [
            RetrivalDocument.model_validate(x) for x in resp.json().get("documents", [])
        ]

    def get_document(
        self,
        knowledge_base: str,
        doc_id: str,
    ):
        resp = self.client.get(f"/api/v1/documents/{doc_id}")
        resp = self.client.get(
            "/api/v1/documents", headers={"x-knowledge-base": knowledge_base}
        )
        return RetrivalDocument.model_validate(resp.json().get("document", {}))
