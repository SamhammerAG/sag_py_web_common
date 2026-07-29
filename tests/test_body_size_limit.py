import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from sag_py_web_common.body_size_limit import BodySizeLimitMiddleware


def build_request_without_content_length(method: str = "POST") -> Request:
    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(
        {
            "type": "http",
            "method": method,
            "path": "/",
            "headers": [],
        },
        receive,
    )


def test_body_size_limit_returns_413_when_content_length_exceeds_limit() -> None:
    # Arrange
    app = FastAPI()
    app.add_middleware(BodySizeLimitMiddleware, max_body_size_mb=1)

    @app.post("/")
    async def post_body() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)

    # Act
    response = client.post("/", content=b"x" * (1024 * 1024 + 1))

    # Assert
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}


@pytest.mark.asyncio
async def test_body_size_limit_returns_411_when_content_length_is_missing() -> None:
    # Arrange
    app = FastAPI()
    middleware = BodySizeLimitMiddleware(app, max_body_size_mb=1)
    request = build_request_without_content_length()

    async def call_next(_: Request) -> JSONResponse:
        raise AssertionError("call_next should not be called")

    # Act
    response = await middleware.dispatch(request, call_next)

    # Assert
    assert response.status_code == 411
    assert response.body == b'{"detail":"Content-Length header is required"}'


@pytest.mark.asyncio
async def test_body_size_limit_skips_missing_content_length_when_configured() -> None:
    # Arrange
    app = FastAPI()
    middleware = BodySizeLimitMiddleware(
        app,
        max_body_size_mb=1,
        skip_if_content_length_header_missing=True,
    )
    request = build_request_without_content_length()

    async def call_next(_: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    # Act
    response = await middleware.dispatch(request, call_next)

    # Assert
    assert response.status_code == 200
    assert response.body == b'{"ok":true}'
