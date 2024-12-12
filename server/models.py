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
class ResetResponse(SuccResonse):
    key_map_cache_size: int
    secret_cache_size: int
