import logging
from unittest.mock import Mock

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sag_py_web_common import handle_unknown_exception, log_exception
from sag_py_web_common.json_exception_handler import handle_validation_exception


@pytest.mark.asyncio
async def test_handle_unknown_exception() -> None:
    # Act
    result: JSONResponse = await handle_unknown_exception("", Exception("error message"))

    # Assert
    assert result.status_code == 500
    assert result.body == b'{"detail":"error message"}'


@pytest.mark.asyncio
async def test_validation_exception_handler() -> None:
    # Arrange
    exc = RequestValidationError([{"loc": ("body", "title"), "msg": "field required", "type": "value_error.missing"}])
    request = Mock()

    # Act
    result: JSONResponse = await handle_validation_exception(request, exc)

    # Assert
    assert result.status_code == 422
    assert b'"msg":"field required"' in result.body
    assert b'"type":"value_error.missing"' in result.body
    assert b'"loc":["body","title"]' in result.body


@pytest.mark.asyncio
async def test_log_exception(caplog: LogCaptureFixture) -> None:
    # Arrange
    caplog.set_level(logging.ERROR)

    # Act
    await log_exception("", StarletteHTTPException(404, "Not found message."))

    # Assert
    assert "An HTTP Error! Not found message." in caplog.text
    assert len(caplog.records) == 1
    assert caplog.records[0].__getattribute__("response_status") == 404
