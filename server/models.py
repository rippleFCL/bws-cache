from pydantic import BaseModel
from typing import Literal


class SecretResponse(BaseModel):
    id: str
    key: str
    value: str


class SuccResonse(BaseModel):
    status: Literal["success"]


class ResetStats(BaseModel):
    keymap_cache_size: int
    secret_cache_size: int


class ResetResponse(SuccResonse):
    before: ResetStats
    after: ResetStats


class ErrorResponse(BaseModel):
    detail: str
