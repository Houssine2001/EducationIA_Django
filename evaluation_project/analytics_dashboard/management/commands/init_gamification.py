"""
Commande Django pour initialiser le système de gamification
Usage: python manage.py init_gamification
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_dashboard.services import BadgeService, CompetitionService
from analytics_dashboard.models import StudentProfile, Competition


class Command(BaseCommand):
    help = 'Initialise le système de gamification'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎮 Initialisation du système de gamification...'))
        
        # 1. Initialiser les badges
        self.stdout.write('📛 Création des badges...')
        badge_service = BadgeService()
        badges = badge_service.initialize_badges()
        self.stdout.write(self.style.SUCCESS(f'✅ {len(badges)} badges créés'))
        
        # 2. Créer les profils gamifiés pour tous les étudiants
        self.stdout.write('👥 Création des profils gamifiés...')
        students = User.objects.filter(is_staff=False)
        profiles_created = 0
        
        for student in students:
            profile, created = StudentProfile.objects.get_or_create(user=student)
            if created:
                profiles_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {profiles_created} nouveaux profils créés'))
        
        # 3. Créer les compétitions initiales
        self.stdout.write('🏆 Création des compétitions...')
        comp_service = CompetitionService()
        
        try:
            daily_comp = comp_service.create_daily_competition()
            self.stdout.write(self.style.SUCCESS(f'✅ Compétition quotidienne créée: {daily_comp.title}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Compétition quotidienne: {str(e)}'))
        
        try:
            weekly_comp = comp_service.create_weekly_competition()
            self.stdout.write(self.style.SUCCESS(f'✅ Compétition hebdomadaire créée: {weekly_comp.title}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Compétition hebdomadaire: {str(e)}'))
        
        # 4. Statistiques finales
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Initialisation terminée !'))
        self.stdout.write(f'📊 Statistiques:')
        self.stdout.write(f'   - Badges disponibles: {len(badges)}')
        self.stdout.write(f'   - Profils gamifiés: {StudentProfile.objects.count()}')
        self.stdout.write(f'   - Compétitions actives: {Competition.objects.filter(status="ACTIVE").count()}')
        self.stdout.write('='*50)
