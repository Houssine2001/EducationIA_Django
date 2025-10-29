"""
Commande de gestion pour nettoyer les profils utilisateur dupliqués.
Garde uniquement le profil le plus récent pour chaque utilisateur.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from backend.mongodb_utils import get_mongodb_client
from pymongo import MongoClient


class Command(BaseCommand):
    help = 'Nettoie les profils utilisateur dupliqués (garde le plus récent)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔍 Recherche des profils dupliqués via MongoDB...'))
        
        # Connexion MongoDB directe
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        profiles_collection = db['evaluation_userprofile']
        
        duplicates_count = 0
        profiles_deleted = 0
        users_checked = 0
        
        # Parcourir tous les utilisateurs
        for user in User.objects.all():
            users_checked += 1
            
            # Récupérer tous les profils de cet utilisateur via PyMongo, triés par date de création (plus récent en premier)
            profiles = list(profiles_collection.find({'user_id': user.id}).sort('created_at', -1))
            
            if len(profiles) > 1:
                duplicates_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  👤 Utilisateur: {user.username} - {len(profiles)} profils trouvés'
                    )
                )
                
                # Garder le premier (le plus récent)
                profile_to_keep = profiles[0]
                self.stdout.write(
                    self.style.SUCCESS(
                        f'    ✅ Profil à garder: _id={profile_to_keep["_id"]}, créé le {profile_to_keep.get("created_at", "N/A")}'
                    )
                )
                
                # Supprimer tous les autres
                for old_profile in profiles[1:]:
                    self.stdout.write(
                        self.style.WARNING(
                            f'    🗑️  Suppression: _id={old_profile["_id"]}, créé le {old_profile.get("created_at", "N/A")}'
                        )
                    )
                    profiles_collection.delete_one({'_id': old_profile['_id']})
                    profiles_deleted += 1
        
        client.close()
        
        # Résumé
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ NETTOYAGE TERMINÉ'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'  • Utilisateurs vérifiés: {users_checked}')
        self.stdout.write(f'  • Utilisateurs avec duplicatas: {duplicates_count}')
        self.stdout.write(f'  • Profils supprimés: {profiles_deleted}')
        self.stdout.write('')
        
        if profiles_deleted > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '✨ Les profils dupliqués ont été supprimés. Le plus récent a été conservé pour chaque utilisateur.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '✨ Aucun doublon trouvé. Tous les profils sont uniques.'
                )
            )
