"""
Script de diagnostic spécifique pour le problème dashboard affichage 0 exercices
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
from django.contrib.auth.models import User

def main():
    print("=== DIAGNOSTIC PROBLÈME DASHBOARD ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # Prendre l'utilisateur prof1 (ID: 32)
    user_id = 32
    print(f"\n🔍 ANALYSE POUR USER ID: {user_id}")
    
    # 1. Documents de cet utilisateur
    print("\n1. DOCUMENTS DU PROFESSEUR")
    user_docs = list(db.course_documents.find({'teacher_id': user_id}))
    print(f"Nombre de documents: {len(user_docs)}")
    
    teacher_document_ids = []
    for i, doc in enumerate(user_docs):
        doc_id = doc['_id']
        teacher_document_ids.append(doc_id)
        print(f"Doc {i+1}: {doc_id} - {doc.get('title', 'N/A')}")
    
    # 2. Exercices liés à ces documents
    print(f"\n2. EXERCICES LIÉS AUX DOCUMENTS")
    print(f"Recherche avec document IDs: {teacher_document_ids}")
    
    # Recherche exacte par source_document_id
    total_exercises = 0
    for doc_id in teacher_document_ids:
        exercises_for_doc = list(db.generated_exercises.find({'source_document_id': doc_id}))
        total_exercises += len(exercises_for_doc)
        print(f"Document {doc_id}: {len(exercises_for_doc)} exercices")
        
        if exercises_for_doc:
            for j, ex in enumerate(exercises_for_doc[:2]):  # Montrer 2 premiers
                print(f"  - Exercice {j+1}: {ex['_id']} - {ex.get('question_text', 'N/A')[:50]}...")
    
    print(f"\n📊 TOTAL EXERCICES TROUVÉS: {total_exercises}")
    
    # 3. Vérifier le problème potentiel avec ObjectId vs String
    print("\n3. VÉRIFICATION TYPE D'IDS")
    if user_docs:
        first_doc = user_docs[0]
        doc_id = first_doc['_id']
        print(f"Type de l'ID document: {type(doc_id)} - {doc_id}")
        
        # Chercher avec différents types
        exercises_with_objectid = list(db.generated_exercises.find({'source_document_id': doc_id}))
        exercises_with_string = list(db.generated_exercises.find({'source_document_id': str(doc_id)}))
        
        print(f"Exercices trouvés avec ObjectId: {len(exercises_with_objectid)}")
        print(f"Exercices trouvés avec String: {len(exercises_with_string)}")
    
    # 4. Vérifier tous les exercices de la base pour cet utilisateur
    print("\n4. VERIFICATION GLOBALE")
    all_exercises = list(db.generated_exercises.find())
    user_exercises = []
    
    for ex in all_exercises:
        source_doc_id = ex.get('source_document_id')
        if source_doc_id in teacher_document_ids:
            user_exercises.append(ex)
    
    print(f"Total exercices dans la base: {len(all_exercises)}")
    print(f"Exercices de l'utilisateur (méthode alternative): {len(user_exercises)}")
    
    # 5. Afficher quelques exercices récents
    print("\n5. EXERCICES RÉCENTS DE L'UTILISATEUR")
    if user_exercises:
        sorted_exercises = sorted(user_exercises, key=lambda x: x.get('created_at', ''), reverse=True)
        for i, ex in enumerate(sorted_exercises[:3]):
            print(f"Exercice {i+1}:")
            print(f"  - ID: {ex['_id']}")
            print(f"  - Source Doc ID: {ex.get('source_document_id')} (type: {type(ex.get('source_document_id'))})")
            print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
            print(f"  - Status: {ex.get('status', 'N/A')}")
    
    client.close()
    print("\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    main()
