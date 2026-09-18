from typing import Type

from pydantic import BaseModel, TypeAdapter
from sqlmodel import JSON, TypeDecorator


class AgentConfig(BaseModel):
    temperature: float = 1
    # max_tokens: int = 4096
    max_tokens: int | None = None


AgentConfig.model_validate_json


# ---------- 通用 TypeDecorator ----------
class PydanticType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_type: Type[BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pydantic_type = pydantic_type
        self._adapter = TypeAdapter(pydantic_type)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # 已经是模型实例就 dump，是 dict 就先 validate
        validated = self._adapter.validate_python(value)
        return self._adapter.dump_python(validated, mode="json")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # 自动补全缺失字段（Pydantic 默认值）
        return self._adapter.validate_python(value)


TYPE_AGENT_CONFIG = PydanticType(AgentConfig)
