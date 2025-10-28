FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working dir to the evaluation_project folder
WORKDIR /code/evaluation_project

# System deps (ffmpeg for whisper/transcription; netcat to wait for services)
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         ffmpeg \
         netcat-openbsd \
     && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY evaluation_project/requirements.txt /code/requirements.txt

# Install dependencies with djongo compatibility fix
RUN pip install --upgrade pip setuptools wheel \
    && sed -e '/^djongo/d' -e "s/^sqlparse==0.2.4/sqlparse>=0.3.1/" /code/requirements.txt > /code/requirements-docker.txt \
    && cat /code/requirements-docker.txt \
    && pip install -r /code/requirements-docker.txt \
    && pip install djongo==1.3.6

# Copy the project into the image
COPY . /code

# Convert entrypoint.sh line endings from CRLF to LF and make it executable (done as root)
RUN apt-get update && apt-get install -y dos2unix && dos2unix /code/entrypoint.sh && apt-get remove -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN chmod +x /code/entrypoint.sh || true

# Create non-root user and switch
RUN useradd -m appuser || true
USER appuser

EXPOSE 8000

# Use entrypoint script and default to running gunicorn for evaluation_project
ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--reload", "--timeout", "120"]
