"""
Script pour tester la validation d'exercice et vérifier le compteur
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
from datetime import datetime

def test_exercise_validation():
    print("=== TEST VALIDATION EXERCICE ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    user_id = 32  # prof1
    
    # 1. Trouver un exercice draft pour le tester
    print("1. RECHERCHE D'UN EXERCICE DRAFT")
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]
    
    draft_exercise = db.generated_exercises.find_one({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'draft'
    })
    
    if not draft_exercise:
        print("❌ Aucun exercice draft trouvé")
        client.close()
        return
    
    exercise_id = draft_exercise['_id']
    print(f"✅ Exercice draft trouvé: {exercise_id}")
    print(f"   Question: {draft_exercise.get('question_text', 'N/A')[:50]}...")
    print(f"   Status actuel: {draft_exercise.get('status')}")
    
    # 2. Compter avant validation
    print(f"\n2. COMPTEUR AVANT VALIDATION")
    validated_before = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'validated'
    })
    print(f"Exercices validés avant: {validated_before}")
    
    # 3. Simuler la validation avec PyMongo directement
    print(f"\n3. VALIDATION DE L'EXERCICE")
    update_result = db.generated_exercises.update_one(
        {'_id': exercise_id},
        {
            '$set': {
                'status': 'validated',
                'validated_by_id': user_id,
                'validation_notes': 'Test de validation',
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    if update_result.modified_count > 0:
        print(f"✅ Exercice {exercise_id} validé avec succès")
    else:
        print(f"❌ Échec de la validation")
    
    # 4. Compter après validation
    print(f"\n4. COMPTEUR APRÈS VALIDATION")
    validated_after = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'validated'
    })
    print(f"Exercices validés après: {validated_after}")
    print(f"Différence: +{validated_after - validated_before}")
    
    # 5. Vérifier l'exercice modifié
    print(f"\n5. VÉRIFICATION DE L'EXERCICE MODIFIÉ")
    updated_exercise = db.generated_exercises.find_one({'_id': exercise_id})
    if updated_exercise:
        print(f"Status: {updated_exercise.get('status')}")
        print(f"Validated by ID: {updated_exercise.get('validated_by_id')}")
        print(f"Validation notes: {updated_exercise.get('validation_notes')}")
        print(f"Updated at: {updated_exercise.get('updated_at')}")
    
    client.close()
    print(f"\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_exercise_validation()
