from collections.abc import Sequence

from pystonic.agents.langchain_agent.agent import RuntimeContext

from nap.db.models import KnowledgeBase


class NapRuntimeContext(RuntimeContext):
    username: str

    knowledge_bases: Sequence[KnowledgeBase] = []
    attachments: list[str] | None = None
    selected_model: str = ""
