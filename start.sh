#!/usr/bin/env bash
# Railway start script - launches Gunicorn with conservative settings for small RAM environments
set -euo pipefail

# Change to repository root, then into Django project
cd "$(dirname "$0")" || exit 1
cd evaluation_project || exit 1

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
# If gunicorn is missing (e.g., build didn't run), run build.sh from the repo root to install dependencies and collect static files.
if ! command -v gunicorn >/dev/null 2>&1; then
	echo "gunicorn not found — attempting to run build script to install dependencies..."
	if [ -f "$REPO_ROOT/build.sh" ]; then
		chmod +x "$REPO_ROOT/build.sh" || true
		"$REPO_ROOT/build.sh"
	else
		echo "build.sh not found at $REPO_ROOT; attempting pip install -r ../requirements.txt or evaluation_project/requirements.txt"
		# Try pip3 or python3 -m pip as fallbacks
		PIP_CMD=""
		if command -v pip >/dev/null 2>&1; then
			PIP_CMD="pip"
		elif command -v pip3 >/dev/null 2>&1; then
			PIP_CMD="pip3"
		elif command -v python3 >/dev/null 2>&1; then
			PIP_CMD="python3 -m pip"
		elif command -v python >/dev/null 2>&1; then
			PIP_CMD="python -m pip"
		else
			echo "No pip/python executable found in PATH. Cannot install dependencies at runtime." >&2
			echo "Recommendation: Configure Railway to run the build in the Build Command: './build.sh' (repo root) or set image to include Python and dependencies." >&2
			exit 1
		fi

		# prefer evaluation_project requirements file
		if [ -f "$REPO_ROOT/evaluation_project/requirements.txt" ]; then
			eval "$PIP_CMD install --upgrade pip"
			eval "$PIP_CMD install -r $REPO_ROOT/evaluation_project/requirements.txt"
		elif [ -f "$REPO_ROOT/requirements.txt" ]; then
			eval "$PIP_CMD install --upgrade pip"
			eval "$PIP_CMD install -r $REPO_ROOT/requirements.txt"
		else
			echo "No requirements.txt found; cannot install dependencies." >&2
			exit 1
		fi
	fi
fi

# Exec gunicorn with conservative settings to avoid OOM on small instances.
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 60
