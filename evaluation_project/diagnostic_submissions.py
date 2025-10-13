#!/usr/bin/env python
"""
Script de diagnostic des soumissions d'exercices
Vérifie pourquoi le comptage des soumissions affiche 0
"""

import os
import sys
import django

# Configuration Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EducationIA.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings
from django.contrib.auth.models import User

def diagnostic_submissions():
    print("=== DIAGNOSTIC DES SOUMISSIONS ===\n")
    
    # Connexion MongoDB
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # 1. Vérifier le set spécifique mentionné
    specific_set_id = "68ed2c283ed41b6a86837e9b"
    print(f"🎯 Analyse du set spécifique: {specific_set_id}")
    
    try:
        from bson.objectid import ObjectId
        set_data = db.exercise_sets.find_one({'_id': ObjectId(specific_set_id)})
        
        if set_data:
            print(f"✅ Set trouvé: {set_data.get('title', 'Sans titre')}")
            print(f"   Status: {set_data.get('status', 'N/A')}")
            print(f"   Teacher ID: {set_data.get('teacher_id')} (type: {type(set_data.get('teacher_id'))})")
            
            # Compter exercices dans ce set
            exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
                'exerciseset_id': specific_set_id
            })
            print(f"   Exercices dans le set: {exercise_count}")
            
            # Compter soumissions pour ce set (deux méthodes)
            submissions_count_with_pk = db.student_exercise_submissions.count_documents({
                'exercise_set_id': ObjectId(specific_set_id)
            })
            submissions_count_with_str = db.student_exercise_submissions.count_documents({
                'exercise_set_id': specific_set_id
            })
            print(f"   Soumissions (ObjectId): {submissions_count_with_pk}")
            print(f"   Soumissions (String): {submissions_count_with_str}")
            
        else:
            print(f"❌ Set {specific_set_id} non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
    
    print()
    
    # 2. Compter tous les ExerciseSets
    total_sets = db.exercise_sets.count_documents({})
    print(f"📦 Total ExerciseSets: {total_sets}")
    
    # 3. Compter toutes les soumissions
    total_submissions = db.student_exercise_submissions.count_documents({})
    print(f"📝 Total Soumissions: {total_submissions}\n")
    
    # 4. Examiner la structure des soumissions
    if total_submissions > 0:
        print("🔍 Structure des soumissions:")
        sample_submissions = list(db.student_exercise_submissions.find().limit(3))
        for i, sub in enumerate(sample_submissions, 1):
            print(f"  Soumission {i}:")
            print(f"    - student_id: {sub.get('student_id')} (type: {type(sub.get('student_id'))})")
            print(f"    - exercise_set_id: {sub.get('exercise_set_id')} (type: {type(sub.get('exercise_set_id'))})")
            print(f"    - score: {sub.get('score', 'N/A')}")
            print(f"    - status: {sub.get('status', 'N/A')}")
            print(f"    - submitted_at: {sub.get('submitted_at', 'N/A')}")
            print()
    
    # 5. Vérifier structure des relations exercices-sets
    print("🔗 Relations exercices-sets:")
    total_relations = db.exercise_generator_exerciseset_exercises.count_documents({})
    print(f"  Total relations: {total_relations}")
    
    if total_relations > 0:
        sample_relations = list(db.exercise_generator_exerciseset_exercises.find().limit(3))
        for i, rel in enumerate(sample_relations, 1):
            print(f"  Relation {i}:")
            print(f"    - exerciseset_id: {rel.get('exerciseset_id')} (type: {type(rel.get('exerciseset_id'))})")
            print(f"    - generatedexercise_id: {rel.get('generatedexercise_id')} (type: {type(rel.get('generatedexercise_id'))})")
    
    client.close()
    print("\n=== FIN DU DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnostic_submissions()
