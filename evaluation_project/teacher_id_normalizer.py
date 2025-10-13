"""
Système de normalisation automatique des teacher_id pour éviter les problèmes futurs
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

class TeacherIdNormalizer:
    """
    Système de normalisation automatique des teacher_id
    """
    
    def __init__(self):
        self.client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.db = self.client[settings.MONGO_DB_NAME]
    
    def auto_normalize_all(self):
        """
        Normalise automatiquement tous les teacher_id en strings vers integers
        """
        print("🔧 NORMALISATION AUTOMATIQUE EN COURS...")
        
        collections_to_normalize = [
            'course_documents',
            'generated_tests', 
            'exercise_sets'
        ]
        
        total_fixed = 0
        
        for collection_name in collections_to_normalize:
            collection = self.db[collection_name]
            
            # Trouver tous les documents avec teacher_id string
            docs_with_string_id = list(collection.find({'teacher_id': {'$type': 'string'}}))
            
            if docs_with_string_id:
                print(f"   📄 {collection_name}: {len(docs_with_string_id)} documents à normaliser")
                
                for doc in docs_with_string_id:
                    old_teacher_id = doc['teacher_id']
                    try:
                        new_teacher_id = int(old_teacher_id)
                        collection.update_one(
                            {'_id': doc['_id']},
                            {'$set': {'teacher_id': new_teacher_id}}
                        )
                        total_fixed += 1
                        print(f"      ✅ {doc['_id']}: '{old_teacher_id}' → {new_teacher_id}")
                    except ValueError:
                        print(f"      ❌ {doc['_id']}: Cannot convert '{old_teacher_id}' to int")
            else:
                print(f"   ✅ {collection_name}: Déjà normalisé")
        
        print(f"🎉 NORMALISATION TERMINÉE: {total_fixed} documents corrigés")
        return total_fixed
    
    def check_and_fix_if_needed(self):
        """
        Vérifie s'il y a des teacher_id string et les corrige automatiquement
        """
        # Vérifier s'il y a des problèmes
        string_docs = self.db.course_documents.count_documents({'teacher_id': {'$type': 'string'}})
        string_tests = self.db.generated_tests.count_documents({'teacher_id': {'$type': 'string'}})
        string_sets = self.db.exercise_sets.count_documents({'teacher_id': {'$type': 'string'}})
        
        total_problems = string_docs + string_tests + string_sets
        
        if total_problems > 0:
            print(f"⚠️ PROBLÈMES DÉTECTÉS: {total_problems} documents avec teacher_id string")
            return self.auto_normalize_all()
        else:
            print("✅ AUCUN PROBLÈME DÉTECTÉ: Tous les teacher_id sont en integer")
            return 0
    
    def get_dashboard_stats(self, user_id):
        """
        Récupère les statistiques dashboard avec normalisation automatique
        """
        # D'abord, normaliser si nécessaire
        self.check_and_fix_if_needed()
        
        # Ensuite, récupérer les vraies statistiques
        teacher_document_ids = [doc['_id'] for doc in self.db.course_documents.find({'teacher_id': user_id})]
        
        total_documents = len(teacher_document_ids)
        total_exercises = self.db.generated_exercises.count_documents({'source_document_id': {'$in': teacher_document_ids}})
        total_tests = self.db.generated_tests.count_documents({'teacher_id': user_id})
        total_sets = self.db.exercise_sets.count_documents({'teacher_id': user_id})
        
        return {
            'total_documents': total_documents,
            'total_exercises': total_exercises,
            'total_tests': total_tests,
            'total_sets': total_sets,
            'teacher_document_ids': teacher_document_ids
        }
    
    def close(self):
        """Fermer la connexion MongoDB"""
        self.client.close()

# Fonction utilitaire pour les vues
def get_normalized_dashboard_stats(user_id):
    """
    Fonction pratique pour récupérer les stats dashboard avec normalisation auto
    """
    normalizer = TeacherIdNormalizer()
    try:
        stats = normalizer.get_dashboard_stats(user_id)
        return stats
    finally:
        normalizer.close()

if __name__ == "__main__":
    # Test du système
    normalizer = TeacherIdNormalizer()
    try:
        fixed = normalizer.check_and_fix_if_needed()
        
        # Test des stats pour user 32
        stats = normalizer.get_dashboard_stats(32)
        print(f"\n📊 STATISTIQUES FINALES POUR USER 32:")
        print(f"   📄 Documents: {stats['total_documents']}")
        print(f"   ✏️ Exercices: {stats['total_exercises']}")
        print(f"   📝 Tests: {stats['total_tests']}")
        print(f"   📦 Sets: {stats['total_sets']}")
        
    finally:
        normalizer.close()
