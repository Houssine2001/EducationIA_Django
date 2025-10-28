"""
Script pour ajouter des IDs auto-incrémentés aux resources MongoDB qui n'en ont pas
"""
import os
import sys
import django

# Ajouter le répertoire parent au PATH Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation_project.settings')
django.setup()

from resources.models import Resource

def fix_resource_ids():
    """Ajoute des IDs aux resources qui n'en ont pas"""
    resources_without_id = Resource.objects.filter(id__isnull=True)
    count = resources_without_id.count()
    
    if count == 0:
        print("✅ Toutes les resources ont déjà un ID")
        return
    
    print(f"🔧 {count} resources sans ID trouvées")
    
    # Trouver le max ID actuel
    max_id_resource = Resource.objects.filter(id__isnull=False).order_by('-id').first()
    next_id = (max_id_resource.id + 1) if max_id_resource else 1
    
    print(f"📝 Début de l'attribution d'IDs à partir de {next_id}")
    
    fixed = 0
    for resource in resources_without_id:
        try:
            resource.id = next_id
            resource.save()
            print(f"  ✓ Resource '{resource.title}' -> ID {next_id}")
            next_id += 1
            fixed += 1
        except Exception as e:
            print(f"  ✗ Erreur pour '{resource.title}': {e}")
    
    print(f"\n✅ {fixed}/{count} resources corrigées")

if __name__ == '__main__':
    fix_resource_ids()