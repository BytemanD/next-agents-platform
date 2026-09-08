from typing import List

from agents import function_tool
from nap.vector.manager import get_vector_driver
from nap.vector.models import Doc, RetrivalDoc

vector_driver = get_vector_driver()


@function_tool(timeout=300)
async def list_docs() -> List[Doc]:
    """列出ChromaDB中的文档

    Returns:
        List[Doc]: 文档列表
    """
    return [x.model_dump(mode="json") for x in vector_driver.list_docs()]


@function_tool(timeout=300)
async def query(text: str, n_results: int = 1) -> List[RetrivalDoc]:
    """根据文本召回匹配的文档内容

    Args:
        text (str): 查询文本
        n_results (int, optional): 需要召回的文档数量. Defaults to 1.
    Returns:
        List[dict]: 所有匹配的文档内容列表
    """
    return [
        x.model_dump(mode="json")
        for x in vector_driver.query(text, n_results=n_results)
    ]
