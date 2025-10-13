"""
Script pour nettoyer les exercices orphelins (sans document source valide)
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

def clean_orphaned_exercises():
    print("=== NETTOYAGE DES EXERCICES ORPHELINS ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    # IDs des exercices problématiques identifiés
    problematic_ids = [
        '68ed2411d6bd84710c795d79',
        '68ed2411d6bd84710c795d7d', 
        '68ed2411d6bd84710c795d7f',
        '68ed2411d6bd84710c795d81',
        '68ed2411d6bd84710c795d83'
    ]
    
    print(f"Exercices à supprimer: {len(problematic_ids)}")
    
    # Convertir en ObjectId
    object_ids = []
    for pid in problematic_ids:
        try:
            object_ids.append(ObjectId(pid))
        except:
            print(f"⚠️ ID invalide: {pid}")
    
    if not object_ids:
        print("❌ Aucun ID valide à traiter")
        return
    
    # 1. Afficher les exercices avant suppression
    print(f"\n1. EXERCICES À SUPPRIMER:")
    exercises_to_delete = list(db.generated_exercises.find({'_id': {'$in': object_ids}}))
    
    for i, ex in enumerate(exercises_to_delete):
        print(f"  {i+1}. {ex['_id']} - {ex.get('question_text', 'N/A')[:50]}...")
    
    # 2. Supprimer les relations ManyToMany d'abord
    print(f"\n2. SUPPRESSION DES RELATIONS MANYTOMANY")
    string_ids = [str(oid) for oid in object_ids]
    
    relations_deleted = db.exercise_generator_exerciseset_exercises.delete_many({
        'generatedexercise_id': {'$in': string_ids}
    })
    print(f"Relations supprimées: {relations_deleted.deleted_count}")
    
    # 3. Supprimer les exercices
    print(f"\n3. SUPPRESSION DES EXERCICES")
    result = db.generated_exercises.delete_many({'_id': {'$in': object_ids}})
    print(f"Exercices supprimés: {result.deleted_count}")
    
    # 4. Vérification finale
    print(f"\n4. VÉRIFICATION FINALE")
    remaining = db.generated_exercises.count_documents({'_id': {'$in': object_ids}})
    if remaining == 0:
        print("✅ Tous les exercices orphelins ont été supprimés avec succès")
    else:
        print(f"⚠️ {remaining} exercices n'ont pas pu être supprimés")
    
    # 5. Statistiques finales
    total_exercises = db.generated_exercises.count_documents({})
    print(f"\nNombre total d'exercices restants: {total_exercises}")
    
    client.close()
    print(f"\n=== NETTOYAGE TERMINÉ ===")

if __name__ == "__main__":
    clean_orphaned_exercises()
