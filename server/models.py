from pydantic import BaseModel
from typing import Literal


class SecretResponse(BaseModel):
    id: str
    key: str
    value: str | dict | list


class SuccessResonse(BaseModel):
    status: Literal["success"]


class HealthcheckResponse(BaseModel):
    status: Literal["I'm alive"]


class CacheStats(BaseModel):
    keymap_cache_size: int
    secret_cache_size: int


class ResetResponse(SuccessResonse):
    before: CacheStats
    after: CacheStats


class ErrorResponse(BaseModel):
    detail: str


class StatsResponse(BaseModel):
    num_clients: int
    client_stats: dict[str, CacheStats]
    total_stats: CacheStats
