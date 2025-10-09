#!/usr/bin/env python
"""
Script pour corriger les roles manquants dans UserProfile
"""
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client['django_education']

print("=" * 70)
print("🔧 CORRECTION DES ROLES DANS USERPROFILE")
print("=" * 70)

# Mapping des IDs vers les roles basé sur auth_user
users = {
    32: 'teacher',    # prof1
    42: 'student',    # etudiant1
    43: 'student',    # etudiant2
    44: 'student',    # etudiant3
}

profiles = db.evaluation_userprofile

for user_id, role in users.items():
    result = profiles.update_one(
        {'user_id': user_id},
        {'$set': {'role': role}}
    )
    
    if result.modified_count > 0:
        print(f"   ✅ user_id={user_id} → role={role}")
    else:
        print(f"   ⚠️  user_id={user_id} non trouvé ou déjà à jour")

# Vérification
print("\n📊 Vérification des profiles:")
for profile in profiles.find({}, {'user_id': 1, 'role': 1, '_id': 0}):
    print(f"   user_id={profile['user_id']}: role={profile.get('role', 'None')}")

print("\n" + "=" * 70)
