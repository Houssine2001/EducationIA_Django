from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_dashboard.models import StudentAnalytics, PerformanceTrend
from analytics_dashboard.services import AnalyticsService, PredictionService
from django.utils import timezone
from datetime import timedelta
import random
import math


class Command(BaseCommand):
    help = 'Génère des données de test pour démontrer les prédictions IA réelles'

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=5, help='Nombre d\'étudiants à créer')

    def handle(self, *args, **options):
        num_students = options['students']
        
        self.stdout.write(f'Génération de données de test pour {num_students} étudiants...')
        
        # Créer des étudiants de test
        students = []
        for i in range(num_students):
            username = f'etudiant{i+1}'
            try:
                student = User.objects.get(username=username)
            except User.DoesNotExist:
                student = User.objects.create_user(
                    username=username,
                    first_name=f'Étudiant',
                    last_name=f'{i+1}',
                    email=f'etudiant{i+1}@test.com',
                    password='testpass123'
                )
            students.append(student)
        
        # Générer des données pour chaque étudiant
        for student in students:
            self.stdout.write(f'Génération de données pour {student.username}...')
            
            # Générer des performances historiques
            base_performance = random.uniform(40, 95)  # Performance de base
            trend = random.uniform(-10, 15)  # Tendance d'amélioration
            
            for day in range(30):  # 30 jours de données
                date = timezone.now() - timedelta(days=30-day)
                
                # Calculer le score avec tendance et variabilité
                daily_variation = random.uniform(-8, 8)
                score = base_performance + (trend * day / 30) + daily_variation
                score = max(0, min(100, score))  # Limiter entre 0 et 100
                
                # Probabilité de faire un exercice ce jour
                if random.random() < 0.7:  # 70% de chance
                    PerformanceTrend.objects.create(
                        student=student,
                        date=date,
                        score=score,
                        subject='General'
                    )
            
            # Actualiser les analytics
            analytics_service = AnalyticsService()
            analytics_service.update_student_analytics(student)
            
            # Générer des prédictions IA réelles
            prediction_service = PredictionService()
            prediction_service.generate_real_prediction(student)
        
        self.stdout.write(self.style.SUCCESS(f'Données générées avec succès pour {num_students} étudiants!'))