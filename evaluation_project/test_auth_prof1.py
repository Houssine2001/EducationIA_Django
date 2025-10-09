#!/usr/bin/env python
"""Test d'authentification approfondi pour prof1"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

print("=" * 70)
print("🔍 DIAGNOSTIC AUTHENTIFICATION PROF1")
print("=" * 70)

# 1. Vérifier que l'utilisateur existe
print("\n1️⃣  Recherche utilisateur prof1...")
try:
    user = User.objects.get(username='prof1')
    print(f"   ✅ Utilisateur trouvé: {user.username}")
    print(f"   📧 Email: {user.email}")
    print(f"   👤 Nom: {user.first_name} {user.last_name}")
    print(f"   🔑 Password hash: {user.password[:50]}...")
    print(f"   ✅ is_active: {user.is_active}")
    print(f"   ✅ is_staff: {user.is_staff}")
except User.DoesNotExist:
    print("   ❌ Utilisateur prof1 introuvable!")
    sys.exit(1)

# 2. Vérifier le hash du mot de passe
print("\n2️⃣  Vérification du mot de passe...")
passwords_to_test = ['Prof@2024', 'password123', 'pass123']

correct_password = None
for pwd in passwords_to_test:
    print(f"   🔐 Test avec: '{pwd}'")
    is_valid = user.check_password(pwd)
    print(f"   {'✅' if is_valid else '❌'} check_password result: {is_valid}")
    if is_valid:
        correct_password = pwd
        break

if not correct_password:
    print("\n   ❌ AUCUN mot de passe ne fonctionne!")
    sys.exit(1)

# 3. Tester authenticate()
print(f"\n3️⃣  Test de authenticate() avec '{correct_password}'...")
auth_user = authenticate(username='prof1', password=correct_password)
print(f"   Résultat: {auth_user}")
print(f"   Type: {type(auth_user)}")

if auth_user is None:
    print("   ❌ authenticate() retourne None!")
    print("\n🔍 CAUSES POSSIBLES:")
    print("   1. Backend d'authentification non configuré")
    print("   2. Signal causant une erreur silencieuse")
    print("   3. Middleware interceptant l'authentification")
    
    # Test direct du backend
    print("\n4️⃣  Test direct du backend...")
    from django.contrib.auth.backends import ModelBackend
    backend = ModelBackend()
    result = backend.authenticate(None, username='prof1', password=correct_password)
    print(f"   Backend result: {result}")
    
else:
    print(f"   ✅ Authentification réussie: {auth_user.username}")

# 5. Vérifier les backends configurés
print("\n5️⃣  Backends d'authentification configurés:")
from django.conf import settings
for backend in settings.AUTHENTICATION_BACKENDS:
    print(f"   - {backend}")

print("\n" + "=" * 70)
