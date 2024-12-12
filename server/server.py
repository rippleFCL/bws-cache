import functools
import logging
import os
import time
from typing import Annotated

from client import (
    BWSAPIRateLimitExceededException,
    BwsClientManager,
    InvalidTokenException,
    MissingSecretException,
    UnauthorizedTokenException,
    UnknownKeyException,
)
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse
from models import (
    ErrorResponse,
    ResetResponse,
    CacheStats,
    SecretResponse,
)
from prom_client import PromMetricsClient

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

root_logger = logging.getLogger()

logger = logging.getLogger("bwscache.server")

ORG_ID = os.environ.get("ORG_ID", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
REQUEST_RATE = int(os.environ.get("REQUEST_RATE", "1"))
REFRESH_RATE = int(os.environ.get("REFRESH_RATE", "10"))

mode_mapping = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

if not ORG_ID:
    raise ValueError("ORG_ID is required")

root_logger.setLevel(mode_mapping[LOG_LEVEL])

ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
root_logger.addHandler(ch)


api = FastAPI()


refresh_keymap_on_miss = os.environ.get("REFRESH_KEYMAP_ON_MISS", "").lower() == "true"


secret_ttl_environ = os.environ.get("SECRET_TTL")
if secret_ttl_environ:
    try:
        SECRET_INFO_TTL = int(secret_ttl_environ)
    except ValueError:
        raise ValueError("SECRET_TTL must be an integer")
else:
    SECRET_INFO_TTL = 600


prom_client = PromMetricsClient()
client_manager = BwsClientManager(prom_client, ORG_ID, REFRESH_RATE, REQUEST_RATE)


@api.middleware("http")
async def prom_middleware(request: Request, call_next):
    api_mapping = [
        "/reset",
        "/id",
        "/key",
    ]
    endpoint = None
    for api_endpoint in api_mapping:
        if request.url.path.startswith(api_endpoint):
            api_endpoint = api_endpoint
    st = time.time()
    return_data: Response = await call_next(request)
    if endpoint and isinstance(return_data, Response):
        prom_client.tick_http_request_total(endpoint, str(return_data.status_code))
        prom_client.tick_http_request_duration(endpoint, time.time() - st)
    return return_data


def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="bws-cache",
        version="1.0.0",
        summary="bws-cache OpenAPI Schema",
        description='<a href="https://github.com/rippleFCL/bws-cache">Github</a> | <a href="https://github.com/rippleFCL/bws-cache/issues">Issues</a>',
        routes=api.routes,
    )
    api.openapi_schema = openapi_schema
    return api.openapi_schema


api.openapi = custom_openapi


def handle_api_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidTokenException:
            return Response("Invalid token", status_code=401)
        except UnauthorizedTokenException:
            return Response("Unauthorized token", status_code=401)
        except BWSAPIRateLimitExceededException:
            return Response("Rate limited", status_code=429)
        except UnknownKeyException:
            return Response("Unknown key", status_code=404)
        except MissingSecretException:
            return Response("Secret not found", status_code=404)

    return wrapper


def handle_auth(authorization: Annotated[str, Header()]):
    if authorization.startswith("Bearer "):
        return authorization.split()[-1]
    raise HTTPException(status_code=401, detail="Invalid token")


@api.get(
    "/reset",
    response_model=ResetResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or unauthorised token"},
        429: {
            "model": ErrorResponse,
            "description": "BWS authentication endpoint rate limited",
        },
    },
)
@handle_api_errors
def reset_cache(authorization: Annotated[str, Depends(handle_auth)]):
    client = client_manager.get_client_by_token(authorization)
    stats = client.reset_cache()
    return ResetResponse(
        "success",
        before=stats,
        after=CacheStats(secret_cache_size=0, keymap_cache_size=0),
    )


@api.get(
    "/id/{secret_id}",
    response_model=SecretResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or unauthorised token"},
        404: {"model": ErrorResponse, "description": "Secret not found"},
        429: {
            "model": ErrorResponse,
            "description": "BWS authentication endpoint rate limited",
        },
    },
)
@handle_api_errors
def get_id(authorization: Annotated[str, Depends(handle_auth)], secret_id: str):
    client = client_manager.get_client_by_token(authorization)
    return client.get_secret_by_id(secret_id).to_json()


@api.get(
    "/key/{secret_key}",
    response_model=SecretResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or unauthorised token"},
        404: {"model": ErrorResponse, "description": "Key not found"},
        429: {
            "model": ErrorResponse,
            "description": "BWS authentication endpoint rate limited",
        },
    },
)
@handle_api_errors
def get_key(
    authorization: Annotated[str, Depends(handle_auth)],
    secret_key: str,
):
    print(authorization)
    client = client_manager.get_client_by_token(authorization)
    return client.get_secret_by_key(secret_key).to_json()


@api.get(
    "/metrics",
    response_class=PlainTextResponse,
    responses={
        200: {
            "description": "Successful response with metrics data",
        },
        500: {
            "model": ErrorResponse,
            "content": {
                "application/json": {"schema": ErrorResponse.model_json_schema()}
            },
            "description": "Internal server error",
        },
    },
)
def prometheus_metrics(accept: Annotated[str | str, Header()] = ""):
    generated_data, content_type = prom_client.generate_metrics(accept)
    headers = {"Content-Type": content_type}
    return PlainTextResponse(generated_data, headers=headers)
