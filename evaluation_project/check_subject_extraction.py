"""
Script pour vérifier l'extraction du subject depuis CourseDocument
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['django_education']

# Récupérer un ExerciseSet
set_data = db.exercise_sets.find_one()
if set_data:
    print(f"✓ ExerciseSet: {set_data.get('title')}")
    print(f"  source_document_id: {set_data.get('source_document_id')}")
    
    # Récupérer le CourseDocument
    source_doc_id = set_data.get('source_document_id')
    if source_doc_id:
        doc = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
        if doc:
            print(f"\n✓ CourseDocument trouvé:")
            print(f"  title: {doc.get('title')}")
            print(f"  subject: {doc.get('subject')}")
            print(f"  subject capitalisé: {doc.get('subject').capitalize()}")
        else:
            print("\n✗ CourseDocument NOT FOUND")
    else:
        print("\n✗ Pas de source_document_id")
else:
    print("✗ Aucun ExerciseSet trouvé")

client.close()
