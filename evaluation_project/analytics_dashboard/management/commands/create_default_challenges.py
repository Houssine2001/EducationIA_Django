from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from analytics_dashboard.models import Challenge
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Créer des défis par défaut pour la gamification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Nom d\'utilisateur pour créer les défis (optionnel)',
        )

    def handle(self, *args, **options):
        # Supprimer les anciens défis expirés
        Challenge.objects.filter(expires_at__lt=timezone.now()).delete()
        
        # Si un utilisateur est spécifié, créer des défis pour lui
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                self.create_challenges_for_user(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur "{options["user"]}" introuvable')
                )
                return
        else:
            # Créer des défis pour tous les étudiants avec "etudiant" dans le nom
            students = User.objects.filter(
                username__icontains='etudiant'
            )
            
            if not students.exists():
                # Fallback sur les utilisateurs non-staff
                students = User.objects.filter(is_staff=False)
            
            for student in students:
                self.create_challenges_for_user(student)
        
        self.stdout.write(self.style.SUCCESS('🎯 Défis créés avec succès!'))

    def create_challenges_for_user(self, user):
        """Créer des défis pour un utilisateur spécifique"""
        
        # Défi 1: Progresser en Physique (facile)
        challenge1, created = Challenge.objects.get_or_create(
            student=user,
            title="Progresser en Physique",
            defaults={
                'description': "Améliorer votre score de 10% en Physique",
                'target_data': {
                    'subject': 'Physique',
                    'target_value': 5,
                    'score_improvement': 10
                },
                'xp_reward': 100,
                'coins_reward': 50,
                'badge_reward': "En Progression",
                'difficulty': 'MEDIUM',
                'status': 'ACTIVE',
                'current_progress': 0,
                'created_at': timezone.now(),
                'expires_at': timezone.now() + timedelta(days=30),
                'tips': [
                    "Commencez par des exercices de base en mécanique",
                    "Révisez les formules avant de faire les exercices",
                    "Prenez votre temps pour comprendre chaque concept"
                ]
            }
        )
        
        if created:
            self.stdout.write(f"✅ Créé pour {user.username}: {challenge1.title}")
        else:
            self.stdout.write(f"⏭️ Existe déjà pour {user.username}: {challenge1.title}")
        
        # Défi 2: Maîtriser la Biologie (difficile)
        challenge2, created = Challenge.objects.get_or_create(
            student=user,
            title="Défi Biologie",
            defaults={
                'description': "Surmonter vos difficultés en Biologie",
                'target_data': {
                    'subject': 'Biologie',
                    'target_value': 8,
                    'score_improvement': 15
                },
                'xp_reward': 200,
                'coins_reward': 100,
                'badge_reward': "Persévérant",
                'difficulty': 'HARD',
                'status': 'ACTIVE',
                'current_progress': 0,
                'created_at': timezone.now(),
                'expires_at': timezone.now() + timedelta(days=30),
                'tips': [
                    "Concentrez-vous sur la génétique et l'évolution",
                    "Utilisez des schémas pour mémoriser",
                    "Faites des liens entre les différents concepts"
                ]
            }
        )
        
        if created:
            self.stdout.write(f"✅ Créé pour {user.username}: {challenge2.title}")
        else:
            self.stdout.write(f"⏭️ Existe déjà pour {user.username}: {challenge2.title}")
        
        # Défi 3: Explorer les Mathématiques (facile)
        challenge3, created = Challenge.objects.get_or_create(
            student=user,
            title="Explorer les Mathématiques",
            defaults={
                'description': "Découvrir de nouveaux concepts mathématiques",
                'target_data': {
                    'subject': 'Mathématiques',
                    'target_value': 3,
                    'score_improvement': 5
                },
                'xp_reward': 75,
                'coins_reward': 30,
                'badge_reward': "Explorateur",
                'difficulty': 'EASY',
                'status': 'ACTIVE',
                'current_progress': 0,
                'created_at': timezone.now(),
                'expires_at': timezone.now() + timedelta(days=30),
                'tips': [
                    "Commencez par les exercices les plus simples",
                    "Vérifiez vos calculs à chaque étape",
                    "N'hésitez pas à refaire les exercices ratés"
                ]
            }
        )
        
        if created:
            self.stdout.write(f"✅ Créé pour {user.username}: {challenge3.title}")
        else:
            self.stdout.write(f"⏭️ Existe déjà pour {user.username}: {challenge3.title}")