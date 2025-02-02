import datetime
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

import yaml
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from models import CacheStats, StatsResponse
from prom_client import PromMetricsClient

PARSE_SECRET_VALUES = os.environ.get("PARSE_SECRET_VALUES", "false").lower() == "true"


logger = logging.getLogger("bwscache.client")


def generate_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class InvalidTokenException(Exception):
    pass


class UnauthorizedTokenException(Exception):
    pass


class BWSAPIRateLimitExceededException(Exception):
    pass


class MissingSecretException(Exception):
    pass


class UnknownKeyException(Exception):
    pass

class CantSendRequestException(Exception):
    pass

class InvalidSecretIDException(Exception):
    pass

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
                    logger.debug("json parse succeeded")
                    return data
                except json.JSONDecodeError:
                    logger.debug("json parse failed... trying yaml")
                try:
                    data = yaml.safe_load(data)
                    logger.debug("yaml parse succeeded")
                    return data
                except yaml.YAMLError:
                    logger.debug("yaml parse failed... return raw secret")
        else:
            logger.info("secret not found")
        return None

    def to_json(self):
        return {"key": self.key, "id": self.id, "value": self.value}


class BWSClient:
    def __init__(self, bws_token: str, org_id: str):
        self.org_id = org_id
        self.bws_token = bws_token
        self.bws_client = self._make_client()
        self.client_lock = Lock()
        self.last_sync = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=60)

    def _make_client(self):
        return BitwardenClient(
            client_settings_from_dict(
                {
                    "apiUrl": "https://api.bitwarden.com",
                    "deviceType": DeviceType.SDK,
                    "identityUrl": "https://identity.bitwarden.com",
                    "userAgent": "Python",
                }
            )
        )


    @staticmethod
    def _handle_api_errors(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error("request failed with %s", e.args[0])

                if "401 Unauthorized" in e.args[0]:
                    raise UnauthorizedTokenException("Unauthorized token") from e
                elif "429 Too Many Requests" in e.args[0]:
                    raise BWSAPIRateLimitExceededException("too many requests") from e
                elif "404 Not Found" in e.args[0]:
                    raise MissingSecretException() from e
                elif "400 Bad Request" in e.args[0] or "Access token is not in a valid format" in e.args[0]:
                    raise InvalidTokenException("Invalid token") from e
                elif "error sending request for url" in e.args[0]:
                    raise CantSendRequestException() from e
                elif "Invalid command value: UUID parsing failed" in e.args[0]:
                    raise InvalidSecretIDException()
                raise e

        return wrapper

    @_handle_api_errors
    def auth(self, cache: bool = True):
        try:
            logger.debug("authenticating client")
            auth_cache_file = f"/dev/shm/token_{generate_hash(self.bws_token)}" if cache else ""
            # fixme: when rapid requests made with valid but expired token, the folllwing line hangs indefinitely
            # not fixed but restructured to call this less
            with self.client_lock:
                self.bws_client.auth().login_access_token(self.bws_token, auth_cache_file)
        except Exception as e:
            logger.error("request failed with %s", e.args[0])

            raise e


    @_handle_api_errors
    def list_secrets(self):
        secrets: list[SecretMetaData] = []
        with self.client_lock:
            logger.debug("getting secret list")
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
            logger.debug("getting updated secrets")
            secret_response = self.bws_client.secrets().sync(self.org_id, self.last_sync).data
        logger.debug("got updated secrets")
        self.last_sync = latest_sync
        if secret_response and secret_response.has_changes and secret_response.secrets:
            for secret in secret_response.secrets:
                logger.debug("got updated secret %s", secret.id)
                secrets.append(SecretResponse(SecretMetaData(secret.key, str(secret.id)), secret.value))
        else:
            logger.debug("no secrets updated")
        return secrets

    @_handle_api_errors
    def get_secret_by_id(self, secret_uuid: str):
        with self.client_lock:
            logger.debug("getting secret %s", secret_uuid)
            data = self.bws_client.secrets().get(secret_uuid).data
        if data:
            logger.debug("upstream has secret %s", secret_uuid)
            return SecretResponse(SecretMetaData(data.key, str(data.id)), data.value)
        logger.debug("upstream secret %s not found", secret_uuid)
        return None


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
                logger.debug("requesting secret %s", request_context.id)

                response = request_context.client.get_secret_by_id(request_context.id)
            except Exception as e:
                logger.error("request failed")
                response = e

            try:
                self.response_queue.put(response, timeout=self.request_interval)
            except TimeoutError:
                logger.critical("client did not consume the response, request thread unrecoverable")
                self.crashed = True
                return
            time.sleep(self.request_interval)

    def get_secret_by_id(self, client: BWSClient, secret_id: str):
        if self.crashed:
            sys.exit(1)

        with self.request_lock:
            logger.debug("submiting secret to be requested %s", secret_id)
            self.request_queue.put(RequestContext(client, secret_id))
            logger.debug("waiting for secret %s", secret_id)
            response = self.response_queue.get()
            if isinstance(response, Exception):
                raise response
            return response


class CachedBWSClient:
    def __init__(
        self,
        bws_secret_token: str,
        org_id: str,
        requester: ClientRequester,
        prom_client: PromMetricsClient,
    ):
        self.prom_client = prom_client
        self.client = self._make_client(bws_secret_token, org_id)
        self.requester = requester
        self.secret_cache: dict[str, SecretResponse] = {}
        self.key_map: dict[str, str] = {}
        self.cache_lock = Lock()

    @staticmethod
    def _make_client(bws_secret_token: str, org_id: str):
        return BWSClient(bws_secret_token, org_id)

    def auth(self):
        self.client.auth()

    def get_secret_by_id(self, secret_id: str):
        with self.cache_lock:
            cached_secret = self.secret_cache.get(secret_id, None)
        if cached_secret is None:
            logger.debug("cache miss for secret %s", secret_id)
            self.prom_client.tick_cache_miss("secret")
            secret = self.requester.get_secret_by_id(self.client, secret_id)
            if secret is None:
                raise MissingSecretException("Secret not found")
            logger.debug("requester returned secret %s", secret_id)
            with self.cache_lock:
                self.secret_cache[secret_id] = secret
            self.prom_client.tick_cache_hits("secret")
            return secret
        else:
            logger.debug("cache hit for secret %s", secret_id)
            self.prom_client.tick_cache_hits("secret")
        return cached_secret

    def _load_secret_keys(self):
        logger.debug("generating secret key map")
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
            logger.debug("no key mapping found %s", secret_key)
            self.prom_client.tick_cache_miss("key")
            raise UnknownKeyException("Key not found")
        logger.debug("key mapping found %s", secret_key)
        return self.get_secret_by_id(key)

    def refresh_cache(self):
        secrets = self.client.get_updated_secrets()
        if secrets:
            self.reset_cache()
        with self.cache_lock:
            for secret in secrets:
                logger.debug("adding cache for secret %s, key %s", secret.id, secret.key)
                self.secret_cache[secret.id] = secret
                self.key_map[secret.key] = secret.id

    def reset_cache(self) -> CacheStats:
        logger.debug("resetting cache")
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


class ClientList:
    def __init__(self):
        self._clients: dict[str, CachedBWSClient] = {}
        self._clients_lock = Lock()

    def add_client(self, token: str, client: CachedBWSClient):
        hashed_token = generate_hash(token)
        with self._clients_lock:
            self._clients[hashed_token] = client
        logger.debug("adding client %s. total clients: %s", hashed_token, len(self._clients))

    def remove_client(self, hashed_token: str):
        with self._clients_lock:
            self._clients.pop(hashed_token, None)
        logger.debug("removed client %s. total clients: %s", hashed_token, len(self._clients))

    def get(self, token: str):
        hashed_token = generate_hash(token)
        with self._clients_lock:
            return self._clients.get(hashed_token, None)

    def list_clients(self):
        with self._clients_lock:
            return self._clients.copy().items()


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
                logger.debug("refreshing %s clients ", len(clients))
            for client_id, client in clients:
                logger.debug("refreshing client id: %s", client_id)
                try:
                    client.refresh_cache()
                except BWSAPIRateLimitExceededException:
                    logger.info("rate limit exceeded for client %s", client_id)
                    time.sleep(30)
                except InvalidTokenException:
                    logger.info("invalid token for client %s", client_id)
                    self.clients.remove_client(client_id)
                except CantSendRequestException:
                    logger.error("cant sent request to upstream for client for client %s", client_id)
                except Exception as e:
                    logger.error("error occored while refreshing client")
                    logger.debug(e, exc_info=True)
                    self.clients.remove_client(client_id)
                time.sleep(self.refresh_interval)


class BwsClientManager:
    def __init__(
        self,
        prom_client: PromMetricsClient,
        org_id: str,
        secret_refresh_interval: int,
        secret_request_interval: int,
    ):
        self.org_id = org_id
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

    def _make_client(self, bws_secret_token: str):
        client = CachedBWSClient(bws_secret_token, self.org_id, self.requester, self.prom_client)
        client.auth()
        return client

    def get_client_by_token(self, bws_secret_token) -> CachedBWSClient:
        client = self.client_list.get(bws_secret_token)
        if client is None:
            logger.debug("creating new client")
            client = self._make_client(bws_secret_token)

            self.client_list.add_client(bws_secret_token, client)
        return client

    def stats(self) -> StatsResponse:
        clients_stats: dict[str, CacheStats] = {}
        for hashed_token, client in self.client_list.list_clients():
            clients_stats[hashed_token] = client.stats()

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
