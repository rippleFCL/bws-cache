from pydantic import BaseModel
from typing import Any, Literal


class SecretResponse(BaseModel):
    id: str
    key: str
    value: str | dict | list


class SuccResonse(BaseModel):
    status: Literal["success"]

class HealthcheckResponse(BaseModel):
    status: Literal["I'm alive"]

class CacheStats(BaseModel):
    keymap_cache_size: int
    secret_cache_size: int


class ResetResponse(SuccResonse):
    before: CacheStats
    after: CacheStats


class ErrorResponse(BaseModel):
    detail: str


class StatsResponse(BaseModel):
    num_clients: int
    client_stats: dict[str, CacheStats]
    total_stats: CacheStats
