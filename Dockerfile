# Utiliser Python slim
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /code/evaluation_project

# Dépendances système (ffmpeg pour Whisper, netcat pour attendre MongoDB)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        netcat-openbsd \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY evaluation_project/requirements.txt /code/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && sed -e '/^djongo/d' -e "s/^sqlparse==0.2.4/sqlparse>=0.3.1/" /code/requirements.txt > /code/requirements-docker.txt \
    && pip install -r /code/requirements-docker.txt \
    && pip install djongo==1.3.6

# Copier le projet complet
COPY . /code

# Convertir entrypoint.sh en LF et le rendre exécutable
RUN dos2unix /code/entrypoint.sh && chmod +x /code/entrypoint.sh

# Créer un utilisateur non-root
RUN useradd -m appuser || true
USER appuser

# Exposer le port pour Azure
EXPOSE 80

# Entrypoint et commande par défaut
ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3", "--reload", "--timeout", "120"]
