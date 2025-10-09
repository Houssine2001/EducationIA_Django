#!/usr/bin/env python
"""
Test de login avec Django Test Client (pas besoin de serveur)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("=" * 70)
print("TEST DE LOGIN AVEC DJANGO TEST CLIENT")
print("=" * 70)

# Créer un client de test
client = Client()

# 1. Test d'accès à la page de login
print("\n1️⃣  Accès à la page de login...")
try:
    response = client.get('/evaluation/login/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Page de login accessible")
        
        # Vérifier que le CSRF est présent
        if 'csrfmiddlewaretoken' in str(response.content):
            print(f"   ✅ CSRF token présent dans le formulaire")
    else:
        print(f"   ❌ Erreur d'accès: {response.status_code}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 2. Test de login avec prof1
print("\n2️⃣  Test de login avec prof1...")
try:
    login_success = client.login(username='prof1', password='pass123')
    print(f"   {'✅' if login_success else '❌'} Login: {login_success}")
    
    if login_success:
        # Vérifier l'accès au dashboard
        print("\n3️⃣  Vérification de l'accès au dashboard...")
        response = client.get('/evaluation/dashboard/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Accès au dashboard réussi!")
            # Vérifier le contenu
            content = response.content.decode('utf-8')
            if 'Professeur' in content or 'Dashboard' in content:
                print(f"   ✅ Contenu du dashboard trouvé")
        elif response.status_code == 302:
            print(f"   ⚠️  Redirection: {response.url}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# 3. Test de login avec etudiant1
print("\n4️⃣  Test de login avec etudiant1...")
try:
    client2 = Client()
    login_success = client2.login(username='etudiant1', password='password123')
    print(f"   {'✅' if login_success else '❌'} Login: {login_success}")
    
    if login_success:
        response = client2.get('/evaluation/dashboard/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Accès au dashboard réussi!")
            
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 4. Test de la page d'accueil (sans login)
print("\n5️⃣  Test de la page d'accueil (sans login)...")
try:
    client3 = Client()
    response = client3.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Page d'accueil accessible")
    elif response.status_code == 302:
        print(f"   ⚠️  Redirection vers: {response.url}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 70)
print("FIN DES TESTS")
print("=" * 70)
