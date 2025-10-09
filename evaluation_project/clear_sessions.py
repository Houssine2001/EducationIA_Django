"""
Script pour nettoyer les sessions MongoDB et résoudre les problèmes CSRF
"""
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('localhost', 27017)
db = client['django_education']

# Nettoyer les sessions
result = db.django_session.delete_many({})
print(f"✅ {result.deleted_count} sessions supprimées")

# Fermer la connexion
client.close()
print("✅ Sessions nettoyées avec succès!")
print("\n📝 Maintenant:")
print("1. Fermez tous les onglets du navigateur")
print("2. Ouvrez une fenêtre privée/incognito")
print("3. Allez sur http://127.0.0.1:8000/accounts/login/")
print("4. Connectez-vous avec: prof1 / password123")
