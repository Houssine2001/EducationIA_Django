"""
Test final pour vérifier que le dashboard affiche correctement après normalisation
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def test_dashboard_logic():
    print("=== TEST FINAL DASHBOARD ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Simuler la logique du dashboard pour user_id = 32
    user_id = 32
    
    print(f"\n1. TEST POUR USER_ID = {user_id}")
    
    # Documents récents (comme dans le dashboard)
    recent_documents_data = list(db.course_documents.find({
        'teacher_id': user_id  # Integer
    }).sort('created_at', -1).limit(5))
    
    print(f"📄 Documents récents trouvés: {len(recent_documents_data)}")
    for i, doc in enumerate(recent_documents_data):
        print(f"   {i+1}. [{doc['_id']}] {doc.get('title', 'N/A')}")
    
    # Récupérer TOUS les documents de l'enseignant pour filtrer les exercices
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': user_id})]
    
    print(f"📚 Total documents du teacher: {len(teacher_document_ids)}")
    print("   IDs des documents:", [str(doc_id) for doc_id in teacher_document_ids[:5]], "..." if len(teacher_document_ids) > 5 else "")
    
    # Exercices récents (comme dans le dashboard)
    recent_exercises_data = list(db.generated_exercises.find({
        'source_document_id': {'$in': teacher_document_ids}
    }).sort('created_at', -1).limit(10))
    
    print(f"✏️ Exercices récents trouvés: {len(recent_exercises_data)}")
    for i, ex in enumerate(recent_exercises_data[:3]):
        print(f"   {i+1}. [{ex['_id']}] {ex.get('question_text', 'N/A')[:50]}...")
        print(f"       Source doc: {ex.get('source_document_id', 'N/A')}")
    
    # Statistiques (comme dans le dashboard)
    total_documents = db.course_documents.count_documents({'teacher_id': user_id})
    total_exercises = db.generated_exercises.count_documents({'source_document_id': {'$in': teacher_document_ids}})
    total_tests = db.generated_tests.count_documents({'teacher_id': user_id})
    validated_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'validated'
    })
    pending_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'draft'
    })
    
    print(f"\n📊 STATISTIQUES DASHBOARD:")
    print(f"   📄 Total documents: {total_documents}")
    print(f"   ✏️ Total exercices: {total_exercises}")
    print(f"   📝 Total tests: {total_tests}")
    print(f"   ✅ Exercices validés: {validated_exercises}")
    print(f"   ⏳ Exercices en attente: {pending_exercises}")
    
    # Distribution par type d'exercice
    mcq_count = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'exercise_type': 'mcq'
    })
    true_false_count = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'exercise_type': 'true_false'
    })
    fill_blank_count = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'exercise_type': 'fill_blank'
    })
    
    print(f"\n📈 DISTRIBUTION PAR TYPE:")
    print(f"   🔵 MCQ: {mcq_count}")
    print(f"   🟢 Vrai/Faux: {true_false_count}")
    print(f"   🟡 Texte à trous: {fill_blank_count}")
    
    # Vérifier les ExerciseSets
    total_sets = db.exercise_sets.count_documents({'teacher_id': user_id})
    published_sets = db.exercise_sets.count_documents({'teacher_id': user_id, 'status': 'published'})
    
    print(f"\n📦 EXERCISE SETS:")
    print(f"   📦 Total sets: {total_sets}")
    print(f"   🌐 Sets publiés: {published_sets}")
    
    client.close()
    
    print(f"\n✅ TEST TERMINÉ")
    print(f"Le dashboard devrait maintenant afficher:")
    print(f"   - Documents: {total_documents}")
    print(f"   - Exercices: {total_exercises}")
    print(f"   - Tests: {total_tests}")
    print(f"   - Validés: {validated_exercises}")

if __name__ == "__main__":
    test_dashboard_logic()
