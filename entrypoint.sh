#!/bin/sh
set -e

# Ensure we're in the evaluation_project directory where manage.py lives
cd /code/evaluation_project || cd /code || true

# Wait for MongoDB to be available
MONGO_HOST=${MONGO_HOST:-mongo}
MONGO_PORT=${MONGO_PORT:-27017}

echo "Waiting for MongoDB at $MONGO_HOST:$MONGO_PORT..."
while ! nc -z "$MONGO_HOST" "$MONGO_PORT"; do
  echo "MongoDB is unavailable - sleeping"
  sleep 1
done
echo "MongoDB is up - continuing"

# Collect static files and run migrations (best-effort)
echo "Apply database migrations (if any)"
python manage.py migrate --noinput || true

echo "Collect static files"
python manage.py collectstatic --noinput --clear || true

exec "$@"
