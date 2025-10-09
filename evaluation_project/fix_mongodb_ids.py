#!/usr/bin/env python
"""
Script pour corriger le problème d'ID dans MongoDB
Ajoute le champ 'id' mappé vers '_id' pour tous les documents
"""
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client['django_education']

collections = [
    'auth_user',
    'evaluation_userprofile',
    'evaluation_test',
    'evaluation_question',
    'evaluation_submission',
    'evaluation_result'
]

print("=" * 70)
print("🔧 CORRECTION DES IDs MONGODB")
print("=" * 70)

for collection_name in collections:
    collection = db[collection_name]
    count = 0
    
    print(f"\n📁 Collection: {collection_name}")
    
    # Pour chaque document, copier _id vers id
    for doc in collection.find():
        if 'id' != doc.get('id'):
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'id': doc['_id']}}
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
