"""
Script MongoDB pur pour ajouter des IDs aux resources
Alternative si la commande Django ne fonctionne pas
"""
from pymongo import MongoClient

# Configuration MongoDB
MONGO_HOST = 'mongodb'  # ou 'localhost' en local
MONGO_PORT = 27017
MONGO_DB_NAME = 'education_ia'

# Connexion
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB_NAME]
collection = db.resources_resource

# Trouver les resources sans ID
resources_without_id = collection.find({'id': None})
count = collection.count_documents({'id': None})

print(f"🔍 {count} resources sans ID trouvées")

if count == 0:
    print("✅ Toutes les resources ont déjà un ID")
    exit(0)

# Trouver le max ID
max_id_doc = collection.find_one({'id': {'$ne': None}}, sort=[('id', -1)])
next_id = (max_id_doc['id'] + 1) if max_id_doc else 1

print(f"📝 Attribution d'IDs à partir de {next_id}")

# Mettre à jour chaque resource
fixed = 0
for resource in resources_without_id:
    try:
        result = collection.update_one(
            {'_id': resource['_id']},
            {'$set': {'id': next_id}}
        )
        
        if result.modified_count > 0:
            print(f"  ✓ '{resource['title']}' -> ID {next_id}")
            next_id += 1
            fixed += 1
        else:
            print(f"  ✗ Échec pour '{resource['title']}'")
    except Exception as e:
        print(f"  ✗ Erreur pour '{resource['title']}': {e}")

print(f"\n✅ {fixed}/{count} resources corrigées")

# Vérifier
remaining = collection.count_documents({'id': None})
print(f"📊 Resources restantes sans ID: {remaining}")

client.close()
