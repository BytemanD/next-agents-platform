from langchain_openai import ChatOpenAI
from loguru import logger
from nap.knowledge.parse_drivers.markitdown import MarkitdownDriver
from langchain.agents import create_agent
from pydantic import SecretStr
from pystonic.utils import funcutil

from nap.llm.tools.internal import update_knowledge_enrichment
from nap.common.exceptions import EnrichFailed, EnrichmentAlreadyExists
from nap.db.models import Knowledge, KnowledgeStatus, LLMs

ENRICH_TEMPLATE = """
请阅读以下文档内容，完成三项任务：

## 任务一：提取关键词
提取 5-10 个最能代表文档核心内容的关键词或短语。要求：
- 优先选择文档中反复出现或处于核心位置的概念
- 每个关键词控制在 2-6 个字（中文）或 1-3 个词（英文）
- 按重要性从高到低排序

## 任务二：生成摘要
用 2-3 句话概括文档的核心内容。要求：
- 保留关键事实、结论和核心论点
- 不添加文档中没有的信息
- 语言简洁，避免套话

## 任务三：保存关键词和摘要
调用提供的工具将关键词和摘要先写入数据库

## 输出格式
严格按以下 JSON 格式输出，不要添加任何其他内容：
{{
  "keywords": ["关键词1", "关键词2", ...],
  "summary": "摘要内容"
}}

## 文档 UUID
{uuid}

## 文档内容
{content}

"""


class EnrichmentAgentDriver:
    @funcutil.timeit
    def enrich(
        self, knowledge: Knowledge, content: str, replace: bool = False
    ):
        # TODO: use config
        items = LLMs.query(LLMs.user == knowledge.creator)
        if not items:
            raise EnrichFailed("llm is empty")
        llm = items[0]
        if not llm.models:
            raise EnrichFailed("llm models is empty")

        agent = create_agent(
            model=ChatOpenAI(
                model=llm.models[0],
                api_key=SecretStr(llm.api_key),
                base_url=llm.base_url,
            ),
            system_prompt="你是一个专业的文档分析助手。",
            tools=[update_knowledge_enrichment],
        )

        if not replace:
            khm_enrichment = knowledge.get_enrichment()
            if khm_enrichment and khm_enrichment.keywords and khm_enrichment.summary:
                raise EnrichmentAlreadyExists(knowledge.uuid)

        logger.info("CALL agent to make knowledge entichment and save db ...")
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": ENRICH_TEMPLATE.format(
                            uuid=knowledge.uuid, content=content
                        ),
                    }
                ]
            },
        )
        logger.debug("Agent Return: {}", result["messages"][-1])
