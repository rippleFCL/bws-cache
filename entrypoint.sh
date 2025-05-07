#!/bin/ash
  if [ -z "${1}" ]; then
    cd ${APP_ROOT}
    set -- "uvicorn" \
      server:api
  fi

  exec "$@"