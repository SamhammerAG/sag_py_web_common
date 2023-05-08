from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


async def handle_exception(_: Any, exception: Exception) -> JSONResponse:
    """Per default fastapi just returns the exception text. We want to return a json instead for rest apis.

    Returns:
        JSONResponse: A json response that contains the field 'detail' with the exception message.
    """
    return JSONResponse(status_code=500, content=jsonable_encoder({"detail": str(exception)}))
