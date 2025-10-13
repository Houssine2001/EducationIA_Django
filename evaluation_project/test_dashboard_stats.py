"""
Script de test pour vérifier les corrections du dashboard
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings
from django.contrib.auth.models import User

def test_dashboard_stats():
    print("=== TEST DES STATISTIQUES DASHBOARD ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Simuler les calculs pour l'utilisateur prof1 (ID=32)
    user_id = 32
    
    # Récupérer les IDs des documents de l'enseignant
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]
    print(f"Documents du professeur {user_id}: {len(teacher_document_ids)}")
    
    # 1. Documents
    total_documents = db.course_documents.count_documents({'teacher_id': user_id})
    print(f"📄 Total Documents: {total_documents}")
    
    # 2. Exercices
    total_exercises = db.generated_exercises.count_documents({'source_document_id': {'$in': teacher_document_ids}})
    print(f"💪 Total Exercices: {total_exercises}")
    
    # 3. Tests (anciennement) = Exercices publiés + Exercise Sets publiés
    published_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'published'
    })
    published_exercise_sets = db.exercise_sets.count_documents({
        'teacher_id': {'$in': [user_id, str(user_id)]},
        'status': 'published'
    })
    total_tests = published_exercises + published_exercise_sets
    print(f"🧪 Tests (Publiés + Sets): {total_tests}")
    print(f"   - Exercices publiés: {published_exercises}")
    print(f"   - Exercise Sets publiés: {published_exercise_sets}")
    
    # 4. Validés = Seulement les exercices avec status='validated' 
    validated_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'validated'
    })
    print(f"✅ Exercices Validés (seulement 'validated'): {validated_exercises}")
    
    # Détail par statut
    print(f"\n📊 DÉTAIL PAR STATUT:")
    for status in ['draft', 'validated', 'published', 'rejected']:
        count = db.generated_exercises.count_documents({
            'source_document_id': {'$in': teacher_document_ids},
            'status': status
        })
        print(f"   - {status}: {count}")
    
    # Exercise Sets par statut
    print(f"\n📋 EXERCISE SETS PAR STATUT:")
    for status in ['draft', 'published']:
        count = db.exercise_sets.count_documents({
            'teacher_id': {'$in': [user_id, str(user_id)]},
            'status': status
        })
        print(f"   - Sets {status}: {count}")
    
    client.close()
    print(f"\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_dashboard_stats()
