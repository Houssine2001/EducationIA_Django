#!/usr/bin/env python
"""Test rapide final du système après toutes les corrections"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from evaluation.models import UserProfile, Test

print("=" * 70)
print("TEST FINAL RAPIDE")
print("=" * 70)

# Test prof1
print("\n1. Prof1:")
user = authenticate(username='prof1', password='pass123')
if user:
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"   OK - ID:{user.id}, Role:{profile.role}")
    except:
        print(f"   ERREUR - Profile introuvable")
else:
    print(f"   ERREUR - Auth failed")

# Test etudiant1
print("\n2. Etudiant1:")
user = authenticate(username='etudiant1', password='password123')
if user:
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"   OK - ID:{user.id}, Role:{profile.role}, XP:{profile.total_xp}")
    except:
        print(f"   ERREUR - Profile introuvable")
else:
    print(f"   ERREUR - Auth failed")

# Test comptage
print("\n3. Tests:")
total = Test.objects.count()
manual = Test.objects.filter(source_type='manual').count()
ai = Test.objects.filter(source_type='ai_generated').count()
print(f"   Total:{total}, Manual:{manual}, IA:{ai}")

print("\n" + "=" * 70)
print("FIN")
print("=" * 70)
