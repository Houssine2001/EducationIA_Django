"""
Test de récupération d'un GeneratedExercise via PyMongo
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

# ID de l'exercice de l'erreur
exercise_id = "68e7f8b3a366a0c4478f99bc"

try:
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Tenter de convertir en ObjectId
    try:
        object_id = ObjectId(exercise_id)
        print(f"✅ ObjectId valide: {object_id}")
    except Exception as e:
        print(f"❌ ObjectId invalide: {e}")
        exit(1)
    
    # Chercher l'exercice
    exercise_data = db.generated_exercises.find_one({'_id': object_id})
    
    if exercise_data:
        print(f"\n✅ Exercice trouvé!")
        print(f"   ID: {exercise_data.get('_id')}")
        print(f"   Question: {exercise_data.get('question', 'N/A')[:80]}...")
        print(f"   Type: {exercise_data.get('exercise_type')}")
        print(f"   Source Document ID: {exercise_data.get('source_document_id')}")
        print(f"   Status: {exercise_data.get('status')}")
        print(f"   Quality Score: {exercise_data.get('quality_score')}")
        
        # Vérifier le document source
        source_doc_id = exercise_data.get('source_document_id')
        if source_doc_id:
            print(f"\n🔍 Recherche du document source...")
            source_doc = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
            if source_doc:
                print(f"   ✅ Document source trouvé:")
                print(f"      Title: {source_doc.get('title')}")
                print(f"      Subject: {source_doc.get('subject')}")
                print(f"      Teacher ID: {source_doc.get('teacher_id')}")
            else:
                print(f"   ❌ Document source NON trouvé")
    else:
        print(f"\n❌ Exercice NON trouvé dans la collection 'generated_exercises'")
        
        # Chercher dans toutes les collections
        print("\n🔍 Recherche dans toutes les collections...")
        for collection_name in db.list_collection_names():
            doc = db[collection_name].find_one({'_id': object_id})
            if doc:
                print(f"   ✅ Trouvé dans '{collection_name}'")
    
    client.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
