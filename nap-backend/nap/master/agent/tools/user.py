"""用户使用的工具"""

import httpx
from langchain.tools import ToolRuntime, tool
from loguru import logger
from nap.common.knowledge_client import KnowledgeClient
from nap.db.models import Attachment
from nap.master.agent.context import RuntimeContext
from nap.services.convert import CONVERT_SERVICE
from sqlmodel import col

KNOWLEDGE_CLIENT = KnowledgeClient()


@tool
def get_username(runtime: ToolRuntime[RuntimeContext]):
    """获取当前用户名

    当需要获取当前用户名时使用。

    Returns:
        用户名
    """
    return runtime.context.username


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


@tool(parse_docstring=True, extras={"title": "向量召回", "type": "file_search"})
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


@tool(parse_docstring=True, extras={"title": "查看向量库文档", "type": "file_search"})
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


@tool(parse_docstring=True, extras={"title": "查看向量库文档", "type": "search"})
async def get_attachments(runtime: ToolRuntime[RuntimeContext]):
    """获取会话附件

    当需要获取会话上下文中的附件列表时使用。
    例如， 用户提问：总结一下这个文档、该文档讲了什么 等等

    Returns:
        附件列表
    """
    logger.info("list attachments with uuid: {}", runtime.context.attachments)
    return [
        x.model_dump(mode="json")
        for x in Attachment.query(
            Attachment.creator == runtime.context.username,
            col(Attachment.uuid).in_(runtime.context.attachments),
        )
    ]


@tool(parse_docstring=True, extras={"title": "查看向量库文档", "type": "search"})
async def get_attachment_content(runtime: ToolRuntime[RuntimeContext], uuid: str):
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


@tool(
    parse_docstring=True,
    extras={
        "title": "网络搜索(TavilyHub)",
        "type": "web_search",
        "requires": {"api_key": {"type": "string"}},
        "help": (
            "该工具需要需要在 TavilyHub 注册账号并创建API_KEY。"
            "官网: https://tavily.sharyuke.com/dashboard"
        ),
    },
)
def tavily_hub_search(
    runtime: ToolRuntime[RuntimeContext], query: str, max_results: int = 5
):
    """TavilyHub网络搜索工具。

    当需要联网获取新闻、咨询是使用。

    Args:
        query: 查询文本
        max_results: 最大返回数量

    Returns:
        查询结果
    """
    api_key = runtime.context.tool_args.get("tavily_hub_search").get("api_key")
    if not api_key:
        raise ValueError("api key is required")

    logger.info("tavily search: {}", query)
    resp = httpx.post(
        "https://tavily.sharyuke.com/api/proxy/search",
        headers={"Authorization": api_key},
        json={"query": query, "max_results": max_results},
    )
    logger.debug("tavily search result: {}", resp.text)
    resp.raise_for_status()
    return resp.text
