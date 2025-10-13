"""
Normaliser DÉFINITIVEMENT tous les teacher_id en integers
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient

def normalize_all_teacher_ids():
    print("=== NORMALISATION DÉFINITIVE TEACHER_IDS ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Normaliser les course_documents
    print("\n1. NORMALISATION COURSE_DOCUMENTS")
    docs_with_string_id = list(db.course_documents.find({'teacher_id': {'$type': 'string'}}))
    print(f"   Trouvé {len(docs_with_string_id)} documents avec teacher_id string")
    
    for doc in docs_with_string_id:
        old_teacher_id = doc['teacher_id']
        try:
            new_teacher_id = int(old_teacher_id)
            result = db.course_documents.update_one(
                {'_id': doc['_id']},
                {'$set': {'teacher_id': new_teacher_id}}
            )
            print(f"   ✅ Document {doc['_id']}: '{old_teacher_id}' → {new_teacher_id}")
        except ValueError:
            print(f"   ❌ Document {doc['_id']}: Cannot convert '{old_teacher_id}' to int")
    
    # 2. Normaliser les generated_tests
    print("\n2. NORMALISATION GENERATED_TESTS")
    tests_with_string_id = list(db.generated_tests.find({'teacher_id': {'$type': 'string'}}))
    print(f"   Trouvé {len(tests_with_string_id)} tests avec teacher_id string")
    
    for test in tests_with_string_id:
        old_teacher_id = test['teacher_id']
        try:
            new_teacher_id = int(old_teacher_id)
            result = db.generated_tests.update_one(
                {'_id': test['_id']},
                {'$set': {'teacher_id': new_teacher_id}}
            )
            print(f"   ✅ Test {test['_id']}: '{old_teacher_id}' → {new_teacher_id}")
        except ValueError:
            print(f"   ❌ Test {test['_id']}: Cannot convert '{old_teacher_id}' to int")
    
    # 3. Normaliser les exercise_sets
    print("\n3. NORMALISATION EXERCISE_SETS")
    sets_with_string_id = list(db.exercise_sets.find({'teacher_id': {'$type': 'string'}}))
    print(f"   Trouvé {len(sets_with_string_id)} sets avec teacher_id string")
    
    for ex_set in sets_with_string_id:
        old_teacher_id = ex_set['teacher_id']
        try:
            new_teacher_id = int(old_teacher_id)
            result = db.exercise_sets.update_one(
                {'_id': ex_set['_id']},
                {'$set': {'teacher_id': new_teacher_id}}
            )
            print(f"   ✅ Set {ex_set['_id']}: '{old_teacher_id}' → {new_teacher_id}")
        except ValueError:
            print(f"   ❌ Set {ex_set['_id']}: Cannot convert '{old_teacher_id}' to int")
    
    # 4. Vérification finale
    print("\n4. VÉRIFICATION FINALE")
    final_docs = db.course_documents.count_documents({'teacher_id': 32})
    final_docs_string = db.course_documents.count_documents({'teacher_id': '32'})
    final_tests = db.generated_tests.count_documents({'teacher_id': 32})
    final_sets = db.exercise_sets.count_documents({'teacher_id': 32})
    
    print(f"   📄 Documents avec teacher_id=32 (int): {final_docs}")
    print(f"   📄 Documents avec teacher_id='32' (str): {final_docs_string}")
    print(f"   📝 Tests avec teacher_id=32 (int): {final_tests}")
    print(f"   📦 Sets avec teacher_id=32 (int): {final_sets}")
    
    if final_docs_string == 0:
        print("   ✅ NORMALISATION RÉUSSIE !")
    else:
        print("   ❌ Il reste encore des teacher_id en string")
    
    client.close()
    print("\n=== NORMALISATION TERMINÉE ===")

if __name__ == "__main__":
    normalize_all_teacher_ids()
