"""
Vérifier les documents existants et nettoyer les documents de test
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]

print("\n=== DOCUMENTS DE COURS ===\n")
docs = list(db.course_documents.find().sort('created_at', -1))
print(f"Total: {len(docs)} documents\n")

for doc in docs:
    print(f"ID: {doc['_id']}")
    print(f"  Titre: {doc.get('title', 'Sans titre')}")
    print(f"  Sujet: {doc.get('subject', 'N/A')}")
    print(f"  Statut: {doc.get('processing_status', 'N/A')}")
    print(f"  Créé: {doc.get('created_at', 'N/A')}")
    
    # Compter les exercices
    ex_count = db.generated_exercises.count_documents({'source_document_id': doc['_id']})
    print(f"  Exercices: {ex_count}")
    print()

print("\n=== EXERCICES GÉNÉRÉS ===\n")
exercises = list(db.generated_exercises.find().sort('created_at', -1).limit(10))
print(f"Total: {db.generated_exercises.count_documents({})} exercices")
print(f"Affichage: {len(exercises)} derniers\n")

for ex in exercises:
    print(f"ID: {ex['_id']}")
    print(f"  Type: {ex.get('exercise_type', 'N/A')}")
    print(f"  Question: {ex.get('question_text', 'N/A')[:60]}...")
    print(f"  Document source: {ex.get('source_document_id', 'N/A')}")
    print()
