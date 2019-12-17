#!/bin/bash

set -euo

cmd="$@"

echo Waiting for Postgres
sleep 5

while !</dev/tcp/db/5432; do
  echo Postgres is not yet available
  sleep 5
done

echo PostgreSQL started up successfully

echo Activating virtual environment
source /home/venv/bin/activate

if [ $1 = "gunicorn" ]; then
  echo Initializing app
  python manage.py collectstatic --noinput
  python manage.py migrate --noinput
fi

exec $cmd