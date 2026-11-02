# nap-client

NAP（next-agents-platform）Master 服务的命令行客户端。

## 安装

```bash
cd nap-client
uv sync
```

## 配置

在运行目录创建 `.env`：

```dotenv
NAP_BASE_URL = "http://localhost:18000"
NAP_AUTH__USERNAME = "your-username"
NAP_AUTH__PASSWORD = "your-password"
```

也可以使用环境变量覆盖，例如 `NAP_BASE_URL=http://host:18000`。

## 使用

```bash
nap-client --help
nap-client -v <command>          # -v / -vv / -vvv 提高日志级别
nap-client --json <command>      # 输出原始 JSON
```

### 资源命令

| 命令 | 说明 |
|------|------|
| `auth` | 获取 / 刷新 token |
| `user` | 注册、当前用户、更新、删除 |
| `agent` | 智能体 CRUD、详情、流式对话 |
| `session` | 会话列表、消息、删除 |
| `kb` | 知识库 CRUD、统计、文档列表、上传/URL/附件导入 |
| `knowledge` | 文档列表、详情、待办、内容下载、更新、删除 |
| `attachment` | 附件上传、列表、详情、下载、删除 |
| `llm` | LLM 提供商 CRUD |
| `mcp` | MCP 服务 CRUD |
| `toolkit` | 可用工具集 |
| `monitoring` | Token 用量、模型、延迟 |
| `dashboard` | 仪表盘概览 |

### 示例

```bash
# 当前用户
nap-client user me

# 智能体
nap-client agent list
nap-client agent detail <agent-uuid>
nap-client agent create --name demo --llm <llm-uuid> --instruction "You are helpful"
nap-client agent chat <agent-uuid> "hello"

# 知识库
nap-client kb list
nap-client kb create --name docs --description "documents"
nap-client kb add-file <kb-uuid> ./README.md
nap-client kb add-url <kb-uuid> https://example.com/doc.md
nap-client kb knowledges <kb-uuid>

# 文档 / 附件
nap-client knowledge list
nap-client knowledge content <knowledge-uuid> -o out.md
nap-client attachment upload ./file.pdf
nap-client attachment download <attachment-uuid> -o ./file.pdf

# 监控
nap-client monitoring token-usage --days 7
nap-client monitoring latency --days 7
```
