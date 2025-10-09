"""
Debug: Vérifier le set Java et ses exercices
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

client = MongoClient('localhost', 27017)
db = client['django_education']

# Chercher les sets publiés qui contiennent "java" dans le titre
print("=== RECHERCHE SETS AVEC 'JAVA' ===")
sets = list(db.exercise_sets.find({
    'status': 'published',
    'title': {'$regex': 'java', '$options': 'i'}
}))

print(f"Trouvé {len(sets)} set(s)")

for i, s in enumerate(sets):
    print(f"\n--- SET #{i+1} ---")
    print(f"ID: {s['_id']}")
    print(f"Type ID: {type(s['_id'])}")
    print(f"Title: {s.get('title')}")
    print(f"Status: {s.get('status')}")
    
    set_id = s['_id']
    
    # Essayer de trouver les relations avec ObjectId
    print(f"\n🔍 Recherche relations avec ObjectId({set_id}):")
    relations_obj = list(db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': set_id
    }))
    print(f"   Résultat: {len(relations_obj)} relations")
    
    # Essayer avec string
    print(f"\n🔍 Recherche relations avec str('{set_id}'):")
    relations_str = list(db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': str(set_id)
    }))
    print(f"   Résultat: {len(relations_str)} relations")
    
    if relations_str:
        print("\n   Détails des relations:")
        for j, rel in enumerate(relations_str[:3]):
            print(f"   Relation {j+1}:")
            print(f"      exerciseset_id: {rel['exerciseset_id']} (type: {type(rel['exerciseset_id']).__name__})")
            print(f"      generatedexercise_id: {rel['generatedexercise_id']} (type: {type(rel['generatedexercise_id']).__name__})")
        
        # Récupérer les exercices
        exercise_ids = [rel['generatedexercise_id'] for rel in relations_str]
        print(f"\n   IDs des exercices: {exercise_ids}")
        
        # Convertir en ObjectId pour requête
        exercise_oids = [ObjectId(eid) if isinstance(eid, str) else eid for eid in exercise_ids]
        exercises = list(db.generated_exercises.find({
            '_id': {'$in': exercise_oids}
        }))
        print(f"\n   ✅ Exercices trouvés: {len(exercises)}")
        
        for k, ex in enumerate(exercises):
            print(f"      Exercice {k+1}: {ex.get('question_text', 'N/A')[:60]}...")

client.close()
