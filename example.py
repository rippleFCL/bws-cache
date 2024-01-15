import json
import logging
import sys
from bitwarden_sdk.bitwarden_client import BitwardenClient
from bitwarden_sdk.schemas import client_settings_from_dict, DeviceType

# Create the BitwardenClient, which is used to interact with the SDK
client = BitwardenClient(client_settings_from_dict({
    "apiUrl": "http://localhost:4000",
    "deviceType": DeviceType.SDK,
    "identityUrl": "http://localhost:33656",
    "userAgent": "Python",
}))

# Add some logging & set the org id
logging.basicConfig(level=logging.DEBUG)

# Attempt to authenticate with the Secrets Manager Access Token

# -- Example Project Commands --

# -- Example Secret Commands --

secret_retrieved = client.secrets().get(secret.data.id)

print(client.secrets().list(organization_id))
