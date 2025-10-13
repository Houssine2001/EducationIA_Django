"""
Script pour identifier et réparer les exercices problématiques
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
from bson.objectid import ObjectId

def find_and_fix_problematic_exercises():
    print("=== IDENTIFICATION ET RÉPARATION DES EXERCICES PROBLÉMATIQUES ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # 1. Récupérer tous les IDs de documents valides
    valid_document_ids = set()
    for doc in db.course_documents.find({}, {'_id': 1}):
        valid_document_ids.add(doc['_id'])
    
    print(f"Documents source valides trouvés: {len(valid_document_ids)}")
    
    # 2. Chercher tous les exercices et vérifier leur source_document_id
    print(f"\n2. VÉRIFICATION DES EXERCICES")
    
    problematic_exercises = []
    all_exercises = list(db.generated_exercises.find())
    
    for ex in all_exercises:
        source_id = ex.get('source_document_id')
        is_problematic = False
        reason = ""
        
        if not source_id:
            is_problematic = True
            reason = "source_document_id manquant"
        elif source_id not in valid_document_ids:
            is_problematic = True
            reason = "source_document_id inexistant dans course_documents"
        
        if is_problematic:
            problematic_exercises.append({
                'exercise': ex,
                'reason': reason
            })
    
    print(f"Exercices problématiques trouvés: {len(problematic_exercises)}")
    
    # 3. Afficher les détails des exercices problématiques
    for i, item in enumerate(problematic_exercises):
        ex = item['exercise']
        reason = item['reason']
        print(f"\nExercice problématique {i+1}:")
        print(f"  - ID: {ex['_id']}")
        print(f"  - Question: {ex.get('question_text', 'N/A')[:50]}...")
        print(f"  - Source Document ID: {repr(ex.get('source_document_id', 'MISSING'))}")
        print(f"  - Problème: {reason}")
        print(f"  - Status: {ex.get('status', 'N/A')}")
        print(f"  - Created: {ex.get('created_at', 'N/A')}")
    
    # 4. Proposer des actions de réparation
    if problematic_exercises:
        print(f"\n4. ACTIONS DE RÉPARATION PROPOSÉES")
        print("Options disponibles:")
        print("1. Supprimer les exercices problématiques")
        print("2. Assigner un document source par défaut")
        print("3. Marquer comme 'orphelins' pour investigation manuelle")
        
        # Pour ce script automatique, on va juste les identifier
        print(f"\n⚠️ {len(problematic_exercises)} exercices nécessitent une attention manuelle")
        
        # Sauvegarder les IDs des exercices problématiques pour référence
        problematic_ids = [str(item['exercise']['_id']) for item in problematic_exercises]
        print(f"IDs des exercices problématiques: {problematic_ids}")
    
    else:
        print(f"\n✅ Aucun exercice problématique trouvé !")
    
    client.close()
    print(f"\n=== FIN D'ANALYSE ===")

if __name__ == "__main__":
    find_and_fix_problematic_exercises()
