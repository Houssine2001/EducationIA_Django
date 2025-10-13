"""
Diagnostic spécifique pour les Exercise Sets non visibles
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

def diagnostic_exercise_sets():
    print("=== DIAGNOSTIC EXERCISE SETS ===")
    
    # Connexion MongoDB
    client = MongoClient('localhost', 27017)
    db = client['django_education']
    
    user_id = 32  # User principal
    
    print(f"🔍 USER ID: {user_id}")
    
    # 1. Vérifier tous les sets de l'utilisateur
    all_sets = list(db.exercise_sets.find({'teacher_id': user_id}).sort('created_at', -1))
    print(f"📦 TOTAL sets pour user {user_id}: {len(all_sets)}")
    
    # 2. Afficher tous les sets pour voir la structure
    print(f"\n📦 TOUS LES EXERCISE SETS:")
    for i, ex_set in enumerate(all_sets):
        print(f"   {i+1}. [{ex_set['_id']}] {ex_set.get('title', 'N/A')}")
        print(f"      Teacher ID: {ex_set.get('teacher_id')} ({type(ex_set.get('teacher_id')).__name__})")
        print(f"      Status: {ex_set.get('status', 'N/A')}")
        print(f"      Created: {ex_set.get('created_at', 'N/A')}")
        print(f"      Source Doc: {ex_set.get('source_document_id', 'N/A')}")
        print()
    
    # 3. Chercher spécifiquement le set mentionné par l'utilisateur
    specific_set_id = "68ed2452d6bd84710c795d92"
    print(f"🎯 RECHERCHE DU SET SPÉCIFIQUE: {specific_set_id}")
    
    try:
        from bson import ObjectId
        specific_set = db.exercise_sets.find_one({'_id': ObjectId(specific_set_id)})
        
        if specific_set:
            print(f"   ✅ SET TROUVÉ:")
            print(f"      ID: {specific_set['_id']}")
            print(f"      Title: {specific_set.get('title', 'N/A')}")
            print(f"      Teacher ID: {specific_set.get('teacher_id')} ({type(specific_set.get('teacher_id')).__name__})")
            print(f"      Status: {specific_set.get('status', 'N/A')}")
            print(f"      Created: {specific_set.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ SET NON TROUVÉ avec cet ID")
    except Exception as e:
        print(f"   ❌ Erreur lors de la recherche: {e}")
    
    # 4. Tester la requête exacte de la vue exercise_sets_list
    print(f"\n🎯 TEST REQUÊTE EXERCISE_SETS_LIST:")
    sets_data = list(db.exercise_sets.find({'teacher_id': user_id}).sort('created_at', -1))
    
    print(f"   Requête: db.exercise_sets.find({{'teacher_id': {user_id}}}).sort('created_at', -1)")
    print(f"   Trouvé: {len(sets_data)} sets")
    
    for i, ex_set in enumerate(sets_data):
        print(f"   {i+1}. [{ex_set['_id']}] {ex_set.get('title', 'N/A')} - Status: {ex_set.get('status', 'N/A')}")
    
    # 5. Vérifier les types de données
    print(f"\n🔍 TYPES DE DONNÉES (premier set):")
    if all_sets:
        first_set = all_sets[0]
        for key, value in first_set.items():
            print(f"   {key}: {type(value).__name__} = {value}")
    
    # 6. Vérifier s'il y a des sets avec des teacher_id différents
    print(f"\n👥 RÉPARTITION PAR TEACHER_ID (SETS):")
    pipeline = [
        {"$group": {"_id": "$teacher_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    teacher_groups = list(db.exercise_sets.aggregate(pipeline))
    
    for group in teacher_groups:
        teacher_id_val = group['_id']
        count = group['count']
        print(f"   Teacher ID {teacher_id_val} ({type(teacher_id_val).__name__}): {count} sets")
    
    client.close()
    print(f"\n=== FIN DIAGNOSTIC SETS ===")

if __name__ == "__main__":
    diagnostic_exercise_sets()
