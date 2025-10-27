Dockerisation rapide du projet EducationIA

Ce fichier explique comment démarrer le projet avec Docker (dev / testing). Il suppose que Docker et Docker Compose sont installés.

1) Fichiers ajoutés
- `Dockerfile` - image Python 3.11 basée sur slim, installe les dépendances depuis `evaluation_project/requirements.txt`.
- `docker-compose.yml` - orchestre `web` (Django) et `mongo` (MongoDB).
- `entrypoint.sh` - attend MongoDB, applique les migrations et collecte les fichiers statiques avant de lancer Gunicorn.
- `.dockerignore` - réduit le contexte envoyé au démon Docker.

2) Variables d'environnement
Créez un fichier `.env` à la racine (ne commitez pas) et définissez au minimum :

DJANGO_SECRET_KEY=changeme
DEBUG=1
MONGO_HOST=mongo
MONGO_PORT=27017

3) Démarrage en local

Build et lance les services :

```powershell
docker compose up --build
```

L'application sera exposée sur http://localhost:8000

4) Notes et limitations
- Le `requirements.txt` utilisé est `evaluation_project/requirements.txt`. Si votre fichier est ailleurs, adaptez le `Dockerfile`.
- Le projet contient des dépendances lourdes (torch, transformers, etc.) : l'image finale peut être très volumineuse. Pour du dev simple, envisagez de commenter les paquets lourds.
- `settings.py` a été modifié pour lire `DJANGO_SECRET_KEY`, `DEBUG` et `MONGO_HOST/MONGO_PORT` depuis les variables d'environnement. Vérifiez ces changements avant un déploiement en production.
