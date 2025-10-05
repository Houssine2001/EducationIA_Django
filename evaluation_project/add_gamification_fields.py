"""
Script pour ajouter les champs de gamification aux profils existants
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import UserProfile
from pymongo import MongoClient

print("🔧 Ajout des champs de gamification aux profils existants...")

# Connexion à MongoDB
client = MongoClient('localhost', 27017)
db = client['evaluation_db']
collection = db['user_profiles']

# Mettre à jour tous les profils avec les nouveaux champs
result = collection.update_many(
    {},  # Tous les documents
    {
        '$set': {
            'level': 1,
            'total_xp': 0,
            'badges': []
        }
    }
)

print(f"✅ {result.modified_count} profils mis à jour avec les champs de gamification")

# Marquer la migration comme appliquée
from django.db import connection
cursor = connection.cursor()

try:
    # Fake la migration
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
        ['evaluation', '0002_userprofile_badges_userprofile_level_and_more']
    )
    print("✅ Migration 0002 marquée comme appliquée")
except Exception as e:
    print(f"⚠️  Migration déjà appliquée ou erreur: {e}")

# Vérifier les profils
profiles = UserProfile.objects.all()
print(f"\n📊 Vérification des profils:")
for profile in profiles:
    print(f"  - {profile.user.username}: Niveau {profile.level}, XP {profile.total_xp}, Badges {len(profile.badges or [])}")

print("\n✅ Opération terminée !")
