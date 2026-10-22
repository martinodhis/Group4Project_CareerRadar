#!/bin/sh
set -eu

python -m flask --app migration_app db upgrade
exec python -m gunicorn --bind "0.0.0.0:${PORT:-10000}" --access-logfile - --error-logfile - run:app
