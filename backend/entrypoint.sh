#! /usr/bin/env bash
set -e

# Run migrations
prisma generate

if [ "$1" = "api" ] ; then
  prisma migrate deploy
  if [ -f /src/app/main.py ]; then
      DEFAULT_MODULE_NAME=app.main
  elif [ -f /src/main.py ]; then
      DEFAULT_MODULE_NAME=main
  fi
  MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
  VARIABLE_NAME=${VARIABLE_NAME:-app}
  export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}
  if [ -f /app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/src/gunicorn_conf.py
  elif [ -f /app/app/gunicorn_conf.py ]; then
      DEFAULT_GUNICORN_CONF=/src/app/gunicorn_conf.py
  else
      DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
  fi
  export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}
  export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
  export LOGGER_CLASS=${LOGGER_CLASS:-"app.core.init_logging.Logger"}
  gunicorn -k "$WORKER_CLASS" --logger-class "$LOGGER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
elif [ "$1" = "worker" ] ; then
  arq app.worker.main.WorkerSettings
else
  echo "Wrong run command, make sure to pass an argument to the entrypoint, available arguments: api, worker"
  exit 126
fi
