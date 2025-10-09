"""
Vérifier la structure de la table ManyToMany exercise_generator_exerciseset_exercises
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

client = MongoClient('localhost', 27017)
db = client['django_education']

# Récupérer un ExerciseSet publié
exercise_set = db.exercise_sets.find_one({'status': 'published'})

if exercise_set:
    print("=== EXERCISE SET ===")
    print(f"ID: {exercise_set['_id']}")
    print(f"Type: {type(exercise_set['_id'])}")
    print(f"Title: {exercise_set.get('title')}")
    print(f"Status: {exercise_set.get('status')}")
    
    # Chercher les relations dans la table ManyToMany
    print("\n=== RECHERCHE RELATIONS (avec ObjectId) ===")
    relations = list(db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': exercise_set['_id']
    }))
    print(f"Trouvé {len(relations)} relations avec ObjectId")
    
    if relations:
        print("\nPremière relation:")
        print(json.dumps({k: str(v) if isinstance(v, ObjectId) else v for k, v in relations[0].items()}, indent=2))
    
    # Essayer aussi avec string
    print("\n=== RECHERCHE RELATIONS (avec string) ===")
    relations_str = list(db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': str(exercise_set['_id'])
    }))
    print(f"Trouvé {len(relations_str)} relations avec string")
    
    # Lister toutes les relations pour voir la structure
    print("\n=== TOUTES LES RELATIONS ===")
    all_relations = list(db.exercise_generator_exerciseset_exercises.find().limit(3))
    for i, rel in enumerate(all_relations):
        print(f"\nRelation #{i+1}:")
        print(f"  exerciseset_id: {rel.get('exerciseset_id')} (type: {type(rel.get('exerciseset_id'))})")
        print(f"  generatedexercise_id: {rel.get('generatedexercise_id')} (type: {type(rel.get('generatedexercise_id'))})")
else:
    print("❌ Aucun ExerciseSet publié trouvé")

client.close()
