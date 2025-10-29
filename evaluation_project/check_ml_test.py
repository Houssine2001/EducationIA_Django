#!/usr/bin/env python
"""
Vérifier si le test Machine Learning avec 100% existe dans la base de données
"""

import os
import django
import sys

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import Result, Test
from pymongo import MongoClient
from django.conf import settings

print("\n" + "="*70)
print("🔍 VÉRIFICATION DU TEST MACHINE LEARNING")
print("="*70)

# Connexion MongoDB
client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client[settings.DATABASES['default']['NAME']]

# 1. Vérifier l'utilisateur
print("\n1️⃣ UTILISATEUR CONNECTÉ:")
print("-" * 70)
try:
    # Chercher l'utilisateur qui a passé le test récemment
    users = User.objects.filter(is_staff=False, is_active=True)
    print(f"   Nombre d'étudiants actifs: {users.count()}")
    
    for user in users[:5]:  # Afficher les 5 premiers
        print(f"   - {user.username} (ID: {user.id})")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 2. Vérifier les tests Machine Learning
print("\n2️⃣ TESTS MACHINE LEARNING:")
print("-" * 70)
try:
    ml_tests = Test.objects.filter(subject__icontains='machine learning')
    print(f"   Nombre de tests ML trouvés: {ml_tests.count()}")
    
    if ml_tests.exists():
        for test in ml_tests:
            print(f"\n   📝 Test: {test.title}")
            print(f"      ID: {test.id}")
            print(f"      Matière: {test.subject}")
            print(f"      Difficulté: {test.difficulty}")
            
            # Vérifier les résultats pour ce test
            results = Result.objects.filter(test=test)
            print(f"      Résultats enregistrés: {results.count()}")
            
            for result in results:
                print(f"         → Étudiant: {result.student.username}")
                print(f"            Score: {result.percentage_score}%")
                print(f"            Date: {result.completed_at}")
    else:
        print("   ⚠️ Aucun test Machine Learning trouvé")
        
        # Lister tous les tests disponibles
        all_tests = Test.objects.all()[:10]
        print(f"\n   📋 Tests disponibles (10 premiers):")
        for test in all_tests:
            print(f"      - {test.title} ({test.subject})")
            
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# 3. Vérifier tous les résultats avec 100%
print("\n3️⃣ RÉSULTATS À 100%:")
print("-" * 70)
try:
    perfect_results = Result.objects.filter(percentage_score=100).order_by('-completed_at')
    print(f"   Nombre de résultats parfaits: {perfect_results.count()}")
    
    if perfect_results.exists():
        for result in perfect_results[:5]:  # Afficher les 5 derniers
            print(f"\n   🏆 Score Parfait:")
            print(f"      Étudiant: {result.student.username}")
            print(f"      Test: {result.test.title}")
            print(f"      Matière: {result.test.subject}")
            print(f"      Score: {result.percentage_score}%")
            print(f"      Date: {result.completed_at}")
    else:
        print("   ⚠️ Aucun résultat à 100% trouvé")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# 4. Vérifier les résultats récents (tous scores)
print("\n4️⃣ RÉSULTATS RÉCENTS (TOUS SCORES):")
print("-" * 70)
try:
    recent_results = Result.objects.all().order_by('-completed_at')[:10]
    print(f"   Nombre total de résultats: {Result.objects.count()}")
    print(f"   10 derniers résultats:")
    
    for result in recent_results:
        print(f"\n   📊 Résultat:")
        print(f"      Étudiant: {result.student.username}")
        print(f"      Test: {result.test.title if hasattr(result, 'test') else 'N/A'}")
        print(f"      Score: {result.percentage_score}%")
        print(f"      Date: {result.completed_at if hasattr(result, 'completed_at') else 'N/A'}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# 5. Vérifier dans MongoDB directement
print("\n5️⃣ VÉRIFICATION MONGODB DIRECTE:")
print("-" * 70)
try:
    # Collection Result
    result_collection = db.evaluation_result
    total_results = result_collection.count_documents({})
    print(f"   Documents dans evaluation_result: {total_results}")
    
    # Résultats à 100%
    perfect_docs = list(result_collection.find({'percentage_score': 100}).limit(5))
    print(f"   Résultats à 100% (MongoDB): {len(perfect_docs)}")
    
    for doc in perfect_docs:
        print(f"\n   🏆 Document:")
        print(f"      ID: {doc.get('_id')}")
        print(f"      student_id: {doc.get('student_id')}")
        print(f"      test_id: {doc.get('test_id')}")
        print(f"      percentage_score: {doc.get('percentage_score')}")
        print(f"      completed_at: {doc.get('completed_at')}")
        
except Exception as e:
    print(f"   ❌ Erreur MongoDB: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ VÉRIFICATION TERMINÉE")
print("="*70 + "\n")
