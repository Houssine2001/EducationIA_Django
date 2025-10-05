"""
Script pour supprimer l'index problématique de student_id
"""
import pymongo

# Connexion à MongoDB
client = pymongo.MongoClient('localhost', 27017)
db = client['evaluation_db']

print("🔧 Suppression de l'index student_id_1...")

if 'user_profiles' in db.list_collection_names():
    collection = db['user_profiles']
    
    # Lister tous les index
    print("📋 Index existants:")
    for index in collection.list_indexes():
        print(f"  - {index['name']}")
    
    # Supprimer l'index student_id_1
    try:
        collection.drop_index('student_id_1')
        print("\n✅ Index 'student_id_1' supprimé avec succès!")
    except Exception as e:
        print(f"\n⚠️  Erreur: {e}")
    
    # Vérifier les index restants
    print("\n📋 Index restants:")
    for index in collection.list_indexes():
        print(f"  - {index['name']}")
else:
    print("⚠️  La collection 'user_profiles' n'existe pas encore")

client.close()
print("\n✅ Terminé ! Vous pouvez maintenant exécuter create_test_data.py")
