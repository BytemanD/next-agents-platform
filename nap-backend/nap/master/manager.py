from typing import Optional

from fastapi import HTTPException
from loguru import logger
from markitdown import MarkItDown
from nap.common.exceptions import KnowledgeAlreadyExists
from nap.db.models import Knowledge
from nap.research.ai import ResearchAI
from nap.storage.manager import get_storage_driver
from nap.vector.manager import get_vector_driver
from pydantic import BaseModel
from pystonic.common import context


class Message(BaseModel):
    role: str = "user"
    content: str = ""
    thinking: str = ""


class MasterManager:
    def __init__(self):
        self.vector_driver = get_vector_driver()
        self.storage_driver = get_storage_driver()
        self.llm = ResearchAI()

    def list_docs(self):
        pid = context.project_id.get()
        if pid:
            return Knowledge.query(Knowledge.project_uuid == pid)
        return Knowledge.query()

    def get_doc_path(self, path: str):
        logger.info("get doc path: {}", path)
        docs = Knowledge.query(Knowledge.file_path == path)
        if not docs:
            return None
        return self.storage_driver.get_path(docs[0])

    def upload_doc(self, filename: str, content: bytes) -> Knowledge:
        """创建 doc 记录， 保存 doc 内容到本地存储"""

        doc = Knowledge(
            project_uuid=context.project_id.get() or "",
            name=filename,
            file_size=len(content),
            file_path="",
            status="pending",
        )
        doc.create()
        self.storage_driver.save(doc, content)
        return doc

    def parse_doc(self, doc_uuid: str):
        doc: Optional[Knowledge] = Doc.get_by_uuid(doc_uuid)
        if not doc:
            logger.warning("parse_doc: doc {} not found, skip", doc_uuid)
            return

        logger.info("parse_doc: start parsing doc {}({})", doc.name, doc_uuid)
        doc.status = "parsing"
        doc.update()
        try:
            self.vector_driver.import_file(doc, self._convert(doc))
            doc.status = "parsed"
            doc.update()
            logger.info("parse_doc: doc {} parsed successfully", doc_uuid)
        except KnowledgeAlreadyExists:
            logger.warning("parse_doc: doc {} already exists in vector store", doc_uuid)
            doc.status = "failed"
            doc.update()
        except Exception:
            logger.exception("parse_doc: doc {} parse failed", doc_uuid)
            doc.status = "failed"
            doc.update()

    def import_doc(self, doc: Knowledge):
        collection = self.vector_driver.import_file()
        storage_driver = get_storage_driver()
        storage_driver.get_content(doc)
        existing = collection.get(doc.uuid)
        if existing.get("ids"):
            raise KnowledgeAlreadyExists("document already exists")

        collection.add(
            ids=[doc.uuid],
            documents=[self._convert(doc)],
            metadatas=[{"file_name": doc.name}],
        )

    def _convert(self, doc: Knowledge):
        if not doc.file_path:
            raise ValueError("doc file_path is required")
        md = MarkItDown()

        logger.info("convert doc: {}", doc)
        result = md.convert(self.storage_driver.get_path(doc))
        return f"---\nsource: {doc.file_path}\n---\n\n{result.text_content}"

    def create_project(self, name: str, description: Optional[str]):
        item = Project(name=name, description=description)
        item.create()
        return item

    def list_project(self):
        return Project.query()

    def delete_project(self, uuid: str):
        db_model = Project.get_by_uuid(uuid)
        if not db_model:
            raise Exception(f"Project {uuid} not found")
        db_model.delete()

    def list_session(self):
        """Project manager"""
        return Session.query()

    def create_session(self, name: str, project: Optional[str]):
        db_project = Project.get_by_uuid(project)
        if not db_project:
            raise Exception(f"Project {project} not found")
        item = Session(project_uuid=project, name=name)
        item.create()
        return item

    def retrival(self, text: str):
        return self.vector_driver.query(text)

    async def delete_session(self, session_id: str):
        session = Session.get_by_uuid(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session.delete()
        await self.llm.clear_session_items(session_id)

    async def llm_query(self, text: str, project_id: str = None):
        return await self.llm.query(text)

    async def list_messages(self, session_id: str = None):
        session = Session.get_by_uuid(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        items = await self.llm.list_messages(session_id=session.uuid)
        messages = []
        for x in items:
            if x.get("role") == "user":
                messages.append(Message(role="user", content=x.get("content")))
            elif x.get("role") == "assistant":
                content = x.get("content") or []
                for content in x.get("content") or []:
                    messages.append(
                        Message(
                            role="assistant",
                            content=content.get("text")
                            if content and content.get("type") == "output_text"
                            else "",
                        )
                    )
        return messages

    async def streaming_llm_query(
        self, text: str, session_id: str = None, model: str = ""
    ):
        if model:
            self.llm.set_model(model)
        async for chunk in self.llm.streaming_query(text, session_id=session_id):
            yield f"data: {chunk}\n\n"

    def get_models(self):
        return self.llm.list_model()


MANAGER = MasterManager()
