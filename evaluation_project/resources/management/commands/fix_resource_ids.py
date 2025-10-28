"""
Management command pour ajouter des IDs aux resources qui n'en ont pas
Usage: python manage.py fix_resource_ids
"""
from django.core.management.base import BaseCommand
from resources.models import Resource


class Command(BaseCommand):
    help = 'Ajoute des IDs auto-incrémentés aux resources MongoDB qui n\'en ont pas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔍 Recherche des resources sans ID...'))
        
        # Trouver les resources sans ID
        resources_without_id = Resource.objects.filter(id__isnull=True)
        count = resources_without_id.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Toutes les resources ont déjà un ID'))
            return
        
        self.stdout.write(self.style.WARNING(f'🔧 {count} resources sans ID trouvées'))
        
        # Trouver le max ID actuel
        max_id_resource = Resource.objects.filter(id__isnull=False).order_by('-id').first()
        next_id = (max_id_resource.id + 1) if max_id_resource else 1
        
        self.stdout.write(self.style.WARNING(f'📝 Début de l\'attribution d\'IDs à partir de {next_id}'))
        
        fixed = 0
        errors = 0
        
        for resource in resources_without_id:
            try:
                # Utiliser directement MongoDB pour mettre à jour le champ id
                from pymongo import MongoClient
                from django.conf import settings
                
                client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
                db = client[settings.MONGO_DB_NAME]
                
                # Mettre à jour directement dans MongoDB
                result = db.resources_resource.update_one(
                    {'_id': resource._id},
                    {'$set': {'id': next_id}}
                )
                
                if result.modified_count > 0:
                    self.stdout.write(f"  ✓ Resource '{resource.title[:50]}' -> ID {next_id}")
                    next_id += 1
                    fixed += 1
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ Échec de mise à jour pour '{resource.title[:50]}'"))
                    errors += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Erreur pour '{resource.title[:50]}': {e}"))
                errors += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {fixed}/{count} resources corrigées'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'❌ {errors} erreurs'))
        
        # Vérifier le résultat
        remaining = Resource.objects.filter(id__isnull=True).count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS('🎉 Toutes les resources ont maintenant un ID !'))
        else:
            self.stdout.write(self.style.ERROR(f'⚠️ {remaining} resources restent sans ID'))
