#!/usr/bin/env bash
# Railway start script - launches Gunicorn with conservative settings for small RAM environments
set -e

# Go to Django project
cd evaluation_project

# Ensure virtualenv/venv activate is handled by Railway environment; just run Gunicorn
# Use 1 worker and 2 threads to reduce memory usage on small hosts
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 60
