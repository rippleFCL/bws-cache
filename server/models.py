from dataclasses import dataclass
from typing import Literal

@dataclass
class SecretResponse:
    id: str
    key: str
    value: str

@dataclass
class SuccResonse:
    status: Literal["success"]

@dataclass
class ResetStats():
    keymap_cache_size: int
    secret_cache_size: int

@dataclass
class ResetResponse(SuccResonse):
    before: ResetStats
    after: ResetStats

@dataclass
class ErrorResponse:
    detail: str

@dataclass
class MetricsResponse:
    content: str
