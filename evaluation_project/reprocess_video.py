#!/usr/bin/env python
"""Script pour relancer le traitement d'une vidéo bloquée"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from resources.models import Resource
from resources.views import process_resource_ai
import threading

# ID de la ressource à retraiter
RESOURCE_ID = 4

if __name__ == '__main__':
    try:
        resource = Resource.objects.get(id=RESOURCE_ID)
        print(f"📹 Ressource trouvée: ID={resource.id}, Title='{resource.title}', Status={resource.processing_status}")
        
        # Réinitialiser le statut
        resource.processing_status = 'pending'
        resource.error_message = ''
        resource.save(update_fields=['processing_status', 'error_message'])
        print(f"✅ Statut réinitialisé à 'pending'")
        
        # Lancer le traitement
        print(f"🚀 Lancement du thread de traitement IA...")
        thread = threading.Thread(target=process_resource_ai, args=(RESOURCE_ID,))
        thread.daemon = False  # Non-daemon pour que le script attende
        thread.start()
        
        print(f"⏳ Traitement en cours... (peut prendre quelques minutes)")
        thread.join()  # Attendre la fin du traitement
        
        # Vérifier le résultat
        resource.refresh_from_db()
        print(f"\n📊 Résultat final:")
        print(f"   - Status: {resource.processing_status}")
        print(f"   - Summary length: {len(resource.summary) if resource.summary else 0} chars")
        if resource.error_message:
            print(f"   - Error: {resource.error_message}")
        else:
            print(f"   ✅ Traitement réussi!")
            
    except Resource.DoesNotExist:
        print(f"❌ Ressource {RESOURCE_ID} introuvable")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()