from typing import Sequence

from nap.db.models import KnowledgeBase
from pydantic import BaseModel


class RuntimeContext(BaseModel):
    knowledge_bases: Sequence[KnowledgeBase] = []
