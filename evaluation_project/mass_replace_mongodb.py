"""
Script pour remplacer automatiquement toutes les occurrences de 
MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
par 
get_mongodb_client()

Usage: python mass_replace_mongodb.py
"""

import os
import re

# Fichiers à modifier
FILES_TO_FIX = [
    'evaluation/views.py',
    'exercise_generator/views.py',
    'exercise_generator/services.py',
    'exercise_generator/models.py',
    'analytics_dashboard/views.py',
    'analytics_dashboard/signals.py',
    'analytics_dashboard/management/commands/sync_gamification.py',
    'evaluation/management/commands/cleanup_duplicate_profiles.py',
    'exercise_generator/management/commands/test_set_detail.py',
    'exercise_generator/management/commands/check_submissions.py',
    'teacher_id_normalizer.py',
    'quick_diag.py',
    'diagnostic_submissions.py',
    'debug_manual_tests.py',
    'check_documents.py',
    'test_process_document.py',
    'test_final_generation.py',
    'test_exercise_generation.py',
    'test_concept_analysis.py',
]

# Pattern de remplacement
OLD_PATTERN = r'MongoClient\(settings\.MONGO_HOST,\s*settings\.MONGO_PORT\)'
NEW_REPLACEMENT = 'get_mongodb_client()'

def fix_file(filepath):
    """Remplacer les occurrences dans un fichier"""
    print(f"\n📄 Traitement: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ⚠️  Fichier non trouvé: {filepath}")
        return 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si l'import existe déjà
    has_import = 'from backend.mongodb_utils import get_mongodb_client' in content
    
    # Compter les occurrences
    count = len(re.findall(OLD_PATTERN, content))
    
    if count == 0:
        print(f"  ✅ Aucune occurrence trouvée")
        return 0
    
    # Remplacer
    new_content = re.sub(OLD_PATTERN, NEW_REPLACEMENT, content)
    
    # Ajouter l'import si nécessaire
    if not has_import:
        # Trouver la ligne d'imports Django
        import_line = None
        lines = new_content.split('\n')
        
        for i, line in enumerate(lines):
            if 'from django.conf import settings' in line:
                import_line = i
                break
            elif 'import django' in line:
                import_line = i
                break
        
        if import_line is not None:
            # Insérer l'import après les imports Django
            lines.insert(import_line + 1, 'from backend.mongodb_utils import get_mongodb_client')
            new_content = '\n'.join(lines)
            print(f"  📌 Import ajouté")
    
    # Sauvegarder
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ {count} occurrence(s) remplacée(s)")
    return count

def main():
    print("🚀 Démarrage du remplacement automatique MongoDB")
    print("=" * 60)
    
    total_fixes = 0
    
    for filepath in FILES_TO_FIX:
        count = fix_file(filepath)
        total_fixes += count
    
    print("\n" + "=" * 60)
    print(f"✅ Terminé ! {total_fixes} occurrence(s) remplacée(s) au total")
    print("\n📝 N'oubliez pas de:")
    print("  1. Vérifier les changements: git diff")
    print("  2. Tester localement")
    print("  3. Commiter: git add -A && git commit -m 'Fix: Complete MongoDB connection refactoring'")
    print("  4. Pusher: git push origin DockerAzureAll")

if __name__ == '__main__':
    main()
