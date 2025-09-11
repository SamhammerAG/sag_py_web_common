import logging
from logging import Logger
from typing import Any

from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from sag_py_web_common.response_content import SimpleDetail, ValidationErrorDetail, ValidationErrorResponse

logger: Logger = logging.getLogger("http_error_logger")


async def handle_unknown_exception(_: Any, exception: Exception) -> JSONResponse:
    """Per default fastapi just returns the exception text. We want to return a json instead for rest apis.

    Returns:
        JSONResponse: A json response that contains the field 'detail' with the exception message.
    """
    logger.error("An unknown Error!", exc_info=True, extra={"response_status": 500})
    return JSONResponse(status_code=500, content=SimpleDetail(detail=str(exception)).model_dump())


async def log_exception(_, exception: StarletteHTTPException) -> Response:  # type: ignore
    logger.error("An HTTP Error! %s", exception.detail, extra={"response_status": exception.status_code})

    return await http_exception_handler(_, exception)


async def handle_validation_exception(_: Any, exception: RequestValidationError) -> JSONResponse:
    errors = [
        ValidationErrorDetail(**{
            "loc": [str(loc) for loc in err["loc"]],
            "msg": err["msg"],
            "type": err["type"]
        })
        for err in exception.errors()
    ]
    logger.error("Validation Error!", exc_info=True, extra={"response_status": 422})
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(detail=errors).model_dump()
    )
