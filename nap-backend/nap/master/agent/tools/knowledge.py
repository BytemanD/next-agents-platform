"""用户使用的工具"""

from langchain.tools import ToolRuntime
from langchain_core.tools import BaseToolkit, tool
from loguru import logger
from sqlmodel import col

from nap.common.exceptions import KnowledgeNotExists
from nap.common.knowledge_client import KnowledgeClient
from nap.db.models import Attachment, Knowledge
from nap.master.agent.context import NapRuntimeContext
from nap.services.convert import CONVERT_SERVICE
from nap.services.storage import STORE_SERVICE

KNOWLEDGE_CLIENT = KnowledgeClient()


@tool
def get_available_knowledge_bases(runtime: ToolRuntime[NapRuntimeContext]):
    """获取本次会话可用的知识库

    当需要获取本次会话可查询的知识库时使用。

    Returns:
        匹配的文档片段列表，每段包含内容和相似度信息。
        如果没有找到相关资料，返回空列表
    """
    return [
        x.model_dump(mode="json", exclude={"id", "created_at", "updated_at"})
        for x in runtime.context.knowledge_bases
    ]


@tool(parse_docstring=True)
def retrival(knowledge_uuid: str, query: str, top_k: int = 3):
    """搜索向量库，返回与查询语义最相关的文档片段。

    当需要回答事实性问题、查找特定信息、或需要引用知识库内容时使用。
    适用于产品文档、技术手册、政策规范等已收录资料的查询。
    不适用于闲聊、计算、或知识库未覆盖的领域。

    Args:
        query: 搜索查询词。建议用完整的自然语言问句，而非零散关键词，
                例如"如何配置数据库连接"比"数据库 配置"效果更好
        top_k: 返回的文档数量，默认 3。问题复杂时可适当增加

    Returns:
        匹配的文档片段列表，每段包含内容和相似度信息。
        如果没有找到相关资料，返回空列表。
    """
    logger.info("retrival for knowledge base: {}", knowledge_uuid)
    docs = KNOWLEDGE_CLIENT.retrival(knowledge_uuid, query, top_k=top_k)
    logger.info(
        "retrival return ({}) docs: {}",
        len(docs),
        [x.model_dump(mode="json", exclude={"content"}) for x in docs],
    )
    return [
        x.model_dump(mode="json")
        for x in KNOWLEDGE_CLIENT.retrival(knowledge_uuid, query, top_k=top_k)
    ]


@tool(parse_docstring=True)
async def list_documents(knowledge_base_uuid: str):
    """列出知识库中的文档。

    从指定的知识库中获取所有文档列表

    Args:
        knowledge_base_uuid: 知识库UUID

    Returns:
        文档列表
    """
    logger.info("list documents for knowledge base: {}", knowledge_base_uuid)
    items = Knowledge.query(Knowledge.knowledge_base == knowledge_base_uuid)
    return [x.model_dump(mode="json") for x in items]


@tool(parse_docstring=True)
async def get_document_content(knowledge_uuid: str, encoding: str = "utf-8"):
    """获取知识库文档内容。

    获取指定知识文档的内容。

    Args:
        knowledge_uuid: 文档UUID
        encoding: 文档编码

    Returns:
        文档内容
    """

    logger.info("list documents for knowledge base: {}", knowledge_uuid)
    items = Knowledge.query(Knowledge.uuid == knowledge_uuid)
    if not items:
        raise KnowledgeNotExists(knowledge_uuid)
    item = items[0]
    return STORE_SERVICE.get_content(item).decode(encoding=encoding)


@tool(parse_docstring=True)
async def get_attachments(runtime: ToolRuntime[NapRuntimeContext]):
    """获取会话附件

    当需要获取会话上下文中的附件列表时使用。
    例如， 用户提问：总结一下这个文档、该文档讲了什么 等等

    Returns:
        附件列表
    """
    logger.info("list attachments with uuid: {}", runtime.context.attachments)
    if not runtime.context.attachments:
        return []
    return [
        x.model_dump(mode="json")
        for x in Attachment.query(
            Attachment.creator == runtime.context.username,
            col(Attachment.uuid).in_(runtime.context.attachments),
        )
    ]


@tool(parse_docstring=True)
async def get_attachment_content(runtime: ToolRuntime[NapRuntimeContext], uuid: str):
    """获取附件内容

    当需要获取会话附件内容时使用。

    Args:
        uuid: 附件UUID

    Returns:
        附件内容或者错误信息
    """
    items = Attachment.query(
        Attachment.creator == runtime.context.username,
        Attachment.uuid == uuid,
    )
    if not items:
        return f"ERROR: attachment {uuid} not exists"
    logger.info("get Attachment content for {}", uuid)
    return CONVERT_SERVICE.convert(items[0], save_convert=False)


@tool(parse_docstring=True)
async def get_document_preview_url(uuid: str):
    """获取文档预览地址

    当需要获取知识文档、附件或者其他文件的预览链接时使用。

    Args:
        uuid: 文档UUID、附件UUID、其他文件UUID

    Returns:
        预览地址,格式： [文件名](地址)
    """
    try:
        item = Knowledge.get_by_uuid(uuid)
        return f"[{item.name}](/knowledges/{uuid})"
    except ValueError:
        pass

    try:
        item = Attachment.get_by_uuid(uuid)
        return f"[{item.name}](/attachments/{uuid})"
    except ValueError:
        pass

    logger.warning("get doc with uuid: {} failed", uuid)
    raise ValueError("doc with uuid: {} not found")


class Toolkit(BaseToolkit):
    """知识库工具集"""

    def get_tools(self) -> list:
        return [
            get_document_preview_url,
            get_available_knowledge_bases,
            retrival,
            list_documents,
            get_document_content,
            get_attachments,
            get_attachment_content,
        ]


TOOLKIT = Toolkit()
