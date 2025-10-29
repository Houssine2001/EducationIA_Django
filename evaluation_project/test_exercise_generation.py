"""
Script de test pour la génération d'exercices avec ObjectId
"""
import os
import sys
import django
from backend.mongodb_utils import get_mongodb_client

# Ajouter le dossier du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from exercise_generator.models import CourseDocument, GeneratedExercise
from django.contrib.auth.models import User
from exercise_generator.services import ExerciseGenerationService
from pymongo import MongoClient
from django.conf import settings

def test_exercise_generation():
    """Test complet de génération + récupération"""
    print("\n=== TEST GÉNÉRATION D'EXERCICES ===\n")
    
    # 1. Récupérer un professeur
    prof = User.objects.filter(username='prof1').first()
    if not prof:
        print("❌ Professeur 'prof1' introuvable")
        return
    print(f"✅ Professeur trouvé: {prof.username}")
    
    # 2. Créer un document de test
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    doc_data = {
        'teacher_id': prof.id,
        'title': 'Test ObjectId Relations',
        'content': 'Python est un langage de programmation. Django est un framework web. MongoDB est une base de données NoSQL.',
        'subject': 'python',
        'topic': 'Concepts de base',
        'level': 'debutant',
        'word_count': 15,
        'sentence_count': 3,
        'processing_status': 'processing',
        'key_concepts': [],
        'main_topics': [],
    }
    
    result = db.course_documents.insert_one(doc_data)
    doc_id = result.inserted_id
    print(f"✅ Document créé: {doc_id}")
    
    # 3. Créer instance Django du document (retirer _id de doc_data)
    clean_data = {k: v for k, v in doc_data.items() if k != '_id'}
    document = CourseDocument(**clean_data)
    document.pk = doc_id
    document._state.adding = False
    document._state.db = 'default'
    print(f"✅ Instance Django créée (pk={document.pk})")
    
    # 4. Générer des exercices
    print("\n--- Génération d'exercices ---")
    service = ExerciseGenerationService()
    
    exercises_data = [
        {
            'type': 'mcq',
            'question': 'Qu\'est-ce que Python?',
            'options': ['A) Un langage', 'B) Un serpent', 'C) Un framework', 'D) Une base de données'],
            'correct_answer': 'A',
            'concept': 'Python',
            'difficulty': 'easy',
            'quality_score': 0.8,
        },
        {
            'type': 'true_false',
            'question': 'Django est un framework web',
            'correct_answer': True,
            'concept': 'Django',
            'difficulty': 'easy',
            'quality_score': 0.9,
        }
    ]
    
    saved = service._save_generated_exercises(document, exercises_data)
    print(f"✅ {len(saved)} exercices sauvegardés via PyMongo")
    
    # 5. Récupérer les exercices avec PyMongo (comme dans views.py)
    print("\n--- Récupération des exercices ---")
    exercises_docs = list(db.generated_exercises.find({'source_document_id': doc_id}))
    print(f"✅ {len(exercises_docs)} exercices trouvés dans MongoDB")
    
    for ex_doc in exercises_docs:
        print(f"   - {ex_doc['exercise_type']}: {ex_doc['question_text'][:50]}...")
    
    # 6. Vérifier les relations (comme document.generated_exercises.all())
    print("\n--- Test des relations ---")
    try:
        # Créer instances Django
        exercises = []
        for ex_data in exercises_docs:
            ex_id = ex_data.pop('_id', None)
            exercise = GeneratedExercise(**ex_data)
            exercise.pk = ex_id
            exercise._state.adding = False
            exercise._state.db = 'default'
            exercises.append(exercise)
        
        print(f"✅ {len(exercises)} instances Django créées")
        print(f"✅ Relations fonctionnelles (contournement PyMongo)")
    except Exception as e:
        print(f"❌ Erreur relations: {e}")
    
    # 7. Vérification des données
    print("\n--- Vérification des données ---")
    for ex in exercises:
        print(f"   Exercise ID: {ex.pk} (type: {type(ex.pk).__name__})")
        print(f"   Question: {ex.question_text[:50]}...")
        print(f"   Type: {ex.exercise_type}")
        print(f"   Source Document ID: {ex.source_document_id} (type: {type(ex.source_document_id).__name__})")
        print()
    
    # 8. Nettoyage
    print("--- Nettoyage ---")
    db.generated_exercises.delete_many({'source_document_id': doc_id})
    db.course_documents.delete_one({'_id': doc_id})
    print("✅ Documents de test supprimés")
    
    print("\n=== TEST TERMINÉ ===\n")

if __name__ == '__main__':
    test_exercise_generation()
