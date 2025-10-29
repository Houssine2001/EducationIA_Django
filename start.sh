#!/usr/bin/env bash
# Railway start script - launches Gunicorn with conservative settings for small RAM environments
set -euo pipefail

# Change to repository root, then into Django project
cd "$(dirname "$0")" || exit 1
cd evaluation_project || exit 1

# If gunicorn is missing (e.g., build didn't run), run build.sh to install dependencies and collect static files.
if ! command -v gunicorn >/dev/null 2>&1; then
	echo "gunicorn not found — running build.sh to install dependencies..."
	if [ -f ./build.sh ]; then
		chmod +x ./build.sh || true
		./build.sh
	else
		echo "build.sh not found; attempting pip install -r requirements.txt"
		if [ -f requirements.txt ]; then
			python -m pip install --upgrade pip
			python -m pip install -r requirements.txt
		else
			echo "No requirements.txt found; cannot install dependencies." >&2
			exit 1
		fi
	fi
fi

# Exec gunicorn with conservative settings to avoid OOM on small instances.
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 60
