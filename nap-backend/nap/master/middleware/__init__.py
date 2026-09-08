from nap.common.context import project_id
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class ProjectContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pid = request.headers.get("x-project-id")
        token = project_id.set(pid)
        try:
            response = await call_next(request)
            return response
        finally:
            project_id.reset(token)
