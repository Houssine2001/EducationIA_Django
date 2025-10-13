"""
Script de test pour vérifier les corrections de l'exercice detail
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
from exercise_generator.models import GeneratedExercise, CourseDocument

def test_exercise_fix():
    print("=== TEST DES CORRECTIONS EXERCICE ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Vérifier quelques exercices avec leur source_document_id
    print("\n1. VÉRIFICATION DES EXERCICES ET LEURS DOCUMENTS SOURCE")
    exercises = list(db.generated_exercises.find().limit(3))
    
    for i, ex in enumerate(exercises):
        print(f"\nExercice {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
        print(f"  - Source Document ID: {ex.get('source_document_id', 'N/A')}")
        
        # Vérifier si le document source existe
        source_doc_id = ex.get('source_document_id')
        if source_doc_id:
            source_doc = db.course_documents.find_one({'_id': source_doc_id})
            if source_doc:
                print(f"  - Document Source trouvé: {source_doc.get('title', 'N/A')}")
            else:
                print(f"  - ⚠️ Document Source INTROUVABLE dans MongoDB")
        else:
            print(f"  - ⚠️ Pas de source_document_id")
    
    # 2. Compter les exercices avec/sans document source
    print(f"\n2. STATISTIQUES")
    total_exercises = db.generated_exercises.count_documents({})
    exercises_with_source = db.generated_exercises.count_documents({
        'source_document_id': {'$ne': None, '$exists': True}
    })
    exercises_without_source = total_exercises - exercises_with_source
    
    print(f"Total exercices: {total_exercises}")
    print(f"Avec source document: {exercises_with_source}")
    print(f"Sans source document: {exercises_without_source}")
    
    # 3. Vérifier les utilisateurs
    print(f"\n3. UTILISATEURS DISPONIBLES")
    users = User.objects.all()[:3]
    for user in users:
        print(f"User {user.id}: {user.username}")
        # Compter ses documents
        user_docs = db.course_documents.count_documents({'teacher_id': user.id})
        print(f"  - Documents: {user_docs}")
    
    client.close()
    print(f"\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_exercise_fix()
