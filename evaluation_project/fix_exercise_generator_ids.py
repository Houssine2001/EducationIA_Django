#!/usr/bin/env python
"""
Script pour corriger le problème d'ID dans les collections exercise_generator
Ajoute le champ 'id' mappé vers '_id' pour tous les documents
"""
import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient('localhost', 27017)
db = client['django_education']

# Collections de exercise_generator
collections = [
    'course_documents',
    'generated_exercises', 
    'generated_tests',
    'exercise_generation_configs',
    'exercise_sets',
    'student_exercise_submissions'
]

print("=" * 70)
print("🔧 CORRECTION DES IDs EXERCISE_GENERATOR")
print("=" * 70)

for collection_name in collections:
    collection = db[collection_name]
    
    # Vérifier si la collection existe
    count_total = collection.count_documents({})
    if count_total == 0:
        print(f"\n📁 Collection: {collection_name}")
        print(f"   ⚠️  Collection vide, ignorée")
        continue
    
    count = 0
    print(f"\n📁 Collection: {collection_name}")
    
    # Pour chaque document
    for doc in collection.find():
        _id = doc['_id']
        
        # Si _id est un ObjectId, convertir en int (hash)
        if isinstance(_id, ObjectId):
            # Utiliser les 8 derniers caractères hex comme int
            id_value = int(str(_id)[-8:], 16)
        else:
            id_value = _id
        
        # Mettre à jour seulement si différent
        if doc.get('id') != id_value:
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'id': id_value}}
            )
            count += 1
    
    print(f"   ✅ {count} documents corrigés")
    
    # Vérification
    sample = collection.find_one()
    if sample:
        print(f"   🔍 Exemple: _id={sample.get('_id')}, id={sample.get('id')}")

print("\n" + "=" * 70)
print("✅ CORRECTION TERMINÉE")
print("=" * 70)
