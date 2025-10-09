"""
Script de test complet du système
Tests: Login, Register, Tests, IA, Dashboard
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from evaluation.models import Test, UserProfile
from pymongo import MongoClient

print("="*70)
print("🧪 TESTS COMPLETS DU SYSTÈME EDUCATIONIA")
print("="*70)

# Test 1: Connexion MongoDB
print("\n1️⃣  TEST: Connexion MongoDB")
try:
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    print(f"   ✅ MongoDB connecté")
    print(f"   📊 Collections: {db.list_collection_names()}")
    
    # Compter les documents
    users_count = db.auth_user.count_documents({})
    tests_count = db.evaluation_test.count_documents({})
    print(f"   👥 Utilisateurs: {users_count}")
    print(f"   📝 Tests: {tests_count}")
except Exception as e:
    print(f"   ❌ Erreur MongoDB: {e}")

# Test 2: Authentification prof1
print("\n2️⃣  TEST: Authentification prof1")
try:
    user = authenticate(username='prof1', password='pass123')  # Mot de passe corrigé
    if user:
        print(f"   ✅ Authentification réussie: {user.username}")
        print(f"   👤 Nom complet: {user.get_full_name()}")
        print(f"   📧 Email: {user.email}")
        print(f"   🔑 Staff: {user.is_staff}")
        
        # Vérifier le profil
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"   👔 Rôle: {profile.role}")
        except:
            print(f"   ⚠️  Pas de profil UserProfile")
    else:
        print(f"   ❌ Authentification échouée")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 3: Authentification etudiant1
print("\n3️⃣  TEST: Authentification etudiant1")
try:
    user = authenticate(username='etudiant1', password='password123')
    if user:
        print(f"   ✅ Authentification réussie: {user.username}")
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"   🎓 Rôle: {profile.role}")
            print(f"   ⭐ XP: {profile.total_xp}")
            print(f"   🏆 Niveau: {profile.level}")
        except:
            print(f"   ⚠️  Pas de profil UserProfile")
    else:
        print(f"   ❌ Authentification échouée")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 4: Liste des tests
print("\n4️⃣  TEST: Liste des tests disponibles")
try:
    tests = Test.objects.all()[:5]
    print(f"   📊 Total de tests: {Test.objects.count()}")
    for test in tests:
        source_badge = "🤖 IA" if test.source_type == 'ai_generated' else "👔 Manuel"
        print(f"   {source_badge} {test.title} - {test.subject}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 5: Vérifier les badges source_type
print("\n5️⃣  TEST: Vérification des badges (source_type)")
try:
    manual_tests = Test.objects.filter(source_type='manual').count()
    ai_tests = Test.objects.filter(source_type='ai_generated').count()
    print(f"   👔 Tests manuels: {manual_tests}")
    print(f"   🤖 Tests IA: {ai_tests}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "="*70)
print("✅ TESTS TERMINÉS")
print("="*70)

# Fermer MongoDB
client.close()
