"""系统内部使用的工具"""

from typing import List

from loguru import logger
from nap.db.models import KnowledgeBase

from langchain.tools import tool, ToolRuntime
from nap.services.vector import VECTOR_SERVICE, Document
from pydantic import BaseModel


class Context(BaseModel):
    knowledge_base: KnowledgeBase | None = None


@tool
def retrival(runtime: ToolRuntime[Context], query: str, top_k: int = 3):
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
    logger.info("retrival for knowledge base:", runtime.context.knowledge_base)
    return VECTOR_SERVICE.retrieval(query, k=top_k)


@tool
async def list_docs() -> List[Document]:
    """列出ChromaDB中的文档

    Returns:
        List[Document]: 文档列表
    """
    return VECTOR_SERVICE.list_knowledges()
