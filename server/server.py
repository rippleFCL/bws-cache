from bitwarden_sdk.schemas import SecretResponse
from client import BWSClientManager, InvalidTokenException, UnauthorizedTokenException, BWSAPIRateLimitExceededException
from datetime import datetime
from flask import Flask, request
from flask_restful import Api, Resource
from flask.json.provider import _default as _json_default
from json import JSONEncoder, dumps
from typing import Any
import functools
import os
import logging


logger = logging.getLogger(__name__)


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


secret_info_ttl = int(os.environ.get("SECRET_TTL", "0"))

client_manager = BWSClientManager(secret_info_ttl)


def handle_api_errors(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                return func(self, auth_header.split()[-1], *args, **kwargs)
            except InvalidTokenException:
                return {"error": "invalid token"}, 400
            except UnauthorizedTokenException:
                return {"error": "unauthorized token"}, 401
            except BWSAPIRateLimitExceededException:
                return {"error": "rate limited"}, 429

        return {"error": "invalid auth header"}, 400
    return wrapper


class BwsCacheId(Resource):
    @handle_api_errors
    def get(self, auth_token, secret_id):
        with client_manager.get_client_by_token(auth_token) as client:
            client.authenticate()
            return client.get_secret_by_id(secret_id)


class BwsCacheKey(Resource):
    @handle_api_errors
    def get(self, auth_token, secret_id, ):
        org_id=os.environ.get("ORG_ID", request.headers.get("OrganizationId", ""))
        with client_manager.get_client_by_token(auth_token) as client:
            client.authenticate()
            return client.get_secret_by_key(secret_id, org_id)


api.add_resource(BwsCacheId, '/id/<string:secret_id>')
api.add_resource(BwsCacheKey, '/key/<string:secret_id>')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
