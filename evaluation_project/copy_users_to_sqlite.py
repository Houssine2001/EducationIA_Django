"""
Script pour copier les utilisateurs de MongoDB vers SQLite
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from pymongo import MongoClient

# Connexion à MongoDB
mongo_client = MongoClient('localhost', 27017)
db = mongo_client['evaluation_db']

print("Copie des utilisateurs de MongoDB vers SQLite...")

# Récupérer les utilisateurs depuis MongoDB
users_collection = db['auth_user']
users_mongo = list(users_collection.find())

print(f"Trouvé {len(users_mongo)} utilisateurs dans MongoDB")

# Copier chaque utilisateur vers SQLite
for user_data in users_mongo:
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=user_data['username']).exists():
            print(f"  - {user_data['username']} existe déjà dans SQLite")
            continue
        
        # Créer l'utilisateur dans SQLite
        user = User.objects.create(
            id=user_data['id'],
            username=user_data['username'],
            password=user_data['password'],
            email=user_data.get('email', ''),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_staff=user_data.get('is_staff', False),
            is_active=user_data.get('is_active', True),
            is_superuser=user_data.get('is_superuser', False),
            date_joined=user_data.get('date_joined'),
            last_login=user_data.get('last_login')
        )
        print(f"  ✓ {user_data['username']} copié vers SQLite")
    except Exception as e:
        print(f"  ✗ Erreur pour {user_data['username']}: {e}")

print("\n✅ Migration des utilisateurs terminée!")
print(f"Total utilisateurs dans SQLite: {User.objects.count()}")
