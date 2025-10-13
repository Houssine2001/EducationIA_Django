"""
Script pour analyser les source_document_id dans les exercices
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from bson.objectid import ObjectId

def main():
    print("=== ANALYSE SOURCE_DOCUMENT_ID ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Récupérer les exercices récents
    recent_exercises = list(db.generated_exercises.find().sort('created_at', -1).limit(10))
    
    print(f"Analysing {len(recent_exercises)} exercices récents:")
    
    for i, ex in enumerate(recent_exercises):
        print(f"\nExercice {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Source Document ID: {ex.get('source_document_id')} (type: {type(ex.get('source_document_id'))})")
        print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
        print(f"  - Created: {ex.get('created_at', 'N/A')}")
        
        # Vérifier si ce document existe
        source_doc_id = ex.get('source_document_id')
        if source_doc_id:
            try:
                # Essayer avec ObjectId
                if isinstance(source_doc_id, str):
                    source_doc_id = ObjectId(source_doc_id)
                
                doc = db.course_documents.find_one({'_id': source_doc_id})
                if doc:
                    print(f"  ✅ Document trouvé: {doc.get('title', 'N/A')} (Teacher ID: {doc.get('teacher_id', 'N/A')})")
                else:
                    print(f"  ❌ Document NON trouvé avec ID: {source_doc_id}")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
    
    # Lister tous les documents existants
    print("\n=== DOCUMENTS EXISTANTS ===")
    all_docs = list(db.course_documents.find())
    for i, doc in enumerate(all_docs):
        print(f"Doc {i+1}: {doc['_id']} - {doc.get('title', 'N/A')} (Teacher: {doc.get('teacher_id', 'N/A')})")
    
    client.close()
    print("\n=== FIN ANALYSE ===")

if __name__ == "__main__":
    main()
