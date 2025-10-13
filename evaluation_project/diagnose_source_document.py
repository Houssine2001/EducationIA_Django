"""
Script pour diagnostiquer les exercices avec des source_document_id problématiques
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
from exercise_generator.models import GeneratedExercise, CourseDocument

def diagnose_source_document_issues():
    print("=== DIAGNOSTIC SOURCE DOCUMENT ID ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Chercher les exercices avec source_document_id vide ou None
    print("\n1. EXERCICES AVEC SOURCE_DOCUMENT_ID PROBLÉMATIQUE")
    
    problematic_exercises = list(db.generated_exercises.find({
        '$or': [
            {'source_document_id': None},
            {'source_document_id': ''},
            {'source_document_id': {'$exists': False}}
        ]
    }))
    
    print(f"Exercices avec source_document_id problématique: {len(problematic_exercises)}")
    
    for i, ex in enumerate(problematic_exercises[:5]):
        print(f"Exercice {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
        print(f"  - Source Document ID: {repr(ex.get('source_document_id', 'MISSING'))}")
        print(f"  - Status: {ex.get('status', 'N/A')}")
    
    # 2. Chercher les exercices avec source_document_id qui n'existe plus
    print(f"\n2. EXERCICES AVEC SOURCE_DOCUMENT_ID INEXISTANT")
    
    orphaned_exercises = []
    exercises_with_source = list(db.generated_exercises.find({
        'source_document_id': {'$ne': None, '$exists': True, '$ne': ''}
    }))
    
    for ex in exercises_with_source[:10]:  # Limiter à 10 pour le test
        source_id = ex.get('source_document_id')
        if source_id:
            source_exists = db.course_documents.find_one({'_id': source_id})
            if not source_exists:
                orphaned_exercises.append(ex)
    
    print(f"Exercices avec source_document_id inexistant (échantillon): {len(orphaned_exercises)}")
    
    for i, ex in enumerate(orphaned_exercises[:3]):
        print(f"Exercice orphelin {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
        print(f"  - Source Document ID manquant: {ex.get('source_document_id')}")
    
    # 3. Statistiques générales
    print(f"\n3. STATISTIQUES GÉNÉRALES")
    total_exercises = db.generated_exercises.count_documents({})
    exercises_with_valid_source = 0
    
    # Compter les exercices avec source valide
    for doc in db.course_documents.find({}, {'_id': 1}):
        count = db.generated_exercises.count_documents({'source_document_id': doc['_id']})
        exercises_with_valid_source += count
    
    print(f"Total exercices: {total_exercises}")
    print(f"Exercices avec source valide: {exercises_with_valid_source}")
    print(f"Exercices potentiellement problématiques: {total_exercises - exercises_with_valid_source}")
    
    client.close()
    print(f"\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnose_source_document_issues()
