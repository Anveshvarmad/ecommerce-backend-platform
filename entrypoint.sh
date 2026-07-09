#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Waiting for Redis..."
while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done
echo "Redis is ready."

if [ "$RUN_MIGRATIONS" = "True" ]; then
  echo "Running database migrations..."
  python manage.py migrate --noinput
fi

if [ "$COLLECT_STATIC" = "True" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
