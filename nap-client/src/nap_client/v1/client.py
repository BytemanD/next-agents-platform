from collections.abc import Iterator

import httpx
from pystonic.utils import httpclient

from nap_client.common.conf import CONF
from nap_client.v1.auth_plugin import AuthPluginV1
from nap_client.v1.models import (
    LLM,
    MCP,
    AddedKnowledgesResponse,
    Agent,
    AgentDetail,
    AgentsResponse,
    AgentSuggestions,
    Attachment,
    AttachmentResponse,
    AttachmentsResponse,
    ChatEvent,
    Dashboard,
    KBStats,
    Knowledge,
    KnowledgeBase,
    KnowledgeBasesResponse,
    KnowledgesResponse,
    KnowledgeTodo,
    KnowledgeTodosResponse,
    Latency,
    LLMsResponse,
    MCPsResponse,
    Message,
    MessagesResponse,
    MonitoringModels,
    Session,
    SessionsResponse,
    TokenResp,
    TokenUsage,
    Toolkit,
    ToolkitsResponse,
    User,
)


class NapClientV1:
    """NAP Master 服务 HTTP 客户端（/api/v1）。"""

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.base_url = (base_url or CONF.base_url).rstrip("/")
        username = CONF.auth.username if username is None else username
        password = CONF.auth.password if password is None else password

        self._client = httpclient.default_client(
            base_url=self.base_url, raise_for_status=True
        )
        self._auth = AuthPluginV1(self.base_url, username, password)
        self._client.auth = self._auth

        # 注册接口无需登录，使用独立的无鉴权客户端
        self._anonymous = httpclient.default_client(
            base_url=self.base_url, raise_for_status=True
        )

    # ---------- internal helpers ----------

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        return self._client.get(path, params=params)

    def _post(self, path: str, **kwargs) -> httpx.Response:
        return self._client.post(path, **kwargs)

    def _put(self, path: str, **kwargs) -> httpx.Response:
        return self._client.put(path, **kwargs)

    def _delete(self, path: str) -> httpx.Response:
        return self._client.delete(path)

    @staticmethod
    def _payload(**fields) -> dict:
        return {k: v for k, v in fields.items() if v is not None}

    @staticmethod
    def _json(resp: httpx.Response):
        return resp.json()

    # ---------- auth / user ----------

    def login(self) -> str:
        """登录并返回 token（token 会被鉴权插件缓存）。"""
        return self._auth.get_token()

    def refresh_token(self) -> str:
        resp = self._post("/api/v1/auth/token")
        return TokenResp.model_validate(self._json(resp)).token

    def register(self, username: str, password: str, email: str | None = None) -> User:
        resp = self._anonymous.post(
            "/api/v1/users",
            json={"username": username, "password": password, "email": email},
        )
        return User.model_validate(self._json(resp))

    def me(self) -> User:
        return User.model_validate(self._json(self._get("/api/v1/users/me")))

    def update_user(
        self,
        uuid: str,
        account: str | None = None,
        email: str | None = None,
    ) -> User:
        resp = self._put(
            f"/api/v1/users/{uuid}",
            json=self._payload(account=account, email=email),
        )
        return User.model_validate(self._json(resp))

    def delete_user(self, uuid: str) -> None:
        self._delete(f"/api/v1/users/{uuid}")

    # ---------- llm ----------

    def list_llms(self) -> list[LLM]:
        return LLMsResponse.model_validate(self._json(self._get("/api/v1/llms"))).llms

    def get_llm(self, uuid: str) -> LLM:
        return LLM.model_validate(self._json(self._get(f"/api/v1/llms/{uuid}")))

    def create_llm(
        self,
        base_url: str,
        api_key: str,
        name: str = "",
        models: list[str] | None = None,
    ) -> LLM:
        resp = self._post(
            "/api/v1/llms",
            json={
                "name": name,
                "base_url": base_url,
                "api_key": api_key,
                "models": models or [],
            },
        )
        return LLM.model_validate(self._json(resp))

    def update_llm(
        self,
        uuid: str,
        name: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        models: list[str] | None = None,
    ) -> LLM:
        resp = self._put(
            f"/api/v1/llms/{uuid}",
            json=self._payload(
                name=name, base_url=base_url, api_key=api_key, models=models
            ),
        )
        return LLM.model_validate(self._json(resp))

    def delete_llm(self, uuid: str) -> None:
        self._delete(f"/api/v1/llms/{uuid}")

    # ---------- mcp ----------

    def list_mcps(self) -> list[MCP]:
        return MCPsResponse.model_validate(self._json(self._get("/api/v1/mcps"))).mcps

    def get_mcp(self, uuid: str) -> MCP:
        return MCP.model_validate(self._json(self._get(f"/api/v1/mcps/{uuid}")))

    def create_mcp(
        self,
        url: str,
        name: str | None = None,
        transport: str = "streamable_http",
        api_key: str | None = None,
    ) -> MCP:
        resp = self._post(
            "/api/v1/mcps",
            json=self._payload(
                url=url, name=name, transport=transport, api_key=api_key
            ),
        )
        return MCP.model_validate(self._json(resp))

    def update_mcp(
        self,
        uuid: str,
        name: str | None = None,
        url: str | None = None,
        transport: str | None = None,
        api_key: str | None = None,
    ) -> MCP:
        resp = self._put(
            f"/api/v1/mcps/{uuid}",
            json=self._payload(
                name=name, url=url, transport=transport, api_key=api_key
            ),
        )
        return MCP.model_validate(self._json(resp))

    def delete_mcp(self, uuid: str) -> None:
        self._delete(f"/api/v1/mcps/{uuid}")

    # ---------- agent ----------

    def list_agents(self) -> list[Agent]:
        return AgentsResponse.model_validate(
            self._json(self._get("/api/v1/agents"))
        ).agents

    def get_agent(self, uuid: str) -> Agent:
        return Agent.model_validate(self._json(self._get(f"/api/v1/agents/{uuid}")))

    def get_agent_detail(self, uuid: str) -> AgentDetail:
        return AgentDetail.model_validate(
            self._json(self._get(f"/api/v1/agents/{uuid}/detail"))
        )

    def create_agent(
        self,
        name: str,
        description: str = "",
        instruction: str = "",
        llm: str = "",
        status: str = "draft",
        config: dict | None = None,
        knowledge_bases: list[str] | None = None,
        tools: dict | None = None,
        mcp_uuids: list[str] | None = None,
    ) -> Agent:
        resp = self._post(
            "/api/v1/agents",
            json={
                "name": name,
                "description": description,
                "instruction": instruction,
                "llm": llm,
                "status": status,
                "config": config or {},
                "knowledge_bases": knowledge_bases or [],
                "tools": tools or {},
                "mcp_uuids": mcp_uuids or [],
            },
        )
        return Agent.model_validate(self._json(resp))

    def update_agent(
        self,
        uuid: str,
        name: str | None = None,
        description: str | None = None,
        instruction: str | None = None,
        llm: str | None = None,
        status: str | None = None,
        config: dict | None = None,
        knowledge_bases: list[str] | None = None,
        tools: dict | None = None,
        mcp_uuids: list[str] | None = None,
    ) -> Agent:
        resp = self._put(
            f"/api/v1/agents/{uuid}",
            json=self._payload(
                name=name,
                description=description,
                instruction=instruction,
                llm=llm,
                status=status,
                config=config,
                knowledge_bases=knowledge_bases,
                tools=tools,
                mcp_uuids=mcp_uuids,
            ),
        )
        return Agent.model_validate(self._json(resp))

    def delete_agent(self, uuid: str) -> None:
        self._delete(f"/api/v1/agents/{uuid}")

    def chat_agent(
        self,
        agent_uuid: str,
        query: str,
        session: str = "",
        model: str = "",
        tools: list[str] | None = None,
        knowledge_bases: list[str] | None = None,
        mcp_uuids: list[str] | None = None,
        attachments: list[str] | None = None,
    ) -> Iterator[ChatEvent]:
        payload = {
            "query": query,
            "model": model,
            "session": session,
            "tools": tools or [],
            "knowledge_bases": knowledge_bases or [],
            "mcp_uuids": mcp_uuids,
            "attachments": attachments or [],
        }
        with self._client.stream(
            "POST", f"/api/v1/agents/{agent_uuid}/chat", json=payload
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[len("data:") :].strip()
                if not data:
                    continue
                yield ChatEvent.model_validate_json(data)

    # ---------- session ----------

    def list_sessions(self, agent: str) -> list[Session]:
        resp = self._get("/api/v1/sessions", params={"agent": agent})
        return SessionsResponse.model_validate(self._json(resp)).sessions

    def list_messages(self, session_id: str) -> list[Message]:
        resp = self._get(f"/api/v1/sessions/{session_id}/messages")
        return MessagesResponse.model_validate(self._json(resp)).messages

    def delete_session(self, session_id: str) -> None:
        self._delete(f"/api/v1/sessions/{session_id}")

    # ---------- knowledge base ----------

    def list_knowledge_bases(self, shared: bool = False) -> list[KnowledgeBase]:
        resp = self._get("/api/v1/knowledge-bases", params={"shared": shared})
        return KnowledgeBasesResponse.model_validate(self._json(resp)).items

    def get_knowledge_base(self, uuid: str) -> KnowledgeBase:
        resp = self._get(f"/api/v1/knowledge-bases/{uuid}")
        return KnowledgeBase.model_validate(self._json(resp))

    def create_knowledge_base(self, name: str, description: str = "") -> KnowledgeBase:
        resp = self._post(
            "/api/v1/knowledge-bases",
            json={"name": name, "description": description},
        )
        return KnowledgeBase.model_validate(self._json(resp))

    def update_knowledge_base(
        self,
        uuid: str,
        name: str | None = None,
        description: str | None = None,
        active: bool | None = None,
    ) -> KnowledgeBase:
        resp = self._put(
            f"/api/v1/knowledge-bases/{uuid}",
            json=self._payload(name=name, description=description, active=active),
        )
        return KnowledgeBase.model_validate(self._json(resp))

    def delete_knowledge_base(self, uuid: str) -> None:
        self._delete(f"/api/v1/knowledge-bases/{uuid}")

    def knowledge_base_stats(self, uuid: str) -> KBStats:
        resp = self._get(f"/api/v1/knowledge-bases/{uuid}/stats")
        return KBStats.model_validate(self._json(resp))

    def list_knowledge_base_knowledges(self, uuid: str) -> list[Knowledge]:
        resp = self._get(f"/api/v1/knowledge-bases/{uuid}/knowledges")
        return KnowledgesResponse.model_validate(self._json(resp)).items

    def add_knowledge_file(
        self, kb_uuid: str, filename: str, content: bytes
    ) -> Knowledge:
        resp = self._post(
            f"/api/v1/knowledge-bases/{kb_uuid}/knowledges/file",
            files={"file": (filename, content)},
        )
        return Knowledge.model_validate(self._json(resp))

    def add_knowledge(
        self,
        kb_uuid: str,
        web_files: list[dict] | None = None,
        attachments: list[str] | None = None,
    ) -> list[Knowledge]:
        resp = self._post(
            f"/api/v1/knowledge-bases/{kb_uuid}/knowledges",
            json={
                "web_files": web_files or [],
                "attachments": attachments or [],
            },
        )
        return AddedKnowledgesResponse.model_validate(self._json(resp)).knowledges

    # ---------- knowledge ----------

    def list_knowledges(self) -> list[Knowledge]:
        return KnowledgesResponse.model_validate(
            self._json(self._get("/api/v1/knowledges"))
        ).items

    def get_knowledge(self, uuid: str) -> Knowledge:
        return Knowledge.model_validate(
            self._json(self._get(f"/api/v1/knowledges/{uuid}"))
        )

    def get_knowledge_todos(self, uuid: str) -> list[KnowledgeTodo]:
        resp = self._get(f"/api/v1/knowledges/{uuid}/todos")
        return KnowledgeTodosResponse.model_validate(self._json(resp)).items

    def get_knowledge_content(self, uuid: str) -> bytes:
        return self._get(f"/api/v1/knowledges/{uuid}/content").content

    def update_knowledge(
        self,
        uuid: str,
        name: str | None = None,
        size: int | None = None,
        path: str | None = None,
        status: int | None = None,
    ) -> Knowledge:
        resp = self._put(
            f"/api/v1/knowledges/{uuid}",
            json=self._payload(name=name, size=size, path=path, status=status),
        )
        return Knowledge.model_validate(self._json(resp))

    def delete_knowledge(self, uuid: str) -> None:
        self._delete(f"/api/v1/knowledges/{uuid}")

    # ---------- attachment ----------

    def upload_attachment(self, filename: str, content: bytes) -> Attachment:
        resp = self._post("/api/v1/attachments", files={"file": (filename, content)})
        return AttachmentResponse.model_validate(self._json(resp)).attachment

    def list_attachments(self) -> list[Attachment]:
        return AttachmentsResponse.model_validate(
            self._json(self._get("/api/v1/attachments"))
        ).attachments

    def get_attachment(self, uuid: str) -> Attachment:
        return Attachment.model_validate(
            self._json(self._get(f"/api/v1/attachments/{uuid}"))
        )

    def get_attachment_content(self, uuid: str) -> bytes:
        return self._get(f"/api/v1/attachments/{uuid}/content").content

    def delete_attachment(self, uuid: str) -> None:
        self._delete(f"/api/v1/attachments/{uuid}")

    # ---------- toolkit ----------

    def list_toolkits(self) -> list[Toolkit]:
        return ToolkitsResponse.model_validate(
            self._json(self._get("/api/v1/toolkits"))
        ).tools

    # ---------- monitoring ----------

    def token_usage(
        self, days: int = 7, agent_uuid: str | None = None, model: str | None = None
    ) -> TokenUsage:
        resp = self._get(
            "/api/v1/monitoring/token-usage",
            params=self._payload(days=days, agent_uuid=agent_uuid, model=model),
        )
        return TokenUsage.model_validate(self._json(resp))

    def monitoring_models(self) -> list[str]:
        resp = self._get("/api/v1/monitoring/models")
        return MonitoringModels.model_validate(self._json(resp)).models

    def latency(
        self, days: int = 7, agent_uuid: str | None = None, model: str | None = None
    ) -> Latency:
        resp = self._get(
            "/api/v1/monitoring/latency",
            params=self._payload(days=days, agent_uuid=agent_uuid, model=model),
        )
        return Latency.model_validate(self._json(resp))

    # ---------- dashboard ----------

    def dashboard(self) -> Dashboard:
        return Dashboard.model_validate(self._json(self._get("/api/v1/dashboard")))

    def get_agent_suggestions(self, agent_id: str):
        return AgentSuggestions.model_validate(
            self._get("/api/v1/agent-suggestions", params={"agent": agent_id}).json()
        ).suggestions


CLIENT = NapClientV1()
