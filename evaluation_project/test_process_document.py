"""
Test de process_document pour vérifier qu'un seul document est créé
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from exercise_generator.models import CourseDocument
from exercise_generator.services import ExerciseGenerationService
from django.contrib.auth.models import User
from pymongo import MongoClient
from django.conf import settings

def test_process_document():
    print("\n=== TEST PROCESS_DOCUMENT (avec UPDATE) ===\n")
    
    # Compter documents avant
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    before_count = db.course_documents.count_documents({})
    print(f"Documents AVANT: {before_count}")
    
    # Créer un document via PyMongo (simule le formulaire)
    prof = User.objects.get(username='prof1')
    
    doc_data = {
        'teacher_id': prof.id,
        'title': 'Test UPDATE',
        'content': 'Python est un langage. Django est un framework. React est une bibliothèque.',
        'document_type': 'text',
        'subject': 'python',
        'processing_status': 'pending',
        'key_concepts': [],
        'main_topics': [],
        'word_count': 0,
        'sentence_count': 0,
    }
    
    result = db.course_documents.insert_one(doc_data)
    doc_id = result.inserted_id
    print(f"✅ Document initial créé: {doc_id}")
    
    # Créer instance Django
    clean_data = {k: v for k, v in doc_data.items() if k != '_id'}
    document = CourseDocument(**clean_data)
    document.pk = doc_id
    document._state.adding = False  # IMPORTANT : pas une nouvelle instance
    document._state.db = 'default'
    
    print(f"✅ Instance Django créée (_state.adding={document._state.adding})")
    
    # Lancer process_document (qui fait plusieurs save())
    print("\n--- Lancement process_document ---")
    service = ExerciseGenerationService()
    result_process = service.process_document(document)
    
    print(f"✅ Process terminé: {result_process['success']}")
    print(f"   Exercices générés: {len(result_process.get('exercises', []))}")
    
    # Vérifier qu'UN SEUL document existe
    after_count = db.course_documents.count_documents({})
    print(f"\nDocuments APRÈS: {after_count}")
    
    if after_count == before_count + 1:
        print("✅ SUCCÈS : Un seul document créé (UPDATE fonctionnel)")
    else:
        print(f"❌ ERREUR : {after_count - before_count} documents créés au lieu de 1")
        print("   Les save() créent de nouveaux documents au lieu d'UPDATE")
    
    # Vérifier le contenu final
    final_doc = db.course_documents.find_one({'_id': doc_id})
    print(f"\n--- État final du document ---")
    print(f"  Statut: {final_doc['processing_status']}")
    print(f"  Concepts: {len(final_doc.get('key_concepts', []))} concepts")
    print(f"  Word count: {final_doc.get('word_count', 0)}")
    print(f"  Processing log: {final_doc.get('processing_log', 'N/A')[:80]}...")
    
    # Compter exercices
    ex_count = db.generated_exercises.count_documents({'source_document_id': doc_id})
    print(f"  Exercices liés: {ex_count}")
    
    # Nettoyage
    # db.generated_exercises.delete_many({'source_document_id': doc_id})
    # db.course_documents.delete_one({'_id': doc_id})
    # print(f"\n✅ Nettoyage effectué")
    print(f"\n⚠️  Document {doc_id} conservé pour inspection")

if __name__ == '__main__':
    test_process_document()
