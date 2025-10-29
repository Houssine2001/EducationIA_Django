#!/usr/bin/env python
"""
Vérifier les détails des tests avec 100% et l'utilisateur correspondant
"""

import os
import django
import sys

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import Result, Test, UserProfile
from pymongo import MongoClient
from django.conf import settings

print("\n" + "="*70)
print("🔍 DÉTAILS DES RÉSULTATS À 100%")
print("="*70)

# Connexion MongoDB
client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client[settings.DATABASES['default']['NAME']]

# Récupérer les résultats à 100% depuis MongoDB
print("\n1️⃣ RÉSULTATS À 100% (MongoDB):")
print("-" * 70)
perfect_docs = list(db.evaluation_result.find({'percentage_score': 100}))
print(f"   Nombre de résultats à 100%: {len(perfect_docs)}")

for doc in perfect_docs:
    print(f"\n   🏆 Résultat ID: {doc.get('id')}")
    
    # Récupérer l'étudiant
    student_id = doc.get('student_id')
    try:
        student = User.objects.get(id=student_id)
        print(f"      Étudiant: {student.username} (ID: {student.id})")
        print(f"      Email: {student.email}")
    except User.DoesNotExist:
        print(f"      ❌ Étudiant ID {student_id} introuvable")
    
    # Récupérer le test
    test_id = doc.get('test_id')
    try:
        test = Test.objects.get(id=test_id)
        print(f"      📝 Test: {test.title}")
        print(f"         Matière: {test.subject}")
        print(f"         Difficulté: {test.difficulty}")
        print(f"         ID: {test.id}")
    except Test.DoesNotExist:
        print(f"      ❌ Test ID {test_id} introuvable")
    
    print(f"      Score: {doc.get('percentage_score')}%")
    print(f"      Date: {doc.get('created_at')}")

# Vérifier le profil de l'étudiant
print("\n2️⃣ PROFIL ÉTUDIANT:")
print("-" * 70)
if perfect_docs:
    student_id = perfect_docs[0].get('student_id')
    try:
        student = User.objects.get(id=student_id)
        print(f"   Étudiant: {student.username}")
        
        # Profil
        try:
            profile = UserProfile.objects.get(user=student)
            print(f"   Profil trouvé:")
            print(f"      Level: {profile.level}")
            print(f"      Total XP: {profile.total_xp}")
            print(f"      Badges: {len(profile.badges) if profile.badges else 0}")
            if profile.badges:
                for badge in profile.badges:
                    print(f"         - {badge.get('name')} ({badge.get('earned_at')})")
        except UserProfile.DoesNotExist:
            print(f"   ❌ Profil introuvable")
            
    except User.DoesNotExist:
        print(f"   ❌ Étudiant ID {student_id} introuvable")

# Vérifier TOUS les résultats de cet étudiant
print("\n3️⃣ TOUS LES RÉSULTATS DE L'ÉTUDIANT:")
print("-" * 70)
if perfect_docs:
    student_id = perfect_docs[0].get('student_id')
    all_results = list(db.evaluation_result.find({'student_id': student_id}).sort('created_at', -1))
    print(f"   Nombre total de résultats: {len(all_results)}")
    
    for doc in all_results[:10]:  # Afficher les 10 derniers
        test_id = doc.get('test_id')
        try:
            test = Test.objects.get(id=test_id)
            test_name = test.title
            test_subject = test.subject
        except:
            test_name = f"Test ID {test_id}"
            test_subject = "N/A"
        
        print(f"\n      📊 {test_name}")
        print(f"         Matière: {test_subject}")
        print(f"         Score: {doc.get('percentage_score')}%")
        print(f"         Date: {doc.get('created_at')}")

print("\n" + "="*70)
print("✅ VÉRIFICATION TERMINÉE")
print("="*70 + "\n")
