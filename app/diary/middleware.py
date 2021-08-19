from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequireJSON(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method in ('POST', 'PUT', 'PATCH'):
            if request.headers.get('content-type') != 'application/json':
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "status_code": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        "reason": f'application/json 형식의 content-type 을 사용하세요.'
                    }
                )
        return await call_next(request)
