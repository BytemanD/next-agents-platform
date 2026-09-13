# NAP

Hand it over and take a nap.

## 开发

### 初始化项目

```shell
cd nap-backend
uv sync
```

### 后端

1. 启动API服务

```shell
uv run uvicorn nap.master.asgi:APP  --reload
```