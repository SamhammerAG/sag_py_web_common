from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        max_body_size_mb: int,
        skip_if_content_length_header_missing: bool = False,
    ) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size_mb * 1024 * 1024  # Convert mb to bytes
        self.skip_if_content_length_header_missing = (
            skip_if_content_length_header_missing
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("content-length")

            if content_length is None:
                if self.skip_if_content_length_header_missing:
                    return await call_next(request)
                return JSONResponse(
                    status_code=411,
                    content={"detail": "Content-Length header is required"},
                )
            try:
                if int(content_length) > self.max_body_size:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large"},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )

        return await call_next(request)
