from flask import Flask, request, Response, make_response
from flask.json.provider import _default as _json_default
from flask_restful import Api, Resource

from bitwarden_sdk.bitwarden_client import BitwardenClient
from bitwarden_sdk.schemas import client_settings_from_dict, DeviceType, SecretResponse
import os
import functools
import time


from json import JSONEncoder, dumps
from datetime import datetime
from typing import Any

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

client = BitwardenClient(client_settings_from_dict({
    "apiUrl": "https://api.bitwarden.com",
    "deviceType": DeviceType.SDK,
    "identityUrl": "https://identity.bitwarden.com",
    "userAgent": "Python",
}))




auth_token_file = os.environ.get("SECRET_TOKEN_PATH", "")
if auth_token_file:
    with open(auth_token_file, 'r', encoding="utf-8") as f:
        auth_token = f.read()
else:
    auth_token = os.environ.get("SECRET_TOKEN", "")

bws_auth_token = os.environ.get("BWS_ACCESS_TOKEN", "")
bws_org_id = os.environ.get("BWS_ORG_ID", "")

secret_key_mapping_refresh_timeout = int(os.environ.get("SECRET_KEY_MAPPING_REFRESH_TIMEOUT", "0"))


client.access_token_login(bws_auth_token)

secret_cache = dict()

count_innit = 0

def update_secret_key_mapping():
    print("yippeee")
    key_mapping = dict()
    for secret in client.secrets().list(bws_org_id).data.data:
        key_mapping[secret.key] = secret.id

    return key_mapping

secret_key_mapping = update_secret_key_mapping()
secret_key_mapping_refresh = time.time()


def validate_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and auth_token == auth_header.split()[-1]:
            return func(*args, **kwargs)
        return "", 401

    return wrapper

class BwsCache(Resource):
    @validate_auth
    def get(self, secret_id_type, secret_id):
        st = time.time()
        if secret_id_type == "key":
            global secret_key_mapping_refresh
            global secret_key_mapping
            if time.time() - secret_key_mapping_refresh > secret_key_mapping_refresh_timeout:
                secret_key_mapping = update_secret_key_mapping()
                secret_key_mapping_refresh = time.time()
            secret_id = secret_key_mapping[secret_id]
        cached_secret = secret_cache.get(secret_id, None)
        if cached_secret is None:
            print("cache miss")
            try:

                secret_cache[secret_id] = client.secrets().get(secret_id).data
            except Exception as e:
                return {"error status": e.args[0]}, 500
        print(secret_cache[secret_id].__dict__)
        return secret_cache[secret_id]


api.add_resource(BwsCache, '/bws-cache/<string:secret_id_type>/<string:secret_id>')


if __name__ == '__main__':
    app.run(debug=True)
