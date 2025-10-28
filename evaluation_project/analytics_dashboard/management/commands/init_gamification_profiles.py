"""
Commande pour initialiser les champs de gamification des profils existants
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evaluation.models import UserProfile
from analytics_dashboard.models import Challenge
from analytics_dashboard.services import ChallengeService
from django.utils import timezone


class Command(BaseCommand):
    help = 'Initialize gamification fields for all user profiles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🎮 INITIALISATION DE LA GAMIFICATION'))
        self.stdout.write('=' * 70)
        
        # Récupérer tous les utilisateurs non-staff
        all_users = list(User.objects.all())
        users = [u for u in all_users if not u.is_staff]
        
        self.stdout.write(f'📊 {len(users)} étudiant(s) à initialiser\n')
        
        profiles_updated = 0
        challenges_created = 0
        
        for user in users:
            self.stdout.write(f'\n👤 {user.username}...')
            
            # Récupérer ou créer le profil
            profile = UserProfile.objects.filter(user=user).order_by('-created_at').first()
            
            if not profile:
                profile = UserProfile.objects.create(
                    user=user,
                    role='student',
                    level=1,
                    total_xp=0
                )
                self.stdout.write('   ✅ Nouveau profil créé')
            
            # Initialiser les champs de gamification s'ils sont None
            updated = False
            
            if profile.level is None:
                profile.level = 1
                updated = True
                self.stdout.write('   📈 Level initialisé à 1')
            
            if profile.total_xp is None:
                profile.total_xp = 0
                updated = True
                self.stdout.write('   💫 XP initialisé à 0')
            
            if profile.badges is None:
                profile.badges = []
                updated = True
                self.stdout.write('   🎖️ Badges initialisés')
            
            if updated:
                profile.save()
                profiles_updated += 1
                self.stdout.write(self.style.SUCCESS('   ✅ Profil mis à jour'))
            else:
                self.stdout.write('   ⏭️ Profil déjà initialisé')
            
            # Vérifier les défis
            active_challenges = Challenge.objects.filter(
                student=user,
                status='ACTIVE',
                expires_at__gte=timezone.now()
            )
            
            if active_challenges.count() == 0:
                try:
                    challenge_service = ChallengeService()
                    new_challenges = challenge_service.generate_daily_challenges(user)
                    challenges_created += len(new_challenges)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   🎯 {len(new_challenges)} défi(s) créé(s)'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'   ⚠️ Erreur création défis: {e}'
                        )
                    )
            else:
                self.stdout.write(f'   🎯 {active_challenges.count()} défi(s) actif(s)')
        
        # Résumé
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ INITIALISATION TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'  • Étudiants traités: {len(users)}')
        self.stdout.write(f'  • Profils mis à jour: {profiles_updated}')
        self.stdout.write(f'  • Défis créés: {challenges_created}')
        self.stdout.write('')
