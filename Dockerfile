# ╔═════════════════════════════════════════════════════╗
# ║                       SETUP                         ║
# ╚═════════════════════════════════════════════════════╝
  # globals
  ARG APP_UID=1000 \
      APP_GID=1000 \
      APP_ROOT=/app


# ╔═════════════════════════════════════════════════════╗
# ║                       BUILD                         ║
# ╚═════════════════════════════════════════════════════╝
  FROM python:3.12-alpine AS requirement-builder
  ARG APP_ROOT \
      PIP_ROOT_USER_ACTION=ignore \
      PIP_BREAK_SYSTEM_PACKAGES=1 \
      PIP_DISABLE_PIP_VERSION_CHECK=1 \
      PIP_NO_CACHE_DIR=1

  RUN set -ex; \
    pip install poetry poetry-plugin-export

  COPY ./pyproject.toml / \
       ./poetry.lock /

  RUN set -ex; \
    poetry export --without-hashes -f requirements.txt --output requirements.txt;

  FROM python:3.12-alpine AS bitwarden-sdk
  # source https://pypi.org/project/bitwarden-sdk/
  # sadly we need to build the bitwarden-sdk from scratch and even add the missing license file which is still not fixed!
  ARG APP_ROOT \
      PIP_ROOT_USER_ACTION=ignore \
      PIP_BREAK_SYSTEM_PACKAGES=1 \
      PIP_DISABLE_PIP_VERSION_CHECK=1 \
      PIP_NO_CACHE_DIR=1

  RUN set -ex; \
    apk --no-cache --update add \
      git \
      curl \
      cargo \
      rust \
      py3-setuptools \
      py3-maturin \
      py3-gpep517 \
      py3-wheel; \
    curl -SL https://files.pythonhosted.org/packages/dd/03/11934ae9d668283895286872a7af3de25d324ec9ac86da5a56ac9dc48544/bitwarden_sdk-1.0.0.tar.gz | tar -zxC /; \
    cd bitwarden_sdk-1.0.0; \
    curl -SL https://raw.githubusercontent.com/bitwarden/sdk/refs/heads/main/LICENSE --output LICENSE; \
    gpep517 build-wheel \
      --wheel-dir .dist \
      --output-fd 3 3>&1 >&2;


# ╔═════════════════════════════════════════════════════╗
# ║                       IMAGE                         ║
# ╚═════════════════════════════════════════════════════╝
# :: HEADER
  FROM 11notes/alpine:stable
  USER root

  # arguments
  ARG PIP_ROOT_USER_ACTION=ignore \
      PIP_BREAK_SYSTEM_PACKAGES=1 \
      PIP_DISABLE_PIP_VERSION_CHECK=1 \
      PIP_NO_CACHE_DIR=1 \
      APP_UID \
      APP_GID \
      APP_ROOT  

  # environment
  ENV APP_ROOT=${APP_ROOT} \
      PYTHONUNBUFFERED=1 \
      ORG_ID= \
      UVICORN_HOST=0.0.0.0 \
      UVICORN_PORT=5000

# :: SETUP
  # dependencies
  RUN set -ex; \
    apk --no-cache --update add \
      python3; \
    apk --no-cache --update --virtual .setup add \
      py3-pip;

  RUN set -ex; \
    mkdir -p ${APP_ROOT}

  # multi-stage
  COPY --from=requirement-builder /requirements.txt ${APP_ROOT}
  COPY --from=bitwarden-sdk /bitwarden_sdk-1.0.0/target/wheels/bitwarden_sdk-1.0.0-cp312-cp312-linux_x86_64.whl /tmp
  COPY ./server/ ${APP_ROOT}
  COPY ./entrypoint.sh /usr/local/bin

  # install application
  RUN set -ex; \
    pip3 install /tmp/bitwarden_sdk-1.0.0-cp312-cp312-linux_x86_64.whl; \
    pip3 install -r ${APP_ROOT}/requirements.txt; \
    apk del --no-network .setup; \
    rm -rf /tmp/*;

  # set permissions
  RUN set -ex; \  
    chmod +x -R /usr/local/bin; \
    chown -R ${APP_UID}:${APP_GID} \
      ${APP_ROOT};

# :: HEALTH
  HEALTHCHECK --interval=15s --timeout=10s --start-period=15s \
    CMD ["curl", "-kILs", "--fail", "http://localhost:5000/healthcheck"]

# :: RUN  
  USER ${APP_UID}:${APP_GID}