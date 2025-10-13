"""
Script pour créer des exercices validés et publiés pour tester les statistiques
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
from bson.objectid import ObjectId

def create_test_validation_data():
    print("=== CRÉATION DE DONNÉES DE VALIDATION TEST ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    user_id = 32  # prof1
    
    # 1. Valider quelques exercices
    print("1. VALIDATION D'EXERCICES")
    draft_exercises = list(db.generated_exercises.find({
        'source_document_id': {'$in': [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]},
        'status': 'draft'
    }).limit(5))
    
    if len(draft_exercises) >= 3:
        # Valider 3 exercices
        for i in range(3):
            exercise_id = draft_exercises[i]['_id']
            db.generated_exercises.update_one(
                {'_id': exercise_id},
                {'$set': {'status': 'validated'}}
            )
            print(f"   ✅ Exercice {exercise_id} → validated")
        
        # Publier 2 exercices
        for i in range(2):
            exercise_id = draft_exercises[i]['_id']
            db.generated_exercises.update_one(
                {'_id': exercise_id},
                {'$set': {'status': 'published'}}
            )
            print(f"   📢 Exercice {exercise_id} → published")
    
    # 2. Vérification finale
    print(f"\n2. VÉRIFICATION FINALE")
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]
    
    total_exercises = db.generated_exercises.count_documents({'source_document_id': {'$in': teacher_document_ids}})
    validated_count = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': {'$in': ['validated', 'published']}
    })
    published_count = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'published'
    })
    published_sets = db.exercise_sets.count_documents({
        'teacher_id': {'$in': [user_id, str(user_id)]},
        'status': 'published'
    })
    
    total_tests = published_count + published_sets
    
    print(f"📊 NOUVELLES STATISTIQUES:")
    print(f"   - Total Exercices: {total_exercises}")
    print(f"   - Validés (validés + publiés): {validated_count}")
    print(f"   - Tests (publiés + sets): {total_tests}")
    print(f"     * Exercices publiés: {published_count}")
    print(f"     * Exercise Sets publiés: {published_sets}")
    
    client.close()
    print(f"\n=== DONNÉES DE TEST CRÉÉES ===")

if __name__ == "__main__":
    create_test_validation_data()
