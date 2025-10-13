"""
Diagnostic pour identifier pourquoi les nouveaux exercices ne s'affichent pas
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from bson import ObjectId
from collections import defaultdict

def diagnostic_nouveaux_exercices():
    print("=== DIAGNOSTIC NOUVEAUX EXERCICES ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Compter TOUS les exercices
    total_exercises = db.generated_exercises.count_documents({})
    print(f"📊 TOTAL exercices dans MongoDB: {total_exercises}")
    
    # 2. Analyser les exercices par teacher/document
    print(f"\n🔍 ANALYSE PAR DOCUMENT:")
    
    # Récupérer tous les documents
    all_docs = list(db.course_documents.find({}, {'_id': 1, 'teacher_id': 1, 'title': 1, 'created_at': 1}))
    print(f"   📄 Total documents: {len(all_docs)}")
    
    teacher_stats = defaultdict(lambda: {'docs': 0, 'exercises': 0, 'doc_ids': []})
    
    for doc in all_docs:
        teacher_id = doc.get('teacher_id')
        teacher_key = f"{teacher_id} ({type(teacher_id).__name__})"
        teacher_stats[teacher_key]['docs'] += 1
        teacher_stats[teacher_key]['doc_ids'].append(doc['_id'])
    
    # 3. Pour chaque teacher, compter les exercices
    for teacher_key, stats in teacher_stats.items():
        doc_ids = stats['doc_ids']
        exercise_count = db.generated_exercises.count_documents({
            'source_document_id': {'$in': doc_ids}
        })
        stats['exercises'] = exercise_count
        
        print(f"   👨‍🏫 {teacher_key}: {stats['docs']} docs → {exercise_count} exercices")
        
        # Afficher les derniers exercices de ce teacher
        recent_exercises = list(db.generated_exercises.find({
            'source_document_id': {'$in': doc_ids}
        }).sort('created_at', -1).limit(3))
        
        for i, ex in enumerate(recent_exercises):
            print(f"      🔹 [{ex['_id']}] {ex.get('question_text', 'N/A')[:40]}...")
    
    # 4. Vérifier spécifiquement pour teacher_id = 32
    print(f"\n🎯 FOCUS SUR TEACHER_ID = 32:")
    
    # Documents avec teacher_id = 32 (integer)
    docs_int = list(db.course_documents.find({'teacher_id': 32}))
    doc_ids_int = [doc['_id'] for doc in docs_int]
    exercises_int = db.generated_exercises.count_documents({'source_document_id': {'$in': doc_ids_int}})
    
    # Documents avec teacher_id = "32" (string)
    docs_str = list(db.course_documents.find({'teacher_id': '32'}))
    doc_ids_str = [doc['_id'] for doc in docs_str]
    exercises_str = db.generated_exercises.count_documents({'source_document_id': {'$in': doc_ids_str}})
    
    print(f"   📄 Documents teacher_id=32 (int): {len(docs_int)} → {exercises_int} exercices")
    print(f"   📄 Documents teacher_id='32' (str): {len(docs_str)} → {exercises_str} exercices")
    print(f"   📊 TOTAL pour teacher 32: {exercises_int + exercises_str} exercices")
    
    # 5. Analyser les derniers exercices créés
    print(f"\n⏰ DERNIERS EXERCICES CRÉÉS:")
    latest_exercises = list(db.generated_exercises.find().sort('created_at', -1).limit(10))
    
    for i, ex in enumerate(latest_exercises):
        source_doc_id = ex.get('source_document_id')
        
        # Trouver le document correspondant
        doc = db.course_documents.find_one({'_id': source_doc_id})
        if doc:
            teacher_id = doc.get('teacher_id')
            teacher_type = type(teacher_id).__name__
            doc_title = doc.get('title', 'N/A')
        else:
            teacher_id = 'UNKNOWN'
            teacher_type = 'UNKNOWN'
            doc_title = 'DOCUMENT NOT FOUND'
        
        print(f"   {i+1}. [{ex['_id']}] Teacher: {teacher_id} ({teacher_type})")
        print(f"      Doc: [{source_doc_id}] {doc_title}")
        print(f"      Created: {ex.get('created_at', 'N/A')}")
        print()
    
    # 6. Recommandations
    print(f"🔧 RECOMMANDATIONS:")
    if docs_str:
        print(f"   ❌ Il y a encore {len(docs_str)} documents avec teacher_id en string")
        print(f"   💡 Exécuter normalize_teacher_ids_final.py à nouveau")
    else:
        print(f"   ✅ Tous les documents ont teacher_id en integer")
    
    if exercises_int + exercises_str != total_exercises:
        orphan_exercises = total_exercises - (exercises_int + exercises_str)
        print(f"   ⚠️ Il y a {orphan_exercises} exercices orphelins (sans document parent valide)")
    
    client.close()
    print(f"\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnostic_nouveaux_exercices()
