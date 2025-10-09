from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['django_education']

# Chercher les sets publiés
sets = list(db.exercise_sets.find({'status': 'published'}).limit(5))
print(f"Sets publiés: {len(sets)}\n")

for s in sets:
    print(f"=== {s.get('title')} ===")
    print(f"ID: {s['_id']}")
    
    # Chercher relations avec string
    relations = list(db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': str(s['_id'])
    }))
    print(f"Relations: {len(relations)}")
    print()

client.close()
