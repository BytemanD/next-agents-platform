"""用户使用的工具"""

from asyncio import to_thread

from langchain.tools import ToolRuntime
from langchain_core.tools import BaseToolkit, tool
from pystonic.common import context

from nap.common.knowledge_client import KnowledgeClient
from nap.db.models import Attachment
from nap.master.agent.context import NapRuntimeContext
from nap.services.storage import STORE_SERVICE

KNOWLEDGE_CLIENT = KnowledgeClient()


@tool
def get_username(runtime: ToolRuntime[NapRuntimeContext]):
    """获取当前用户名

    当需要获取当前用户名时使用。

    Returns:
        用户名
    """
    return runtime.context.username


@tool(parse_docstring=True)
async def save_text(
    filename: str, content: str, encoding: str = "utf-8-sig", overwrite: bool = False
):
    """保存文本到文件中

    当需要保存文本内容时使用。建议文件加上日期和时间，避免文件名冲突。

    Args:
        filename: 文件名
        content: 文本内容
        encoding: 文件编码
        overwrite: 如果文件已经存在是否覆盖

    Returns:
        文件UUID
    """
    attachment = Attachment(
        creator=context.getvar("account") or "guest",
        name=filename,
    )
    await to_thread(
        STORE_SERVICE.save_text,
        attachment,
        content,
        encoding=encoding,
        overwrite=overwrite,
    )
    attachment.create()
    return attachment.uuid


class Toolkit(BaseToolkit):
    """知识库工具集"""

    def get_tools(self) -> list:
        return [get_username, save_text]


TOOLKIT = Toolkit()
