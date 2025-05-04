import datetime
import enum
import functools
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from queue import Queue
from threading import Lock, Thread
import requests

import yaml
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from models import CacheStats, StatsResponse
from prom_client import PromMetricsClient
from errors import (
    BWSAPIRateLimitExceededException,
    InvalidSecretIDException,
    InvalidTokenException,
    MissingSecretException,
    NoDefaultOrgIdException,
    NoDefaultRegionException,
    SendRequestException,
    UnauthorizedTokenException,
    UnknownKeyException,
    UnknownOrgIdException,
)

logger = logging.getLogger("bwscache.client")


class RegionEnum(enum.Enum):
    DEFAULT = "DEFAULT"
    EU = "EU"
    CUSTOM = "CUSTOM"
    NONE = "NONE"


@dataclass
class Region:
    api_url: str
    identity_url: str


REGION_MAPPING = {
    RegionEnum.DEFAULT: Region(
        api_url="https://api.bitwarden.com",
        identity_url="https://identity.bitwarden.com",
    ),
    RegionEnum.EU: Region(
        api_url="https://api.bitwarden.eu", identity_url="https://identity.bitwarden.eu"
    ),
}


PARSE_SECRET_VALUES = os.environ.get("PARSE_SECRET_VALUES", "false").lower() == "true"

API_URL = os.environ.get("BWS_API_URL", "")
IDENTITY_URL = os.environ.get("BWS_IDENTITY_URL", "")

if not (not API_URL and not IDENTITY_URL) and not (API_URL and IDENTITY_URL):
    raise ValueError("BWS_API_URL and BWS_IDENTITY_URL must be set")
elif API_URL and IDENTITY_URL:
    logger.info("custom region set using BWS_API_URL and BWS_IDENTITY_URL")
    REGION_MAPPING[RegionEnum.CUSTOM] = Region(
        api_url=API_URL, identity_url=IDENTITY_URL
    )


def generate_hash(value: str, org_id: str, region: Region) -> str:
    value = f"{value}{org_id}{region.api_url}{region.identity_url}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass
class SecretMetaData:
    key: str
    id: str


class SecretResponse:
    def __init__(self, metadata: SecretMetaData, value: str | None):
        self._metadata = metadata
        self._id = id
        self._value = value

    @property
    def metadata(self):
        return self._metadata

    @property
    def key(self):
        return self._metadata.key

    @property
    def id(self):
        return self._metadata.id

    @property
    def value(self):
        data = self._value
        if data is not None:
            if not PARSE_SECRET_VALUES:
                return data
            else:
                try:
                    data = json.loads(data)
                    logger.debug("JSON parse succeeded")
                    return data
                except json.JSONDecodeError:
                    logger.debug("JSON parse failed... trying yaml")
                try:
                    data = yaml.safe_load(data)
                    logger.debug("YAML parse succeeded")
                    return data
                except yaml.YAMLError:
                    logger.debug("YAML parse failed... return raw secret")
        else:
            logger.info("Secret not found")
        return None

    def to_json(self):
        return {"key": self.key, "id": self.id, "value": self.value}


class BWSClient:
    def __init__(self, bws_token: str, org_id: str, region: Region):
        self.region = region
        self.org_id = org_id
        self.bws_token = bws_token
        self.bws_client = self._make_client()
        self.client_lock = Lock()
        self.last_sync = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(seconds=60)

    def _make_client(self):
        return BitwardenClient(
            client_settings_from_dict(
                {
                    "apiUrl": self.region.api_url,
                    "deviceType": DeviceType.SDK,
                    "identityUrl": self.region.identity_url,
                    "userAgent": "Python",
                }
            )
        )

    @staticmethod
    def _handle_api_errors(func):
        @functools.wraps(func)
        def wrapper(self: "BWSClient", *args, **kwargs):
            try:
                requests.head("https://bitwarden.com", timeout=5)
                return func(self, *args, **kwargs)
            except requests.exceptions.RequestException as e:
                logger.debug("Cannot connect to bitwarden.com")
                raise SendRequestException() from e
            except Exception as e:
                logger.error("Request failed with %s", e.args[0])
                if "401 Unauthorized" in e.args[0]:
                    raise UnauthorizedTokenException("Unauthorized token") from e
                elif "429 Too Many Requests" in e.args[0]:
                    raise BWSAPIRateLimitExceededException("Too many requests") from e
                elif "404 Not Found" in e.args[0] and "Secret not found" in e.args[0]:
                    raise MissingSecretException() from e
                elif "404 Not Found" in e.args[0] and "Resource not found" in e.args[0]:
                    raise UnknownOrgIdException() from e
                elif (
                    "400 Bad Request" in e.args[0]
                    or "Access token is not in a valid format" in e.args[0]
                ):
                    raise InvalidTokenException("Invalid token") from e
                elif "error sending request for url" in e.args[0]:
                    raise SendRequestException() from e
                elif "Invalid command value: UUID parsing failed" in e.args[0]:
                    raise InvalidSecretIDException()
                raise e

        return wrapper

    @_handle_api_errors
    def auth(self, cache: bool = True):
        try:
            logger.debug("Authenticating client")
            auth_cache_file = f"/dev/shm/token_{self.client_hash}" if cache else ""
            # fixme: when rapid requests made with valid but expired token, the following line hangs indefinitely
            # not fixed but restructured to call this less
            with self.client_lock:
                self.bws_client.auth().login_access_token(
                    self.bws_token, auth_cache_file
                )
        except Exception as e:
            logger.error("Request failed with %s", e.args[0])

            raise e

    @_handle_api_errors
    def list_secrets(self):
        secrets: list[SecretMetaData] = []
        with self.client_lock:
            logger.debug("Getting secret list")
            secrets_metadata = self.bws_client.secrets().list(self.org_id).data
        if secrets_metadata:
            for secret in secrets_metadata.data:
                secrets.append(SecretMetaData(secret.key, str(secret.id)))
        return secrets

    @_handle_api_errors
    def get_updated_secrets(self):
        secrets: list[SecretResponse] = []
        latest_sync = datetime.datetime.now(tz=datetime.timezone.utc)
        with self.client_lock:
            logger.debug("Getting updated secrets")
            secret_response = (
                self.bws_client.secrets().sync(self.org_id, self.last_sync).data  # type: ignore
            )  # type: ignore
        logger.debug("Got updated secrets")
        self.last_sync = latest_sync
        if secret_response and secret_response.has_changes and secret_response.secrets:
            for secret in secret_response.secrets:
                logger.debug("Got updated secret %s", secret.id)
                secrets.append(
                    SecretResponse(
                        SecretMetaData(secret.key, str(secret.id)), secret.value
                    )
                )
        else:
            logger.debug("No secrets updated")
        return secrets

    @_handle_api_errors
    def get_secret_by_id(self, secret_uuid: str):
        with self.client_lock:
            logger.debug("Getting secret %s", secret_uuid)
            data = self.bws_client.secrets().get(secret_uuid).data
        if data:
            logger.debug("Upstream has secret %s", secret_uuid)
            return SecretResponse(SecretMetaData(data.key, str(data.id)), data.value)
        logger.debug("Upstream secret %s not found", secret_uuid)
        return None

    @property
    def client_hash(self):
        return generate_hash(self.bws_token, self.org_id, self.region)


class RequesterCrash(Exception):
    pass


@dataclass
class RequestContext:
    client: BWSClient
    id: str


class ClientRequester:
    def __init__(self, request_interval: int):
        self.request_interval = request_interval
        self.request_lock = Lock()
        self.request_queue: Queue[RequestContext] = Queue(1)
        self.response_queue: Queue[SecretResponse | None | Exception] = Queue(1)
        self.request_thread = Thread(target=self._request_loop, daemon=True)
        self.crashed = False

    def start(self):
        self.request_thread.start()

    def _request_loop(self):
        while True:
            try:
                request_context = self.request_queue.get()
                logger.debug("Requesting secret %s", request_context.id)

                response = request_context.client.get_secret_by_id(request_context.id)
            except Exception as e:
                logger.error("Request failed")
                response = e

            try:
                self.response_queue.put(response, timeout=self.request_interval)
            except TimeoutError:
                logger.critical(
                    "Client did not consume the response, request thread unrecoverable"
                )
                self.crashed = True
                return
            time.sleep(self.request_interval)

    def get_secret_by_id(self, client: BWSClient, secret_id: str):
        if self.crashed:
            sys.exit(1)

        with self.request_lock:
            logger.debug("Submitting secret to be requested %s", secret_id)
            self.request_queue.put(RequestContext(client, secret_id))
            logger.debug("Waiting for secret %s", secret_id)
            response = self.response_queue.get()
            if isinstance(response, Exception):
                raise response
            return response


class CachedBWSClient:
    def __init__(
        self,
        bws_secret_token: str,
        org_id: str,
        region: Region,
        requester: ClientRequester,
        prom_client: PromMetricsClient,
    ):
        self.prom_client = prom_client
        self.client = self._make_client(bws_secret_token, org_id, region)
        self.requester = requester
        self.secret_cache: dict[str, SecretResponse] = {}
        self.key_map: dict[str, str] = {}
        self.cache_lock = Lock()

    @staticmethod
    def _make_client(bws_secret_token: str, org_id: str, region: Region):
        return BWSClient(bws_secret_token, org_id, region)

    def auth(self):
        self.client.auth()

    def get_secret_by_id(self, secret_id: str):
        with self.cache_lock:
            cached_secret = self.secret_cache.get(secret_id, None)
        if cached_secret is None:
            logger.debug("Cache miss for secret %s", secret_id)
            self.prom_client.tick_cache_miss("secret")
            secret = self.requester.get_secret_by_id(self.client, secret_id)
            if secret is None:
                raise MissingSecretException("Secret not found")
            logger.debug("Requester returned secret %s", secret_id)
            with self.cache_lock:
                self.secret_cache[secret_id] = secret
            self.prom_client.tick_cache_hits("secret")
            return secret
        else:
            logger.debug("Cache hit for secret %s", secret_id)
            self.prom_client.tick_cache_hits("secret")
        return cached_secret

    def _load_secret_keys(self):
        logger.debug("Generating secret key map")
        secrets = self.client.list_secrets()
        with self.cache_lock:
            for secret in secrets:
                self.key_map[secret.key] = secret.id
            logger.debug(f"generated secret key map with {len(self.key_map)} keys")

    def get_secret_by_key(self, secret_key: str):
        if not self.key_map:
            self._load_secret_keys()

        with self.cache_lock:
            key = self.key_map.get(secret_key, None)

        if key is None:
            logger.debug("No key mapping found %s", secret_key)
            self.prom_client.tick_cache_miss("key")
            raise UnknownKeyException("Key not found")
        logger.debug("Key mapping found %s", secret_key)
        return self.get_secret_by_id(key)

    def refresh_cache(self):
        secrets = self.client.get_updated_secrets()
        if secrets:
            self.reset_cache()
        with self.cache_lock:
            for secret in secrets:
                logger.debug(
                    "Adding cache for secret %s, key %s", secret.id, secret.key
                )
                self.secret_cache[secret.id] = secret
                self.key_map[secret.key] = secret.id

    def reset_cache(self) -> CacheStats:
        logger.debug("Resetting cache")
        stats = self.stats()
        with self.cache_lock:
            self.secret_cache = {}
            self.key_map = {}
        return stats

    def stats(self) -> CacheStats:
        with self.cache_lock:
            return CacheStats(
                secret_cache_size=len(self.secret_cache),
                keymap_cache_size=len(self.key_map),
            )

    @property
    def client_hash(self):
        return self.client.client_hash


class ClientList:
    def __init__(self):
        self._clients: dict[str, CachedBWSClient] = {}
        self._clients_lock = Lock()

    def add_client(self, client: CachedBWSClient):
        with self._clients_lock:
            self._clients[client.client_hash] = client
        logger.debug(
            "Adding client %s. total clients: %s",
            client.client_hash,
            len(self._clients),
        )

    def remove_client(self, client: CachedBWSClient):
        with self._clients_lock:
            self._clients.pop(client.client_hash, None)
        logger.debug(
            "Removed client %s. total clients: %s",
            client.client_hash,
            len(self._clients),
        )

    def get(self, token: str, org_id: str, region: Region):
        hashed_token = generate_hash(token, org_id, region)
        with self._clients_lock:
            return self._clients.get(hashed_token, None)

    def list_clients(self):
        with self._clients_lock:
            return list(self._clients.copy().values())


class CachedClientRefresher:
    def __init__(self, refresh_interval: int, client_list: ClientList):
        self.clients = client_list
        self.refresh_interval = refresh_interval
        self.refresh_loop = Thread(target=self._refresh_loop, daemon=True)

    def start(self):
        self.refresh_loop.start()

    def _refresh_loop(self):
        while True:
            clients = self.clients.list_clients()
            if clients:
                logger.debug("Refreshing %s clients.", len(clients))
                for client in clients:
                    logger.debug("Refreshing client id: %s", client.client_hash)
                    try:
                        client.refresh_cache()
                    except BWSAPIRateLimitExceededException:
                        logger.info(
                            "Rate limit exceeded for client %s", client.client_hash
                        )
                        time.sleep(30)
                    except InvalidTokenException:
                        logger.error("Invalid token for client %s", client.client_hash)
                        self.clients.remove_client(client)
                    except UnknownOrgIdException:
                        logger.error("Unknown org ID for client %s", client.client_hash)
                        self.clients.remove_client(client)
                    except SendRequestException:
                        logger.info(
                            "Can't sent request to upstream for client for client %s skipping...",
                            client.client_hash,
                        )
                    except Exception as e:
                        logger.error("Error occurred while refreshing client.")
                        logger.debug(e, exc_info=True)
                        self.clients.remove_client(client)
                    time.sleep(self.refresh_interval)
            else:
                time.sleep(1)


class BwsClientManager:
    def __init__(
        self,
        prom_client: PromMetricsClient,
        default_org_id: str | None,
        default_region: Region | None,
        secret_refresh_interval: int,
        secret_request_interval: int,
    ):
        self.org_id = default_org_id
        self.region = default_region
        self.prom_client = prom_client
        self.client_list = self._make_client_list()
        self.refresher = self._make_refresher(secret_refresh_interval, self.client_list)
        self.requester = self._make_requester(secret_request_interval)

    @staticmethod
    def _make_requester(request_interval: int):
        requester = ClientRequester(request_interval)
        requester.start()
        return requester

    @staticmethod
    def _make_refresher(refresh_interval: int, client_list: ClientList):
        refresher = CachedClientRefresher(refresh_interval, client_list)
        refresher.start()
        return refresher

    @staticmethod
    def _make_client_list():
        return ClientList()

    def _make_client(self, bws_secret_token: str, org_id: str, region: Region):
        client = CachedBWSClient(
            bws_secret_token, org_id, region, self.requester, self.prom_client
        )
        client.auth()
        return client

    def get_client(
        self, bws_secret_token, org_id: str | None, region: Region | None
    ) -> CachedBWSClient:
        if org_id is None:
            if self.org_id is None:
                raise NoDefaultOrgIdException("Default org id is not set")
            org_id = self.org_id

        if region is None:
            if self.region is None:
                raise NoDefaultRegionException("Default region is not set")
            region = self.region

        client = self.client_list.get(bws_secret_token, org_id, region)
        if client is None:
            logger.debug("Creating new client")
            client = self._make_client(bws_secret_token, org_id, region)

            self.client_list.add_client(client)
        return client

    def stats(self) -> StatsResponse:
        clients_stats: dict[str, CacheStats] = {}
        for client in self.client_list.list_clients():
            clients_stats[client.client_hash] = client.stats()

        secret_cache_size_sum = 0
        keymap_cache_size_sum = 0
        for client_stats in clients_stats.values():
            secret_cache_size_sum += client_stats.secret_cache_size
            keymap_cache_size_sum += client_stats.keymap_cache_size

        total_stats = CacheStats(
            secret_cache_size=secret_cache_size_sum,
            keymap_cache_size=keymap_cache_size_sum,
        )

        return StatsResponse(
            num_clients=len(clients_stats),
            client_stats=clients_stats,
            total_stats=total_stats,
        )
