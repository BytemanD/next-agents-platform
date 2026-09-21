"""系统内部使用的工具"""

from langchain.tools import tool, ToolRuntime
from loguru import logger

from nap.llm.tools.context import RuntimeContext
from nap.common.knowledge_client import KnowledgeClient

KNOWLEDGE_CLIENT = KnowledgeClient()


@tool
def get_available_knowledge_bases(runtime: ToolRuntime[RuntimeContext]):
    """获取本次会话需要可用哪些知识库

    当需要查询知道本次会话可以查询哪些知识库时使用。

    Returns:
        匹配的文档片段列表，每段包含内容和相似度信息。
        如果没有找到相关资料，返回空列表
    """
    return [
        x.model_dump(mode="json", exclude={"id", "created_at", "updated_at"})
        for x in runtime.context.knowledge_bases
    ]


@tool(parse_docstring=True, extras={"title": "向量召回", "type": "search"})
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
    return [
        x.model_dump(mode="json")
        for x in KNOWLEDGE_CLIENT.retrival(knowledge_uuid, query, top_k=top_k)
    ]


@tool(parse_docstring=True, extras={"title": "查看向量库文档", "type": "search"})
async def list_documents(knowledge_uuid: str):
    """列出向量库中的中的文档。

    从向量库中获取所有文档列表

    Args:
        knowledge_uuid: 知识库UUID

    Returns:
        文档列表
    """
    logger.info("list documents for knowledge base: {}", knowledge_uuid)
    return [
        x.model_dump(mode="json")
        for x in KNOWLEDGE_CLIENT.list_documents(knowledge_uuid)
    ]
