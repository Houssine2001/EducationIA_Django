"""
Test de récupération d'un CourseDocument via PyMongo
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

# ID du document de l'erreur
doc_id = "68e7f78425de1147e82c3510"

try:
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Tenter de convertir en ObjectId
    try:
        object_id = ObjectId(doc_id)
        print(f"✅ ObjectId valide: {object_id}")
    except Exception as e:
        print(f"❌ ObjectId invalide: {e}")
        exit(1)
    
    # Chercher le document
    doc_data = db.course_documents.find_one({'_id': object_id})
    
    if doc_data:
        print(f"\n✅ Document trouvé!")
        print(f"   ID: {doc_data.get('_id')}")
        print(f"   Title: {doc_data.get('title')}")
        print(f"   Teacher ID: {doc_data.get('teacher_id')}")
        print(f"   Subject: {doc_data.get('subject')}")
        print(f"   Status: {doc_data.get('processing_status')}")
    else:
        print(f"\n❌ Document NON trouvé dans la collection 'course_documents'")
        
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
