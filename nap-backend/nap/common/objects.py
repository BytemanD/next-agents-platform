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
