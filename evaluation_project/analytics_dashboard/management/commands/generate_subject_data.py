from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_dashboard.subject_services import SubjectAnalyticsService

class Command(BaseCommand):
    help = 'Génère des données de test pour les analytics par matière'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Nombre d\'utilisateurs à traiter'
        )

    def handle(self, *args, **options):
        service = SubjectAnalyticsService()
        users = User.objects.all()[:options['users']]
        
        self.stdout.write(
            self.style.SUCCESS(f'Génération des données pour {len(users)} utilisateurs...')
        )
        
        for user in users:
            self.stdout.write(f'Traitement de {user.username}...')
            
            for subject in service.subjects:
                analytics = service.create_or_update_subject_analytics(user, subject)
                self.stdout.write(
                    f'  ✅ {subject}: {analytics.total_visits} visites, '
                    f'{analytics.tests_taken} tests, '
                    f'prédiction: {analytics.predicted_success_probability:.2f}'
                )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Génération terminée avec succès!')
        )