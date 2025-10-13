"""
Vérifier l'état des teacher_id après normalisation
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from collections import defaultdict

def check_teacher_ids():
    print("=== VÉRIFICATION TEACHER_IDS APRÈS NORMALISATION ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Vérifier les types de teacher_id
    docs = list(db.course_documents.find({}, {'teacher_id': 1, 'title': 1}))
    
    type_counts = defaultdict(int)
    teacher_groups = defaultdict(list)
    
    print(f"📊 Total documents dans MongoDB: {len(docs)}")
    
    for doc in docs:
        teacher_id = doc.get('teacher_id')
        teacher_id_type = type(teacher_id).__name__
        type_counts[teacher_id_type] += 1
        teacher_groups[f"{teacher_id} ({teacher_id_type})"].append({
            'id': str(doc['_id']),
            'title': doc.get('title', 'N/A')
        })
    
    print(f"\n📋 RÉPARTITION PAR TYPE:")
    for type_name, count in type_counts.items():
        print(f"   {type_name}: {count} documents")
    
    print(f"\n👥 REGROUPEMENT PAR TEACHER_ID:")
    for teacher_info, docs_list in teacher_groups.items():
        print(f"   - {teacher_info}: {len(docs_list)} documents")
        for i, doc in enumerate(docs_list[:3]):  # Afficher les 3 premiers
            print(f"      * [{doc['id']}] {doc['title']}")
        if len(docs_list) > 3:
            print(f"      ... et {len(docs_list) - 3} autres")
    
    # Vérifier aussi les exercices
    print(f"\n🔍 VÉRIFICATION EXERCICES:")
    
    # Compter les exercices par document
    for teacher_info, docs_list in teacher_groups.items():
        teacher_part = teacher_info.split(' (')[0]  # Extraire juste le teacher_id
        try:
            if teacher_part.isdigit():
                teacher_id_clean = int(teacher_part)
            else:
                teacher_id_clean = teacher_part
        except:
            teacher_id_clean = teacher_part
            
        doc_ids = [doc['id'] for doc in docs_list]
        
        # Convertir les doc_ids en ObjectId pour la recherche
        from bson import ObjectId
        object_doc_ids = []
        for doc_id in doc_ids:
            try:
                object_doc_ids.append(ObjectId(doc_id))
            except:
                pass
        
        exercise_count = db.generated_exercises.count_documents({
            'source_document_id': {'$in': object_doc_ids}
        })
        
        print(f"   {teacher_info}: {exercise_count} exercices")
    
    client.close()
    print("\n=== FIN VÉRIFICATION ===")

if __name__ == "__main__":
    check_teacher_ids()
