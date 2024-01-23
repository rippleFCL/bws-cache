from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict

import time
from threading import Lock
import logging
import functools
import os

logger = logging.getLogger(__name__)

debug = True if os.environ.get('DEBUG', False) == "true" else False

if debug:
    logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class InvalidTokenException(Exception):
    pass


class UnauthorizedTokenException(Exception):
    pass

class BWSAPIRateLimitExceededException(Exception):
    pass

class BWSClient:
    def __init__(self, bws_client: BitwardenClient, bws_token: str, client_lock:Lock, secret_info_ttl):
        self.bws_token = bws_token
        self.bws_client_lock = client_lock
        self.bws_client = bws_client
        self.secret_cache = dict()
        self.secret_cache_ttl = dict()
        self.secret_key_map = dict()
        self.secret_key_map_refresh = 0
        self.secret_info_ttl = secret_info_ttl
        self.errored = False

    def __enter__(self):
        self.bws_client_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.bws_client_lock.release()


    def authenticate(self):
        try:
            logger.debug("authenticating client")
            self.bws_client.access_token_login(self.bws_token, f"/tmp/token_{hash(self.bws_token)}") #fixme: when rapid requests made with valid but expired token, this line hangs indefinitely
        except Exception as e:
            self.errored = True
            if "400 Bad Request" in e.args[0] or "Access token is not in a valid format" in e.args[0]:
                raise InvalidTokenException("Invalid token") from e
            raise e

    @staticmethod
    def _handle_api_errors(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.errored = True
                if "401 Unauthorized" in e.args[0]:
                    raise UnauthorizedTokenException("Unauthorized token") from e
                elif "429 Too Many Requests" in e.args[0]:
                    raise BWSAPIRateLimitExceededException("too many requests") from e
                raise e
        return wrapper

    @_handle_api_errors
    def _gen_secret_key_map(self, org_id):
        key_mapping = dict()
        for secret in self.bws_client.secrets().list(org_id).data.data:
            key_mapping[secret.key] = secret.id
        self.secret_key_map = key_mapping
        self.secret_key_map_refresh = time.time()

    @_handle_api_errors
    def _get_secret_from_client(self, secret_uuid:str):
            return self.bws_client.secrets().get(secret_uuid).data

    def reset_cache(self):
        self.secret_cache = dict()
        self.secret_cache_ttl = dict()
        logger.debug("resetting secret cache")
        self.secret_key_map = dict()
        self.secret_key_map_refresh = 0
        logger.debug("resetting secret key map")



    def get_secret_by_id(self, secret_id):
        cached_secret = self.secret_cache.get(secret_id, None)
        if cached_secret is None or time.time() - self.secret_cache_ttl[secret_id] > self.secret_info_ttl:
            logger.debug("cache miss for secret %s", secret_id)
            self.secret_cache[secret_id] = self._get_secret_from_client(secret_id)
            self.secret_cache_ttl[secret_id] = time.time()
        else:
            logger.debug("cache hit for secret %s", secret_id)

        return self.secret_cache[secret_id]

    def get_secret_by_key(self, secret_key, org_id):
        if not self.secret_key_map or time.time() - self.secret_key_map_refresh > self.secret_info_ttl:
            logger.debug("regenerating secret key map")
            self._gen_secret_key_map(org_id)
        return self.get_secret_by_id(self.secret_key_map[secret_key])

class BWSClientManager:
    def __init__(self, secret_info_ttl=0):
        self.secret_info_ttl = secret_info_ttl
        self.bws_client = self.make_client()
        self.clients = dict()
        self.client_lock = Lock()


    def make_client(self):
        return BitwardenClient(client_settings_from_dict({
            "apiUrl": "https://api.bitwarden.com",
            "deviceType": DeviceType.SDK,
            "identityUrl": "https://identity.bitwarden.com",
            "userAgent": "Python",
        }))

    def get_client_by_token(self, bws_secret_token) -> BWSClient:
        client = self.clients.get(bws_secret_token, None)
        if client is None:
            client = BWSClient(self.bws_client, bws_secret_token, self.client_lock, self.secret_info_ttl)
            self.clients[bws_secret_token] = client
        return client
