import logging

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi import FastAPI
from starlette.testclient import TestClient

from sag_py_web_common.filtered_access_logger import FilteredAccessLoggerMiddleware

app = FastAPI()
app.add_middleware(
    FilteredAccessLoggerMiddleware,
    format="%(client_addr)s - %(request_line)s %(status_code)s",
    logger=logging.getLogger("access"),
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the root URL"}


client = TestClient(app)


@pytest.mark.asyncio
async def test_filtered_access_logger(caplog: LogCaptureFixture) -> None:
    # Arrange
    caplog.set_level(logging.INFO)

    # Act
    client.get("/")

    # Assert
    assert len(caplog.records) == 3
    # log from the call method
    assert caplog.records[0].getMessage() == "Received: GET /"
    # log from the log method
    assert caplog.records[1].getMessage().startswith("testclient:50000 - GET / HTTP/1.1 200")
    # coming from the httpx library. This log is not related to the FilteredAccessLoggerMiddleware class
    assert caplog.records[2].getMessage().startswith("HTTP Request: GET http://testserver/ ")


@pytest.mark.asyncio
async def test_filtered_access_logger_health_check(caplog: LogCaptureFixture) -> None:
    # Arrange
    caplog.set_level(logging.INFO)

    # Act
    client.get("/", headers={"healthcheck": "livenessprobe"})

    # Assert
    # Log is coming from the httpx library. This log is not related to the FilteredAccessLoggerMiddleware class.
    # No other logs appear
    assert len(caplog.records) == 1


@pytest.mark.asyncio
async def test_filtered_access_logger_not_found(caplog: LogCaptureFixture) -> None:
    # Arrange
    caplog.set_level(logging.INFO)

    # Act
    client.get("/test", headers={"healthcheck": "invalid"})

    # Assert
    assert len(caplog.records) == 3
    assert caplog.records[0].getMessage() == "Received: GET /test"
    # log from the log method (404) is logged with warning
    assert caplog.records[1].levelname == "WARNING"
    assert caplog.records[1].getMessage().startswith("testclient:50000 - GET /test HTTP/1.1 404")
    # coming from the httpx library. This log is not related to the FilteredAccessLoggerMiddleware class
    assert caplog.records[2].getMessage().startswith("HTTP Request: GET http://testserver/test ")


def test_filtered_access_logger_init() -> None:
    # Act
    middleware = FilteredAccessLoggerMiddleware(app,  # type: ignore
                                                format="%(client_addr)s - %(request_line)s %(status_code)s")

    # Assert
    assert middleware.format == "%(client_addr)s - %(request_line)s %(status_code)s"
    assert middleware.logger.name == "access"
