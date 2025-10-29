"""
Utilitaires pour la connexion MongoDB
Compatible avec Render (MONGO_URI) et local (MONGO_HOST/MONGO_PORT)
"""
from pymongo import MongoClient
from django.conf import settings


def get_mongodb_client():
    """
    Obtenir un client MongoDB compatible avec les deux configurations:
    - Render: MONGO_URI (chaîne de connexion complète)
    - Local: MONGO_HOST + MONGO_PORT
    
    Returns:
        MongoClient: Client MongoDB connecté
    """
    # Priorité 1: MONGO_URI (pour Render et MongoDB Atlas)
    mongo_uri = getattr(settings, 'MONGO_URI', None)
    if mongo_uri:
        return MongoClient(mongo_uri)
    
    # Priorité 2: MONGO_HOST + MONGO_PORT (pour développement local)
    mongo_host = getattr(settings, 'MONGO_HOST', 'localhost')
    mongo_port = getattr(settings, 'MONGO_PORT', 27017)
    return MongoClient(mongo_host, mongo_port)


def get_mongodb_database():
    """
    Obtenir la base de données MongoDB configurée
    
    Returns:
        Database: Base de données MongoDB
    """
    client = get_mongodb_client()
    db_name = getattr(settings, 'MONGO_DB_NAME', 'django_education')
    return client[db_name]
