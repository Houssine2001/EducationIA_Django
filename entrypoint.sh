#!/bin/sh
set -e

# Aller au répertoire où se trouve manage.py
cd /code/evaluation_project || cd /code || true

# Variables MongoDB
MONGO_HOST=${MONGO_HOST:-mongo}
MONGO_PORT=${MONGO_PORT:-27017}

# Attente de MongoDB avec timeout
MAX_RETRIES=30
COUNT=0
echo "Waiting for MongoDB at $MONGO_HOST:$MONGO_PORT..."
while ! nc -z "$MONGO_HOST" "$MONGO_PORT"; do
  COUNT=$((COUNT+1))
  echo "MongoDB is unavailable - sleeping ($COUNT/$MAX_RETRIES)"
  sleep 2
  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    echo "MongoDB did not start in time, exiting..."
    exit 1
  fi
done
echo "MongoDB is up - continuing"

# Afficher versions pour debug
echo "Python version: $(python --version)"
echo "Django version: $(python -m django --version)"

# Migrations et collecte statiques
echo "Applying database migrations..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Exécuter la commande passée (Gunicorn)
exec "$@"
