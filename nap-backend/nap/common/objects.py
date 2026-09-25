from langchain_core.tools.base import BaseTool
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    knowledge_id: str | None = ""
    knowledge_path: str | None = ""
    header1: str | None | None = None
    header2: str | None = None
    header3: str | None = None


class RetrivalDocument(BaseModel):
    id: str | None = None
    content: str | None = None
    metadata: DocumentMetadata = DocumentMetadata()
    score: float | None = None


class ToolModel(BaseModel):
    class Extras(BaseModel):
        title: str = ""
        type: str = ""

    name: str
    description: str = ""
    extras: Extras = Extras()
    args: dict = {}

    @classmethod
    def from_llm_tool(cls, t: BaseTool):
        return cls(
            name=t.name,
            description=t.description,
            extras=cls.Extras.model_validate(t.extras or {}),
            args=t.args,
        )
