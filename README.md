# Bitwarden Secrets Manager Cache

Python app implementing a read-through cache for BWS secrets.

# Run

```
docker run \
  -p 5000:5000 \
  -e BWS_ORG_ID=<org ID> \
  -e BWS_ACCESS_TOKEN=<bws token> \
  -e SECRET_TOKEN=<client auth token> \
  ghcr.io/rippleFCL/bws-cache:latest
```

```
docker run \
  -p 5000:5000 \
  -e BWS_ORG_ID=<org ID> \
  -e BWS_ACCESS_TOKEN_FILE=/app/bws_token \
  -e SECRET_TOKEN=/app/client_auth_token \
  -v ./bws_token:/app/bws_token \
  -v ./client_auth_token:/app/client_auth_token \
  ghcr.io/rippleFCL/bws-cache:latest
```

## Environment Variables

| Name                    | Info                                                                                            |
|-------------------------|-------------------------------------------------------------------------------------------------|
| `BWS_ORG_ID`            | Your BWS organisation ID.                                                                       |
| `BWS_ACCESS_TOKEN_FILE` | File containing BWS access token for bws-cache authentication.                                  |
| `BWS_ACCESS_TOKEN`      | BWS access token for bws-cache authentication.<br>Required if `BWS_ACCESS_TOKEN_FILE` is unset. |
| `SECRET_TOKEN_FILE`     | File containing string for client authentication to bws-cache.                                  |
| `SECRET_TOKEN`          | String for client authentication to bws-cache.<br>Required if `SECRET_TOKEN_FILE` is unset.     |
| `LOG_LEVEL`             | App logging level. Defaults to `INFO`.                                                          |
