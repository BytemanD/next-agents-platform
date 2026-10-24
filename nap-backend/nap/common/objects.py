import abc
from typing import Any

from langchain_core.tools.base import BaseTool, BaseToolkit
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    knowledge_id: str | None = ""
    knowledge_path: str | None = ""
    header1: str | None = None
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
        requires: dict[str, Any] = {}
        help: str | None = None

    name: str
    description: str = ""
    extras: Extras = Extras()
    args: dict = {}

    @classmethod
    def from_llm_tool(cls, t: BaseTool):
        return cls(
            name=t.name,
            description=t.description.split()[0],
            extras=cls.Extras.model_validate(t.extras or {}),
            args=t.args,
        )


class Message(BaseModel):
    id: str
    type: str
    content: str | None = None
    thinking: str | None = None


class ToolkitMetadata(BaseModel):
    name: str
    title: str = ""
    type: str = ""
    help: str = ""


class Toolkit(BaseToolkit):
    @classmethod
    @abc.abstractmethod
    def metadata(cls) -> ToolkitMetadata:
        pass

    @abc.abstractmethod
    def get_tools(self) -> list[BaseTool]:
        """获取工具列表"""
