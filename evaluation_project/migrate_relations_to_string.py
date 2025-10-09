"""
Migration: Convertir toutes les relations ManyToMany de ObjectId vers String
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['django_education']

print("=== MIGRATION DES RELATIONS MANYTOMANY ===\n")

# 1. Récupérer toutes les relations
all_relations = list(db.exercise_generator_exerciseset_exercises.find())
print(f"Total relations trouvées: {len(all_relations)}")

if not all_relations:
    print("❌ Aucune relation à migrer")
    client.close()
    exit()

# 2. Analyser les types
objectid_count = 0
string_count = 0
mixed_count = 0

for rel in all_relations:
    set_id = rel.get('exerciseset_id')
    ex_id = rel.get('generatedexercise_id')
    
    set_is_obj = isinstance(set_id, ObjectId)
    ex_is_obj = isinstance(ex_id, ObjectId)
    
    if set_is_obj and ex_is_obj:
        objectid_count += 1
    elif not set_is_obj and not ex_is_obj:
        string_count += 1
    else:
        mixed_count += 1

print(f"\nAnalyse:")
print(f"  - Tout en ObjectId: {objectid_count}")
print(f"  - Tout en String: {string_count}")
print(f"  - Mixte: {mixed_count}")

# 3. Migrer les ObjectId vers String
if objectid_count > 0 or mixed_count > 0:
    print(f"\n🔄 Migration de {objectid_count + mixed_count} relations...")
    
    migrated = 0
    for rel in all_relations:
        set_id = rel.get('exerciseset_id')
        ex_id = rel.get('generatedexercise_id')
        
        # Vérifier si besoin de migration
        needs_update = isinstance(set_id, ObjectId) or isinstance(ex_id, ObjectId)
        
        if needs_update:
            # Convertir en string
            new_data = {
                'exerciseset_id': str(set_id),
                'generatedexercise_id': str(ex_id)
            }
            
            # Mettre à jour
            db.exercise_generator_exerciseset_exercises.update_one(
                {'_id': rel['_id']},
                {'$set': new_data}
            )
            migrated += 1
    
    print(f"✅ {migrated} relations migrées vers String")
else:
    print("\n✅ Toutes les relations sont déjà en String format")

# 4. Vérifier le résultat
print("\n=== VÉRIFICATION POST-MIGRATION ===")
sets = list(db.exercise_sets.find({'status': 'published'}))

for s in sets:
    title = s.get('title', 'Sans titre')
    set_id = s['_id']
    
    # Compter avec string
    count = db.exercise_generator_exerciseset_exercises.count_documents({
        'exerciseset_id': str(set_id)
    })
    
    print(f"  {title}: {count} exercice(s)")

print("\n✅ Migration terminée!")
client.close()
