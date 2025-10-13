"""
Diagnostic spécifique pour les Documents Récents du dashboard
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

def diagnostic_documents_recents():
    print("=== DIAGNOSTIC DOCUMENTS RÉCENTS ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    user_id = 32  # User principal
    
    print(f"🔍 USER ID: {user_id}")
    
    # 1. Vérifier tous les documents de l'utilisateur
    all_docs = list(db.course_documents.find({'teacher_id': user_id}).sort('created_at', -1))
    print(f"📚 TOTAL documents pour user {user_id}: {len(all_docs)}")
    
    # 2. Afficher les 10 premiers pour voir la structure
    print(f"\n📄 LES 10 DOCUMENTS LES PLUS RÉCENTS:")
    for i, doc in enumerate(all_docs[:10]):
        print(f"   {i+1}. [{doc['_id']}] {doc.get('title', 'N/A')}")
        print(f"      Teacher ID: {doc.get('teacher_id')} ({type(doc.get('teacher_id')).__name__})")
        print(f"      Created: {doc.get('created_at', 'N/A')}")
        print(f"      Status: {doc.get('processing_status', 'N/A')}")
        print()
    
    # 3. Tester la requête exacte du dashboard
    print(f"🎯 TEST REQUÊTE DASHBOARD (limite 5):")
    recent_documents_data = list(db.course_documents.find({
        'teacher_id': user_id
    }).sort('created_at', -1).limit(5))
    
    print(f"   Trouvé: {len(recent_documents_data)} documents")
    for i, doc in enumerate(recent_documents_data):
        print(f"   {i+1}. [{doc['_id']}] {doc.get('title', 'N/A')}")
    
    # 4. Vérifier les types de données
    print(f"\n🔍 TYPES DE DONNÉES:")
    if all_docs:
        first_doc = all_docs[0]
        for key, value in first_doc.items():
            print(f"   {key}: {type(value).__name__} = {value}")
    
    # 5. Vérifier s'il y a des documents avec des teacher_id différents
    print(f"\n👥 RÉPARTITION PAR TEACHER_ID:")
    pipeline = [
        {"$group": {"_id": "$teacher_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    teacher_groups = list(db.course_documents.aggregate(pipeline))
    
    for group in teacher_groups:
        teacher_id_val = group['_id']
        count = group['count']
        print(f"   Teacher ID {teacher_id_val} ({type(teacher_id_val).__name__}): {count} documents")
    
    client.close()
    print(f"\n=== FIN DIAGNOSTIC DOCUMENTS ===")

if __name__ == "__main__":
    diagnostic_documents_recents()
