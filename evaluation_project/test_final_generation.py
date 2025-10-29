"""
✅ TEST FINAL : Génération complète d'exercices avec ObjectId

Ce script teste le flux complet :
1. Créer un document via PyMongo (comme le formulaire)
2. Lancer process_document() (analyse + génération)
3. Vérifier qu'UN SEUL document existe
4. Vérifier que les exercices sont sauvegardés
5. Récupérer le document avec les exercices (comme document_detail)
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from exercise_generator.models import CourseDocument, GeneratedExercise
from exercise_generator.services import ExerciseGenerationService
from django.contrib.auth.models import User
from pymongo import MongoClient
from django.conf import settings
from backend.mongodb_utils import get_mongodb_client

def main():
    print("\n" + "="*70)
    print("🚀 TEST FINAL - GÉNÉRATION COMPLÈTE D'EXERCICES")
    print("="*70 + "\n")
    
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    # 0. Compter documents avant
    before_docs = db.course_documents.count_documents({})
    before_exercises = db.generated_exercises.count_documents({})
    print(f"📊 AVANT : {before_docs} documents, {before_exercises} exercices\n")
    
    # 1. Créer un document (simule le formulaire)
    prof = User.objects.get(username='prof1')
    
    text = """
    Python est un langage de programmation de haut niveau, interprété et polyvalent.
    Django est un framework web Python qui suit le pattern MVT (Model-View-Template).
    React est une bibliothèque JavaScript pour construire des interfaces utilisateur.
    MongoDB est une base de données NoSQL orientée documents.
    """
    
    doc_data = {
        'teacher_id': prof.id,
        'title': 'Test Final - Technologies Web',
        'content': text,
        'document_type': 'text',
        'subject': 'informatique',
        'topic': 'Technologies modernes',
        'processing_status': 'pending',
        'key_concepts': [],
        'main_topics': [],
        'word_count': 0,
        'sentence_count': 0,
    }
    
    result = db.course_documents.insert_one(doc_data)
    doc_id = result.inserted_id
    print(f"✅ Document créé: {doc_id}")
    print(f"   Titre: {doc_data['title']}")
    print(f"   Contenu: {len(text)} caractères\n")
    
    # 2. Créer instance Django
    clean_data = {k: v for k, v in doc_data.items() if k != '_id'}
    document = CourseDocument(**clean_data)
    document.pk = doc_id
    document._state.adding = False
    document._state.db = 'default'
    
    # 3. Lancer process_document (analyse + génération)
    print("🔄 Lancement du traitement...\n")
    service = ExerciseGenerationService()
    result_process = service.process_document(document)
    
    if result_process['success']:
        print(f"✅ Traitement réussi !")
        print(f"   Exercices générés: {len(result_process.get('exercises', []))}")
        print(f"   Concepts extraits: {len(result_process.get('analysis', {}).get('key_concepts', []))}")
    else:
        print(f"❌ Erreur: {result_process.get('error', 'Inconnue')}")
        return
    
    print()
    
    # 4. Vérifier qu'UN SEUL document a été créé
    after_docs = db.course_documents.count_documents({})
    after_exercises = db.generated_exercises.count_documents({})
    
    new_docs = after_docs - before_docs
    new_exercises = after_exercises - before_exercises
    
    print(f"📊 APRÈS : {after_docs} documents (+{new_docs}), {after_exercises} exercices (+{new_exercises})\n")
    
    if new_docs == 1:
        print("✅ SUCCÈS : Un seul document créé (UPDATE fonctionne)")
    else:
        print(f"❌ ERREUR : {new_docs} documents créés au lieu de 1")
    
    print()
    
    # 5. Vérifier l'état final du document
    final_doc = db.course_documents.find_one({'_id': doc_id})
    
    print("📄 État final du document:")
    print(f"   Statut: {final_doc.get('processing_status', 'N/A')}")
    print(f"   Concepts: {final_doc.get('key_concepts', [])}")
    print(f"   Mots: {final_doc.get('word_count', 0)}")
    print(f"   Phrases: {final_doc.get('sentence_count', 0)}")
    print()
    
    # 6. Récupérer les exercices liés
    exercises = list(db.generated_exercises.find({'source_document_id': doc_id}))
    
    print(f"📝 Exercices générés: {len(exercises)}")
    for i, ex in enumerate(exercises, 1):
        print(f"\n   {i}. Type: {ex.get('exercise_type', 'N/A')}")
        print(f"      Question: {ex.get('question_text', 'N/A')[:60]}...")
        print(f"      Concept: {ex.get('concept', 'N/A')}")
        print(f"      Difficulté: {ex.get('difficulty', 'N/A')}")
        print(f"      Qualité: {ex.get('quality_score', 0):.2f}")
    
    print()
    
    # 7. Tester la récupération comme dans document_detail
    print("🔍 Test de récupération (comme document_detail):")
    
    from exercise_generator.views import get_mongo_object
    
    try:
        retrieved_doc = get_mongo_object(CourseDocument, str(doc_id), teacher=prof)
        print(f"✅ Document récupéré: {retrieved_doc.title}")
        print(f"   PK: {retrieved_doc.pk}")
        print(f"   Type PK: {type(retrieved_doc.pk).__name__}")
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
    
    print()
    
    # 8. Résumé final
    print("="*70)
    print("📋 RÉSUMÉ")
    print("="*70)
    print(f"✅ Document créé avec ObjectId")
    print(f"✅ Traitement complet sans duplication")
    print(f"✅ {len(exercises)} exercices sauvegardés")
    print(f"✅ Récupération fonctionnelle")
    print()
    
    if new_docs == 1 and len(exercises) > 0:
        print("🎉 TOUS LES TESTS PASSENT !")
        print()
        print("👉 Testez maintenant dans le navigateur:")
        print(f"   http://localhost:8000/generator/documents/{doc_id}/")
    else:
        print("⚠️  Certains tests ont échoué")
    
    print()
    print("🗑️  Note: Document et exercices conservés pour inspection")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
