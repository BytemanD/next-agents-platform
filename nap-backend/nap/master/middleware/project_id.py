from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pystonic.common.context import setvars


class ProjectContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        project_id = request.headers.get("x-project-id")
        setvars(project_id=project_id)
        return await call_next(request)
