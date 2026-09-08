from typing import Optional

from pydantic import BaseModel


class Doc(BaseModel):
    file_path: str


class RetrivalDoc(BaseModel):
    id: str
    name: str
    distance: Optional[float] = 0
    content: Optional[str] = ""
    metadata: Optional[dict] = {}
