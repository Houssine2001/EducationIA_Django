"""
Script de diagnostic pour comprendre pourquoi les exercices ne s'affichent pas 
dans le dashboard et la liste des sets
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
from exercise_generator.models import GeneratedExercise, CourseDocument, ExerciseSet

def main():
    print("=== DIAGNOSTIC AFFICHAGE EXERCICES ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Vérifier les exercices récents
    print("\n1. EXERCICES RÉCENTS (MongoDB)")
    recent_exercises = list(db.generated_exercises.find().sort('created_at', -1).limit(5))
    print(f"Nombre d'exercices: {len(recent_exercises)}")
    
    for i, ex in enumerate(recent_exercises[:3]):
        print(f"Exercice {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Question: {ex.get('question', 'N/A')[:50]}...")
        print(f"  - Source Document ID: {ex.get('source_document_id', 'N/A')}")
        print(f"  - Status: {ex.get('status', 'N/A')}")
        print(f"  - Created: {ex.get('created_at', 'N/A')}")
    
    # 2. Vérifier via Django ORM
    print("\n2. EXERCICES VIA DJANGO ORM")
    try:
        django_exercises = GeneratedExercise.objects.all()[:3]
        print(f"Django ORM trouve: {django_exercises.count()} exercices")
        
        for ex in django_exercises:
            print(f"  - ID: {ex.pk}")
            print(f"  - Question: {ex.question[:50]}...")
    except Exception as e:
        print(f"Erreur Django ORM: {e}")
    
    # 3. Vérifier les documents de cours
    print("\n3. DOCUMENTS DE COURS")
    docs = list(db.course_documents.find().sort('created_at', -1).limit(3))
    print(f"Nombre de documents: {len(docs)}")
    
    for i, doc in enumerate(docs):
        print(f"Document {i+1}:")
        print(f"  - ID: {doc['_id']}")
        print(f"  - Title: {doc.get('title', 'N/A')}")
        print(f"  - Teacher ID: {doc.get('teacher_id', 'N/A')}")
        print(f"  - Status: {doc.get('processing_status', 'N/A')}")
    
    # 4. Vérifier les ExerciseSets
    print("\n4. EXERCISE SETS")
    sets = list(db.exercise_sets.find().sort('created_at', -1).limit(3))
    print(f"Nombre de sets: {len(sets)}")
    
    for i, ex_set in enumerate(sets):
        print(f"Set {i+1}:")
        print(f"  - ID: {ex_set['_id']}")
        print(f"  - Title: {ex_set.get('title', 'N/A')}")
        print(f"  - Teacher ID: {ex_set.get('teacher_id', 'N/A')}")
        print(f"  - Status: {ex_set.get('status', 'N/A')}")
    
    # 5. Vérifier les relations ManyToMany
    print("\n5. RELATIONS MANYTOMANY")
    relations = list(db.exercise_generator_exerciseset_exercises.find().limit(5))
    print(f"Nombre de relations: {len(relations)}")
    
    for i, rel in enumerate(relations):
        print(f"Relation {i+1}:")
        print(f"  - ExerciseSet ID: {rel.get('exerciseset_id')} (type: {type(rel.get('exerciseset_id'))})")
        print(f"  - Exercise ID: {rel.get('generatedexercise_id')} (type: {type(rel.get('generatedexercise_id'))})")
    
    # 6. Vérifier les utilisateurs
    print("\n6. UTILISATEURS")
    users = User.objects.all()[:3]
    for user in users:
        print(f"User {user.id}: {user.username} ({user.email})")
        
        # Compter ses documents via MongoDB
        user_docs = db.course_documents.count_documents({'teacher_id': user.id})
        user_exercises = db.generated_exercises.count_documents({'source_document_id': {'$in': [doc['_id'] for doc in db.course_documents.find({'teacher_id': user.id})]}})
        user_sets = db.exercise_sets.count_documents({'teacher_id': user.id})
        
        print(f"  - Documents: {user_docs}")
        print(f"  - Exercices: {user_exercises}")
        print(f"  - Sets: {user_sets}")
    
    client.close()
    print("\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    main()
