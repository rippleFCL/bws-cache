import functools
import logging
import os
import time
from typing import Annotated

from bws_sdk import BWSSDKError
from client import (
    REGION_MAPPING,
    BwsClientManager,
    Region,
    RegionEnum,
)
from errors import (
    BWSAPIRateLimitExceededException,
    InvalidSecretIDException,
    InvalidTokenException,
    MissingSecretException,
    NoDefaultRegionException,
    SendRequestException,
    UnauthorizedTokenException,
    UnknownKeyException,
)
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse
from models import (
    CacheStats,
    ErrorResponse,
    HealthcheckResponse,
    ResetResponse,
    SecretResponse,
    StatsResponse,
)
from prom_client import PromMetricsClient

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
root_logger = logging.getLogger()
logger = logging.getLogger("bwscache.server")

mode_mapping = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

if root_logger.level == logging.DEBUG:
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(name)s:%(levelname)s - %(message)s",
        "%m-%d %H:%M:%S",
    )
else:
    formatter = logging.Formatter("%(asctime)s - %(name)s:%(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
root_logger.addHandler(ch)

root_logger.setLevel(mode_mapping[LOG_LEVEL])
logger.info("Logging level set to %s", LOG_LEVEL)

REFRESH_RATE = int(os.environ.get("REFRESH_RATE", "10"))
REGION_ENV = os.environ.get("BWS_REGION", "DEFAULT").upper()

if REGION_ENV not in RegionEnum:
    raise ValueError("BWS_REGION must be one of DEFAULT, EU, NONE or CUSTOM")

REGION = RegionEnum[REGION_ENV]

try:
    DEFAULT_REGION = REGION_MAPPING[REGION]
    logger.info("region set to %s", DEFAULT_REGION)
except KeyError:
    if REGION == RegionEnum.CUSTOM:
        raise ValueError(
            "BWS_REGION is CUSTOM but BWS_API_URL and BWS_IDENTITY_URL are not set"
        )
    elif REGION == RegionEnum.NONE:
        DEFAULT_REGION = None
        logger.warning("No default region set")
    else:
        raise ValueError("a Unknown region was provided")

if os.environ.get("ENABLE_TELEMETRY", "false").lower() == "true":
    import sentry_sdk

    sentry_sdk.init(
        dsn="https://dc49189fab59b5237fe2d73a6baba08d@sentry.beryju.io/7",
        # Don't add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=False,
    )


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
client_manager = BwsClientManager(prom_client, DEFAULT_REGION, REFRESH_RATE)


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
            endpoint = request.url.path
    st = time.time()
    return_data: Response = await call_next(request)
    if endpoint and isinstance(return_data, Response):
        prom_client.tick_http_request_total(endpoint, str(return_data.status_code))
        prom_client.tick_http_request_duration(endpoint, time.time() - st)
    prom_client.tick_stats(client_manager.stats())
    return return_data


def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="bws-cache",
        version="1.1.0",
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
        except SendRequestException:
            return Response("Can't connect to bitwarden.com")
        except MissingSecretException:
            return Response("Secret not found", status_code=404)
        except InvalidSecretIDException:
            return Response("Invalid secret ID", status_code=400)
        except NoDefaultRegionException:
            return Response(
                "No region set. Set BWS_DEFAULT_REGION environment variable for a default, provide one in the request via the X-BWS-REGION header or set X-BWS-API-URL and X-BWS-IDENTITY-URL HEADERS",
                status_code=400,
            )
        except BWSSDKError as e:
            logger.warning("BWS SDK error (This is a bug): %s", e)
            return Response(f"BWS SDK error: {e}", status_code=500)

    return wrapper


def handle_auth(authorization: Annotated[str, Header()]):
    if authorization.startswith("Bearer "):
        return authorization.split()[-1]
    raise HTTPException(status_code=401, detail="Invalid token")


def get_region(
    x_bws_region: Annotated[str | None, Header()] = None,
    x_bws_api_endpoint: Annotated[str | None, Header()] = None,
    x_bws_identity_endpoint: Annotated[str | None, Header()] = None,
):
    if x_bws_api_endpoint and x_bws_identity_endpoint:
        return Region(api_url=x_bws_api_endpoint, identity_url=x_bws_identity_endpoint)
    elif x_bws_api_endpoint or x_bws_identity_endpoint:
        raise HTTPException(
            status_code=400,
            detail="X-BWS-API-URL and X-BWS-IDENTITY-URL must be used together",
        )
    if x_bws_region:
        if x_bws_region in RegionEnum:
            return REGION_MAPPING[RegionEnum[x_bws_region]]
        raise HTTPException(
            status_code=400,
            detail="Invalid region, must be one of 'DEFAULT', 'EU', 'CUSTOM' or 'NONE'",
        )
    return None


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
def reset_cache(
    authorization: Annotated[str, Depends(handle_auth)],
    region: Annotated[Region | None, Depends(get_region)],
):
    client = client_manager.get_client(authorization, region)
    stats = client.reset_cache()
    return ResetResponse(
        status="success",
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
def get_id(
    authorization: Annotated[str, Depends(handle_auth)],
    region: Annotated[Region | None, Depends(get_region)],
    secret_id: str,
):
    client = client_manager.get_client(authorization, region)
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
    region: Annotated[Region | None, Depends(get_region)],
    secret_key: str,
):
    client = client_manager.get_client(authorization, region)
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


@api.get(
    "/stats",
    response_model=StatsResponse,
    responses={
        200: {
            "model": StatsResponse,
            "description": "Successful response with stats data",
        },
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
@handle_api_errors
def get_stats():
    return client_manager.stats()


@api.get("/healthcheck", response_model=HealthcheckResponse)
def healthcheck():
    return {"status": "I'm alive"}
