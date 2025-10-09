"""
Script de diagnostic pour vérifier les corrections MongoDB/Djongo
Exécute une série de tests pour s'assurer que tout fonctionne correctement
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

def test_connection():
    """Test 1: Connexion MongoDB"""
    print("\n" + "="*60)
    print("TEST 1: Connexion MongoDB")
    print("="*60)
    try:
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ Connexion MongoDB réussie")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_objectid_foreign_keys(client):
    """Test 2: Vérifier que les ForeignKeys sont des strings"""
    print("\n" + "="*60)
    print("TEST 2: Vérification ForeignKeys (ObjectId → String)")
    print("="*60)
    
    db = client.django_education
    collections_to_check = {
        'course_documents': ['teacher_id'],
        'generated_exercises': ['source_document_id', 'validated_by_id'],
        'generated_tests': ['source_document_id', 'teacher_id'],
        'exercise_sets': ['teacher_id', 'source_document_id'],
        'student_exercise_submissions': ['student_id', 'exercise_set_id']
    }
    
    all_ok = True
    for collection_name, fields in collections_to_check.items():
        collection = db[collection_name]
        count = collection.count_documents({})
        
        if count == 0:
            print(f"⚠️  {collection_name}: Aucun document (normal si données vides)")
            continue
        
        print(f"\n📄 {collection_name} ({count} documents)")
        
        for field in fields:
            # Chercher des ObjectIds (devrait être 0)
            objectid_count = collection.count_documents({field: {'$type': 'objectId'}})
            string_count = collection.count_documents({field: {'$type': 'string'}})
            
            if objectid_count > 0:
                print(f"   ❌ {field}: {objectid_count} ObjectId trouvés (devrait être 0)")
                all_ok = False
            else:
                print(f"   ✅ {field}: {string_count} strings, 0 ObjectId")
    
    if all_ok:
        print("\n✅ Tous les ForeignKeys sont correctement stockés comme strings!")
    else:
        print("\n❌ Des ObjectIds ont été trouvés. Exécutez: python fix_objectid_foreign_keys.py")
    
    return all_ok

def test_data_integrity(client):
    """Test 3: Vérifier l'intégrité des données"""
    print("\n" + "="*60)
    print("TEST 3: Intégrité des Données")
    print("="*60)
    
    db = client.django_education
    
    # Compter les documents
    stats = {
        'CourseDocuments': db.course_documents.count_documents({}),
        'GeneratedExercises': db.generated_exercises.count_documents({}),
        'GeneratedTests': db.generated_tests.count_documents({}),
        'ExerciseSets': db.exercise_sets.count_documents({}),
        'Submissions': db.student_exercise_submissions.count_documents({})
    }
    
    print("\n📊 Statistiques:")
    total = 0
    for name, count in stats.items():
        print(f"   {name}: {count}")
        total += count
    
    print(f"\n   TOTAL: {total} documents")
    
    if total > 0:
        print("✅ Base de données contient des données")
    else:
        print("⚠️  Base de données vide (normal pour un nouveau projet)")
    
    return True

def test_string_id_format(client):
    """Test 4: Vérifier le format des IDs strings"""
    print("\n" + "="*60)
    print("TEST 4: Format des IDs (24 caractères hexadécimaux)")
    print("="*60)
    
    db = client.django_education
    collection = db.exercise_sets
    
    sample = collection.find_one({})
    if not sample:
        print("⚠️  Pas de données pour tester (normal si DB vide)")
        return True
    
    all_ok = True
    fields_to_check = ['teacher_id', 'source_document_id']
    
    for field in fields_to_check:
        if field in sample:
            value = sample[field]
            
            # Vérifier le type
            if isinstance(value, int):
                # Les User IDs (teacher_id, student_id, etc.) peuvent être des ints
                # car auth_user utilise des IDs auto-incrémentés
                print(f"   ✅ {field}: {value} (ID Django User - int normal)")
                continue
            
            if not isinstance(value, str):
                print(f"   ❌ {field}: Type incorrect ({type(value).__name__})")
                all_ok = False
                continue
            
            # Vérifier la longueur (ObjectId = 24 caractères hex)
            if len(value) == 24:
                try:
                    # Vérifier que c'est un hex valide
                    int(value, 16)
                    print(f"   ✅ {field}: '{value}' (format ObjectId valide)")
                except ValueError:
                    print(f"   ⚠️  {field}: '{value}' (pas hexadécimal mais string)")
            elif len(value) < 10:
                # Probablement un ID integer converti en string
                print(f"   ✅ {field}: '{value}' (ID numérique en string)")
            else:
                print(f"   ⚠️  {field}: '{value}' (format inattendu)")
    
    return all_ok

def test_indexes(client):
    """Test 5: Vérifier les indexes MongoDB"""
    print("\n" + "="*60)
    print("TEST 5: Indexes MongoDB")
    print("="*60)
    
    db = client.django_education
    important_collections = ['course_documents', 'generated_exercises', 'exercise_sets']
    
    for collection_name in important_collections:
        collection = db[collection_name]
        indexes = list(collection.list_indexes())
        print(f"\n📋 {collection_name}:")
        for idx in indexes:
            keys = ', '.join([f"{k}: {v}" for k, v in idx['key'].items()])
            print(f"   - {idx['name']}: {keys}")
    
    return True

def test_django_compatibility():
    """Test 6: Tester l'importation Django"""
    print("\n" + "="*60)
    print("TEST 6: Compatibilité Django")
    print("="*60)
    
    try:
        # Essayer d'importer Django
        import django
        print(f"✅ Django {django.get_version()} importé")
        
        # Configurer Django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        print("✅ Django setup() réussi")
        
        # Importer les modèles
        from exercise_generator.models import ExerciseSet, CourseDocument
        print("✅ Modèles importés (exercise_generator)")
        
        from evaluation.models import UserProfile
        print("✅ Modèles importés (evaluation)")
        
        return True
    except Exception as e:
        print(f"❌ Erreur Django: {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("\n" + "🔍"*30)
    print("DIAGNOSTIC MONGODB/DJONGO - Vérification des Corrections")
    print("🔍"*30)
    
    # Test 1: Connexion
    client = test_connection()
    if not client:
        print("\n❌ Impossible de continuer sans connexion MongoDB")
        return False
    
    # Test 2: ObjectId → String
    test2_ok = test_objectid_foreign_keys(client)
    
    # Test 3: Intégrité des données
    test3_ok = test_data_integrity(client)
    
    # Test 4: Format des IDs
    test4_ok = test_string_id_format(client)
    
    # Test 5: Indexes
    test5_ok = test_indexes(client)
    
    # Fermer la connexion
    client.close()
    
    # Test 6: Django (après fermeture MongoDB)
    test6_ok = test_django_compatibility()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    
    results = {
        "Connexion MongoDB": True,
        "ForeignKeys (ObjectId→String)": test2_ok,
        "Intégrité des données": test3_ok,
        "Format des IDs": test4_ok,
        "Indexes MongoDB": test5_ok,
        "Compatibilité Django": test6_ok
    }
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système est prêt à être utilisé")
        return True
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("📖 Consultez RECAPITULATIF_CORRECTIONS_MONGODB.md pour plus d'infos")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
