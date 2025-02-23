#!/usr/bin/env bash
set -e

for i in {1..10}; do
  if nc -z db 5432; then
    echo "Database is up!"
    break
  fi
  echo "Waiting for DB..."
  sleep 3
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_default_superuser

exec gunicorn qfield_coastal_manager.wsgi:application --bind 0.0.0.0:8000
