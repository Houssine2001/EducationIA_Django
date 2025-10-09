#!/usr/bin/env python
"""Test direct de UserProfile avec les IDs MongoDB"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile
import pymongo

print("=" * 70)
print("🔍 TEST USERPROFILE AVEC IDS MONGODB")
print("=" * 70)

# Vérifier les IDs MongoDB directement
client = pymongo.MongoClient('localhost', 27017)
db = client['django_education']

print("\n1️⃣  IDs dans MongoDB:")
users_mongo = list(db.auth_user.find({}, {'_id': 1, 'username': 1}))
for u in users_mongo:
    print(f"   {u['username']}: _id = {u['_id']}")

profiles_mongo = list(db.evaluation_userprofile.find({}, {'_id': 1, 'user_id': 1, 'role': 1}))
print("\n2️⃣  Profiles dans MongoDB:")
for p in profiles_mongo:
    print(f"   Profile: user_id={p['user_id']}, role={p.get('role', 'N/A')}")

# Test Django ORM
print("\n3️⃣  Test Django ORM - User.objects.get():")
try:
    user = User.objects.get(username='prof1')
    print(f"   Username: {user.username}")
    print(f"   ID (Django): {user.id}")
    print(f"   PK (Django): {user.pk}")
    print(f"   Type ID: {type(user.id)}")
    
    # Essayer d'accéder au profil via related_name
    print("\n4️⃣  Test user.profile:")
    try:
        profile = user.profile
        print(f"   ✅ Profile trouvé: {profile.role}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Essayer avec UserProfile.objects.get directement
    print("\n5️⃣  Test UserProfile.objects.get(user=user):")
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"   ✅ Profile trouvé: {profile.role}")
    except Exception as e:
        print(f"   ❌ Erreur: {type(e).__name__}: {e}")
    
    # Essayer avec l'ID MongoDB exact
    print("\n6️⃣  Test UserProfile.objects.get(user_id=32):")
    try:
        profile = UserProfile.objects.get(user_id=32)
        print(f"   ✅ Profile trouvé: {profile.role}")
        print(f"   ✅ User: {profile.user.username}")
    except Exception as e:
        print(f"   ❌ Erreur: {type(e).__name__}: {e}")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
