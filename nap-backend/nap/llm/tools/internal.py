"""系统内部使用的工具"""

from loguru import logger
from nap.db.models import KnowledgeEnrichmen

from langchain_core.tools import tool


@tool
def update_knowledge_enrichment(doc_uuid: str, keywords: list[str], summary: str):
    """将文档的关键词和摘要写入知识库。每次完成关键词和摘要的提取后，必须调用此工具保存结果。

    当已经完成对某篇文档的关键词提取和摘要生成，需要把结果持久化保存时使用。
    如果该文档已有记录则覆盖更新，没有则新建。

    Args:
        knowledge_uuid: 文档在知识库中的唯一标识（UUID）
        keywords: 提取出的关键词列表，按重要性从高到低排序
        summary: 文档的摘要，2-3 句话概括核心内容

    Returns:
        保存结果，成功时返回确认信息
    """

    items = KnowledgeEnrichmen.query(KnowledgeEnrichmen.knowledge == doc_uuid)
    if not items:
        logger.info("create KnowledgeEnrichmen")
        item = KnowledgeEnrichmen(
            knowledge=doc_uuid,
            keywords=keywords,
            summary=summary,
        )
        item.create()
    else:
        logger.info("update KnowledgeEnrichmen")
        item = items[0]
        item.keywords = keywords
        item.summary = summary
        item.save()

    return f"已保存文档 {doc_uuid} 的富化信息"
