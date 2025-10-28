"""
Management command pour retraiter les resources en attente
Usage: python manage.py process_pending_resources
"""
from django.core.management.base import BaseCommand
from resources.models import Resource
from resources.views import process_resource_ai
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Traite les resources en attente avec l\'IA'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔍 Recherche des resources en attente...'))
        
        # Trouver les resources en pending
        pending_resources = Resource.objects.filter(processing_status='pending')
        count = pending_resources.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Aucune resource en attente'))
            return
        
        self.stdout.write(self.style.WARNING(f'🔧 {count} resources en attente trouvées'))
        
        processed = 0
        errors = 0
        
        for resource in pending_resources:
            if not resource.id:
                self.stdout.write(self.style.ERROR(f"  ✗ Resource '{resource.title[:50]}' n'a pas d'ID"))
                errors += 1
                continue
                
            try:
                self.stdout.write(f"  ⚙️  Traitement de '{resource.title[:50]}'...")
                process_resource_ai(resource.id)
                self.stdout.write(self.style.SUCCESS(f"  ✓ '{resource.title[:50]}' traité"))
                processed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Erreur pour '{resource.title[:50]}': {e}"))
                errors += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {processed}/{count} resources traitées'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'❌ {errors} erreurs'))