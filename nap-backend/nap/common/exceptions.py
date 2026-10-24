class KnowledgeBaseAlreadyExists(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"KnowledgeBase({name}) alredy exists")


class KnowledgeAlreadyExists(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"knowledge {name} alredy exists")


class AgentNotExists(Exception):
    def __init__(self, agent_uuid: str) -> None:
        super().__init__(f"agnet {agent_uuid} not found")


class LLMNotExists(Exception):
    def __init__(self, llm_uuid: str) -> None:
        super().__init__(f"LLM {llm_uuid} not found")


class LLMIsInvalid(Exception):
    def __init__(self, llm_uuid: str) -> None:
        super().__init__(f"LLM {llm_uuid} is invalid")


class LLMRateLimitError(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(f"LLM API rate limit: {detail}")


class EnrichFailed(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(f"enrich document failed: {detail}")


class EnrichmentAlreadyExists(Exception):
    def __init__(self, knowledge_uuid: str) -> None:
        super().__init__(f"knowledge({knowledge_uuid}) enrichment already exists")


class KnowledgeProcessFailed(Exception):
    def __init__(self, knowledge_uuid: str, detail: str) -> None:
        super().__init__(f"knowledge({knowledge_uuid}) process faield: {detail}")


class DocumentNotFound(Exception):
    def __init__(self, doc_id: str) -> None:
        super().__init__(f"document({doc_id}) not exists")


class AuthFailed(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(f"invalid token: {detail}")


class AttachmentNotExists(Exception):
    def __init__(self, uuid: str) -> None:
        super().__init__(f"Attachment {uuid} not exists")


class NoPermission(Exception):
    def __init__(self, detail: str = "No permission") -> None:
        super().__init__(detail)
