from collections.abc import Awaitable
from typing import Callable

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.messages import AIMessageChunk
from langchain_openai import ChatOpenAI
from loguru import logger
from nap.master.agent.context import RuntimeContext
from pydantic import SecretStr


class ReasoningChatOpenAI(ChatOpenAI):
    """保留 reasoning_content 字段的 ChatOpenAI 包装器"""

    def _convert_chunk_to_generation_chunk(
        self, chunk, default_chunk_class, base_generation_info
    ):
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )
        if generation_chunk is None:
            return None

        # 从原始 delta 中提取 reasoning_content
        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {})
            reasoning = delta.get("reasoning_content") or delta.get("reasoning")
            if reasoning and isinstance(generation_chunk.message, AIMessageChunk):
                # breakpoint()
                prev = generation_chunk.message.additional_kwargs.get(
                    "reasoning_content", ""
                )
                generation_chunk.message.additional_kwargs["reasoning_content"] = (
                    prev + reasoning
                )
        return generation_chunk


class RuntimeAgentMiddleware(AgentMiddleware[AgentState, RuntimeContext]):
    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        ctx: RuntimeContext = request.runtime.context
        runtime_model = ReasoningChatOpenAI(
            model=ctx.model,
            api_key=SecretStr(ctx.model_api_key),
            base_url=ctx.model_base_url,
            temperature=ctx.agent_config.temperature,
            stream_usage=True,
            model_kwargs={"stream_options": {"include_usage": True}},
            # use_responses_api=True,
            # reasoning_effort="medium",
            # use_responses_api=False,
        )
        logger.info(
            "runtime tools: {}, knowledge bases: {}",
            [x.name for x in ctx.tools or []],
            [x.name for x in ctx.knowledge_bases],
        )
        return await handler(
            request.override(
                model=runtime_model,
                tools=ctx.tools,
                system_prompt=ctx.system_prompt,
            )
        )
