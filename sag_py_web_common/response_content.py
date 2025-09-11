from pydantic import BaseModel
from typing import List


class SimpleDetail(BaseModel):
    detail: str


class ValidationErrorDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorDetail]
