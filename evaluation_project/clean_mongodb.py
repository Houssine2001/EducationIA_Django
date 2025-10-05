"""
Script pour nettoyer la base de données MongoDB
"""
import pymongo

# Connexion à MongoDB
client = pymongo.MongoClient('localhost', 27017)
db = client['evaluation_db']

print("🧹 Nettoyage de la base de données MongoDB...")
print(f"📊 Collections existantes : {db.list_collection_names()}\n")

# Supprimer toutes les collections
collections_to_drop = [
    'user_profiles',
    'tests',
    'questions',
    'submissions',
    'results',
    'auth_user',
    'django_migrations',
    'django_session'
]

for collection in collections_to_drop:
    if collection in db.list_collection_names():
        db[collection].drop()
        print(f"  ✅ Collection '{collection}' supprimée")
    else:
        print(f"  ⚪ Collection '{collection}' n'existe pas")

print("\n✅ Nettoyage terminé ! La base de données est vide.")
print("Vous pouvez maintenant exécuter : python manage.py migrate")

client.close()
