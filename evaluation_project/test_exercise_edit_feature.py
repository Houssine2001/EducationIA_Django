"""
Script pour tester la nouvelle fonctionnalité d'édition d'exercices
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

def test_exercise_edit_feature():
    print("=== TEST FONCTIONNALITÉ ÉDITION EXERCICE ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    user_id = 32  # prof1
    
    # 1. Trouver un exercice à éditer
    print("1. RECHERCHE D'EXERCICES À ÉDITER")
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]
    
    exercises = list(db.generated_exercises.find({
        'source_document_id': {'$in': teacher_document_ids}
    }).limit(3))
    
    print(f"Exercices trouvés: {len(exercises)}")
    
    for i, exercise in enumerate(exercises):
        print(f"\nExercice {i+1}:")
        print(f"  - ID: {exercise['_id']}")
        print(f"  - Type: {exercise.get('exercise_type', 'N/A')}")
        print(f"  - Question: {exercise.get('question_text', 'N/A')[:50]}...")
        print(f"  - Status: {exercise.get('status', 'N/A')}")
        print(f"  - URL d'édition: http://127.0.0.1:8000/generator/exercises/{exercise['_id']}/edit/")
        
        # Afficher les options selon le type
        options_data = exercise.get('options_data', {})
        if exercise.get('exercise_type') == 'mcq':
            print(f"  - Options: {options_data.get('options', [])}")
            print(f"  - Correct: {options_data.get('correct', 'N/A')}")
        elif exercise.get('exercise_type') == 'true_false':
            print(f"  - Correct: {options_data.get('correct', 'N/A')}")
        elif exercise.get('exercise_type') == 'fill_blank':
            print(f"  - Texte: {options_data.get('text', 'N/A')[:30]}...")
            print(f"  - Correct: {options_data.get('correct', 'N/A')}")
    
    # 2. Compter par type d'exercice
    print(f"\n2. RÉPARTITION PAR TYPE")
    types = ['mcq', 'true_false', 'fill_blank']
    for exercise_type in types:
        count = db.generated_exercises.count_documents({
            'source_document_id': {'$in': teacher_document_ids},
            'exercise_type': exercise_type
        })
        print(f"  - {exercise_type}: {count}")
    
    # 3. URLs importantes
    print(f"\n3. URLS IMPORTANTES")
    print(f"  - Dashboard: http://127.0.0.1:8000/generator/")
    print(f"  - Liste exercices: http://127.0.0.1:8000/generator/exercises/")
    if exercises:
        exercise_id = exercises[0]['_id']
        print(f"  - Détail exercice: http://127.0.0.1:8000/generator/exercises/{exercise_id}/")
        print(f"  - Éditer exercice: http://127.0.0.1:8000/generator/exercises/{exercise_id}/edit/")
    
    client.close()
    print(f"\n=== FONCTIONNALITÉ PRÊTE À TESTER ===")

if __name__ == "__main__":
    test_exercise_edit_feature()
