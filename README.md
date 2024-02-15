# Bitwarden Secrets Manager Cache

Python app implementing a read-through cache for Bitwarden Secrets Manager (BWS) secrets.

# Usage

When a secret is queried, not only is the secret cached in memory, but a mapping between ID and key is also cached.

This allows lookup by either ID or key, as shown below.

## Endpoints

* `/id/<string:secret_id>`
* `/key/<string:secret_key>`
* `/reset`

## Authentication

bws-cache delegates authentication to the BWS client library, rather than requiring a defined token for client authentication.

A valid BWS access token should be passed as a bearer token in the `Authorization` header, as shown in the examples below.

## Examples

Query secret by ID: `curl -H "Authorization: Bearer <BWS token>" http://localhost:5000/id/<secret_id>`

Query secret by key: `curl -H "Authorization: Bearer <BWS token>" http://localhost:5000/key/my_secret`

Invalidate the secret cache: `curl -H "Authorization: Bearer <BWS token>" http://localhost:5000/reset`

# Run

You can get your BWS organisation ID two ways:
* From BWS CLI:
  * `bws project list` / `bws project get <project_id>` - Your organisation ID is shown in the `organizationId` value of each project returned.
  * `bws secret list` / `bws secret get <secret_id>` - Your organisation ID is shown in the `organizationId` value of each secret returned.
* From browser:
  1. Go to https://vault.bitwarden.com
  2. Open Secrets Manager from the apps list in the top right
  3. Your organisation ID is in the URL like this: `https://vault.bitwarden.com/#/sm/<BWS org ID>`

```
docker run \
  -p 5000:5000 \
  -e ORG_ID=<org ID> \
  ghcr.io/ripplefcl/bws-cache:latest
```

## Environment Variables

| Name         | Info                                                 | Default |
|--------------|------------------------------------------------------|---------|
| `ORG_ID`     | Your BWS organisation ID.                            |         |
| `SECRET_TTL` | TTL of cached secrets and secret ID-to-key mappings. | `600`   |
| `DEBUG`      | Enable debug logging. Defaults to `false`.           | `false` |

# Internal notes

For reference on how internally this cache works. on a key based secret lookup
the app does a org wide list of all secrets and stores a cache of the keys and their
relating ids. this 'key_map_cache' also abides by the secret ttl and refreshes this
entire cache when it expires.
