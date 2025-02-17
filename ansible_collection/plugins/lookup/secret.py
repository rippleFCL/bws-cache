from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: secret
    author: tigattack (@tigattack)
    version_added: "1.0.0"
    requirements:
      - requests Python package
      - E(BWS_ACCESS_TOKEN) environment variable
      - E(BWS_CACHE_URL) environment variable
    short_description: Retrieve secrets from bws-cache
    description:
      - Lookup a secret from Bitwarden Secrets Manager Cache (bws-cache) by secret ID or key.
    options:
      _terms:
        description: Secret ID or key
        example: my_secret_id
        required: true
        type: str
"""

EXAMPLES = """
- name: Retrieve secret by ID
  ansible.builtin.debug:
    msg: >-
      {{ lookup('ripplefcl.bwscache.secret', '01fae166-302b-4e75-b7a4-c6887ef7e3a8') }}

- name: Retrieve secret by key
  ansible.builtin.debug:
    msg: >-
      {{ lookup('ripplefcl.bwscache.secret', 'my_secret_key') }}
"""

RETURN = """
  _raw:
    description: Retrieved secret
    type: str
    returned: success
    sample: '{"id": "01fae166-302b-4e75-b7a4-c6887ef7e3a8", "key": "my_secret_key", "value": "my_secret_value"}'
"""

import http.client  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import uuid  # noqa: E402
from urllib.parse import urlparse  # noqa: E402

from ansible.errors import (  # type: ignore # noqa: E402
    AnsibleLookupError,
    AnsibleUndefinedVariable,
)
from ansible.plugins.lookup import LookupBase  # type: ignore # noqa: E402
from ansible.utils.display import Display  # type: ignore # noqa: E402

display = Display()


class BwsCacheSecretLookupException(AnsibleLookupError):
    pass


class BwsCacheSecretLookup:
    def __init__(self) -> None:
        self.bws_token = os.environ.get("BWS_ACCESS_TOKEN")
        self.bws_cache_url = os.environ.get("BWS_CACHE_URL")
        self.headers = {"Authorization": f"Bearer {self.bws_token}"}

    def is_valid_uuid(self, val):
        """Check if input is a valid UUID"""
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    def make_request(self, endpoint: str):
        """Perform an HTTP GET request to the specified endpoint."""
        if not self.bws_cache_url:
            raise AnsibleUndefinedVariable(
                "BWS_CACHE_URL environment variable must be set."
            )

        parsed_url = urlparse(self.bws_cache_url)
        conn = (
            http.client.HTTPSConnection(parsed_url.netloc, timeout=5)
            if parsed_url.scheme == "https"
            else http.client.HTTPConnection(parsed_url.netloc, timeout=5)
        )

        try:
            conn.request("GET", f"{parsed_url.path}{endpoint}", headers=self.headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            if response.status == 200:
                return json.loads(data)
            raise BwsCacheSecretLookupException(
                f"Failed to retrieve secret: {response.status} - {data.decode()}"
            )
        except (http.client.HTTPException, TimeoutError) as err:
            raise BwsCacheSecretLookupException(
                f"Error while querying bws-cache: {err}"
            )

    def get_secret(self, secret_identifier: str):
        """Get and return the secret with the given secret_id or secret_key."""
        if not self.bws_token:
            raise AnsibleUndefinedVariable(
                "BWS_ACCESS_TOKEN environment variable must be set."
            )

        if self.is_valid_uuid(secret_identifier):
            display.verbose("bws_cache: input matches UUID format; retrieving by ID.")
            return self.make_request(f"/id/{secret_identifier}")
        else:
            display.verbose(
                "bws_cache: input does not match UUID format; retrieving by key."
            )
            return self.make_request(f"/key/{secret_identifier}")


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):  # type: ignore
        bws_cache = BwsCacheSecretLookup()
        return [bws_cache.get_secret(term) for term in terms]
