import functools
import logging
import os
import time
from datetime import datetime
from json import JSONEncoder
from typing import Any

from bitwarden_sdk.schemas import SecretResponse
from client import (BWSAPIRateLimitExceededException, BWSClientManager,
                    InvalidTokenException, UnauthorizedTokenException,
                    UnsetOrgIdException, BWSSecretNotFound, BWSKeyNotFound)
from flask import Flask, request
from flask.json.provider import _default as _json_default
from flask_restful import Api, Resource
from prom_client import PromMetricsClient

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


logger = logging.getLogger(__name__)

debug_environ = os.environ.get('DEBUG', "")
debug = debug_environ.lower() == "true"

if debug:
    logger.setLevel(logging.DEBUG)


ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class BWJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, SecretResponse):
            return {
                "".join(x.capitalize() if index != 0 else x for index, x in enumerate(key.lower().split("_"))): value
                for key, value in o.__dict__.items()
            }
        if isinstance(o, datetime):
            return o.isoformat()
        return _json_default(o)


app = Flask(__name__)
api = Api(app)

app.config["RESTFUL_JSON"] = {
    "cls": BWJSONEncoder
}


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
client_manager = BWSClientManager(SECRET_INFO_TTL, prom_client)


def handle_api_errors(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                return func(self, auth_header.split()[-1], *args, **kwargs)
            except InvalidTokenException:
                return {"error": "Invalid token"}, 400
            except UnauthorizedTokenException:
                return {"error": "Unauthorized token"}, 401
            except BWSAPIRateLimitExceededException:
                return {"error": "Rate limited"}, 429
            except UnsetOrgIdException:
                return {"error": "Unset org id"}, 400
            except BWSSecretNotFound:
                return {"error": "Secret not found"}, 404
            except BWSKeyNotFound:
                return {"error": "Key not found"}, 404
        return {"error": "invalid auth header"}, 400
    return wrapper


def prom_stats(endpoint):
    def wrapper(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            st = time.time()
            return_data, return_code, *vals = func(self, *args, **kwargs)
            prom_client.tick_http_request_total(endpoint, return_code)
            prom_client.tick_http_request_duration(endpoint, time.time() - st)
            return return_data, return_code, *vals
        return inner
    return wrapper


class BwsReset(Resource):
    @prom_stats("/reset")
    @handle_api_errors
    def get(self, auth_token):
        with client_manager.get_client_by_token(auth_token) as client:
            client.authenticate(cache=False)
            client.reset_cache()
            return {"status": "success"}, 200


class BwsCacheId(Resource):
    @prom_stats("/id")
    @handle_api_errors
    def get(self, auth_token, secret_id):
        with client_manager.get_client_by_token(auth_token) as client:
            client.authenticate()
            return client.get_secret_by_id(secret_id), 200


class BwsCacheKey(Resource):
    @prom_stats("/key")
    @handle_api_errors
    def get(self, auth_token, secret_id, ):
        org_id = os.environ.get(
            "ORG_ID", request.headers.get("OrganizationId", ""))
        with client_manager.get_client_by_token(auth_token) as client:
            client.authenticate()
            return client.get_secret_by_key(secret_id, org_id, refresh_keymap_on_miss), 200


api.add_resource(BwsReset, '/reset')
api.add_resource(BwsCacheId, '/id/<string:secret_id>')
api.add_resource(BwsCacheKey, '/key/<string:secret_id>')


@app.route("/metrics")
def prometheus_metrics():
    accept_header = request.headers.get("Accept")

    generated_data, content_type = prom_client.generate_metrics(accept_header)
    headers = {'Content-Type': content_type}
    return generated_data, 200, headers


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
