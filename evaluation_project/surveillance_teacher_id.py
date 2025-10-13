"""
🔄 SURVEILLANCE CONTINUE DES TEACHER_ID
Script à exécuter périodiquement pour maintenir la cohérence des données
"""
import os
import sys
import django
import time
from datetime import datetime

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from teacher_id_normalizer import TeacherIdNormalizer

def surveillance_continue():
    """
    Surveillance continue des teacher_id avec correction automatique
    """
    print("🔄 SURVEILLANCE TEACHER_ID DÉMARRÉE")
    print(f"⏰ Heure de démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    normalizer = TeacherIdNormalizer()
    
    try:
        while True:
            print(f"\n🔍 VÉRIFICATION - {datetime.now().strftime('%H:%M:%S')}")
            
            # Vérifier et corriger si nécessaire
            fixed = normalizer.check_and_fix_if_needed()
            
            if fixed > 0:
                print(f"🎉 {fixed} problèmes corrigés automatiquement!")
                
                # Afficher les stats actuelles
                stats = normalizer.get_dashboard_stats(32)  # User principal
                print(f"📊 Stats actuelles (User 32):")
                print(f"   📄 Documents: {stats['total_documents']}")
                print(f"   ✏️ Exercices: {stats['total_exercises']}")
                print(f"   📦 Sets: {stats['total_sets']}")
            
            # Attendre 30 secondes avant la prochaine vérification
            print("⏳ Prochaine vérification dans 30 secondes...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ SURVEILLANCE ARRÊTÉE - {datetime.now().strftime('%H:%M:%S')}")
    finally:
        normalizer.close()

def verification_unique():
    """
    Vérification unique (sans boucle) pour les tests
    """
    print("🔍 VÉRIFICATION UNIQUE DES TEACHER_ID")
    
    normalizer = TeacherIdNormalizer()
    
    try:
        # Vérifier et corriger
        fixed = normalizer.check_and_fix_if_needed()
        
        if fixed > 0:
            print(f"🎉 {fixed} problèmes corrigés!")
        
        # Afficher les stats finales
        stats = normalizer.get_dashboard_stats(32)
        print(f"\n📊 STATS FINALES (User 32):")
        print(f"   📄 Documents: {stats['total_documents']}")
        print(f"   ✏️ Exercices: {stats['total_exercises']}")
        print(f"   📝 Tests: {stats['total_tests']}")
        print(f"   📦 Sets: {stats['total_sets']}")
        
        return stats
        
    finally:
        normalizer.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continue":
        # Mode surveillance continue
        surveillance_continue()
    else:
        # Mode vérification unique
        verification_unique()
