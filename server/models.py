from pydantic import BaseModel
from typing import Literal


class SecretResponse(BaseModel):
    id: str
    key: str
    value: str


class SuccResonse(BaseModel):
    status: Literal["success"]


class CacheStats(BaseModel):
    keymap_cache_size: int
    secret_cache_size: int


class ResetResponse(SuccResonse):
    before: CacheStats
    after: CacheStats


class ErrorResponse(BaseModel):
    detail: str
