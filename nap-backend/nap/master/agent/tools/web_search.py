"""用户使用的工具"""

import httpx
from langchain_core.tools import tool
from loguru import logger
from nap.common.objects import Toolkit, ToolkitMetadata


class WebSearchToolkit(Toolkit):
    # title: str = "联网搜索"
    # type: str = "web_search"
    # help: str = (
    #     "该工具需要需要在 TavilyHub 注册账号并创建API_KEY。"
    #     "官网: https://tavily.sharyuke.com/dashboard"
    # )
    # args_schema: dict = {"api_key": {"type": "string"}}
    # config: dict = {}
    api_key: str

    @classmethod
    def metadata(cls):
        return ToolkitMetadata(
            name="web_search",
            title="联网搜索",
            type="web_search",
            help=(
                "该工具需要需要在 TavilyHub 注册账号并创建API_KEY。"
                "官网: https://tavily.sharyuke.com/dashboard"
            ),
        )

    def _tavily_hub_search(self, query: str, max_results: int = 5):
        # api_key = runtime.context.tool_args.get("tavily_hub_search").get("api_key")
        logger.info("tavily search: {}", query)
        resp = httpx.post(
            "https://tavily.sharyuke.com/api/proxy/search",
            headers={"Authorization": self.api_key},
            json={"query": query, "max_results": max_results},
        )
        logger.debug("tavily search result: {}", resp.text)
        resp.raise_for_status()
        return resp.text

    def get_tools(self):

        @tool(
            parse_docstring=True,
            extras={
                "title": "联网搜索(TavilyHub)",
                "type": "web_search",
                "requires": {"api_key": {"type": "string"}},
                "help": (
                    "该工具需要需要在 TavilyHub 注册账号并创建API_KEY。"
                    "官网: https://tavily.sharyuke.com/dashboard"
                ),
            },
        )
        def web_search(query: str, max_results: int = 5):
            """联网搜索工具

            当需要联网获取新闻、咨询是使用。

            Args:
                query: 查询文本
                max_results: 最大返回数量

            Returns:
                查询结果
            """
            return self._tavily_hub_search(query, max_results)

        return [web_search]
