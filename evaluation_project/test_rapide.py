# -*- coding: utf-8 -*-
"""
Script de test simple sans emojis pour eviter les problemes d'encodage
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 70)
print("TEST RAPIDE DU PROJET")
print("=" * 70)

client = Client()

# Test 1: Login page
print("\n1. Test page login...")
response = client.get('/accounts/login/')
print(f"   Status: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

# Test 2: Login etudiant
print("\n2. Test login etudiant1...")
success = client.login(username='etudiant1', password='pass123')
print(f"   Login: {'OK' if success else 'ERREUR'}")

# Test 3: Dashboard etudiant  
print("\n3. Test dashboard etudiant...")
response = client.get('/')
print(f"   Status: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

# Test 4: Page progression
print("\n4. Test page progression...")
response = client.get('/progress/')
print(f"   Status: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

client.logout()

# Test 5: Login professeur
print("\n5. Test login professeur...")
success = client.login(username='prof1', password='pass123')
print(f"   Login: {'OK' if success else 'ERREUR'}")

# Test 6: Dashboard professeur
print("\n6. Test dashboard professeur...")
response = client.get('/teacher/')
print(f"   Status: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

print("\n" + "=" * 70)
print("TESTS TERMINES")
print("=" * 70)
