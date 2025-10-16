# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\management\commands\generate_student_evolution_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from analytics_dashboard.models import StudentAnalytics, PerformanceTrend, PredictionModel
from analytics_dashboard.tracking_service import StudentTrackingService

class Command(BaseCommand):
    help = 'Génère des données d\'évolution réalistes pour les étudiants'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=10,
            help='Nombre d\'étudiants à traiter (défaut: 10)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Nombre de jours d\'historique à générer (défaut: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Effacer les données existantes avant génération'
        )

# ...existing code...

    def handle(self, *args, **options):
        students_count = options['students']
        days_count = options['days']
        clear_data = options['clear']
        
        self.stdout.write(self.style.SUCCESS(
            f'Génération de données d\'évolution pour {students_count} étudiants sur {days_count} jours'
        ))
        
        # Nettoyer les données existantes si demandé
        if clear_data:
            self.stdout.write('Nettoyage des données existantes...')
            PerformanceTrend.objects.all().delete()
            StudentAnalytics.objects.all().delete()
            PredictionModel.objects.all().delete()
        
        # Obtenir ou créer des étudiants
        students = self.get_or_create_students(students_count)
        
        # Service de tracking
        tracking_service = StudentTrackingService()
        
        # Sujets et types de tests
        subjects = [
            'Mathématiques', 'Français', 'Anglais', 'Sciences', 
            'Histoire', 'Géographie', 'Informatique', 'Physique'
        ]
        
        test_types = [
            'Quiz', 'Test Pratique', 'Évaluation', 'Exercice', 
            'Contrôle', 'Devoir', 'Examen Blanc'
        ]
        
        # Générer les données pour chaque étudiant
        for student in students:
            self.stdout.write(f'Génération pour {student.username}...')
            
            # Profil d'étudiant (détermine la progression)
            student_profile = self.generate_student_profile()
            
            # Générer l'historique de performance
            self.generate_performance_history(
                student, tracking_service, subjects, test_types, 
                days_count, student_profile
            )
            
            # Générer des visites de cours
            self.generate_course_visits(
                student, tracking_service, subjects, days_count, student_profile
            )
        
        # 🔧 GÉNÉRATION DES PRÉDICTIONS IA APRÈS LES DONNÉES
        self.stdout.write(self.style.SUCCESS('Génération des prédictions IA...'))
        self.create_sample_predictions(students)
        
        self.stdout.write(self.style.SUCCESS(
            f'Données générées avec succès pour {len(students)} étudiants!'
        ))
        
        # Statistiques finales
        total_trends = PerformanceTrend.objects.count()
        total_analytics = StudentAnalytics.objects.count()
        total_predictions = PredictionModel.objects.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'Statistiques: {total_trends} performances, {total_analytics} analytics, {total_predictions} prédictions'
        ))

# ...existing code...
    
    def get_or_create_students(self, count):
        """Obtenir ou créer des étudiants pour les tests"""
        # Éviter la requête NOT qui pose problème avec Djongo
        try:
            students = list(User.objects.exclude(is_staff=True))
        except:
            # Si exclude ne fonctionne pas non plus, utiliser une approche différente
            all_users = list(User.objects.all())
            students = [user for user in all_users if not user.is_staff]
        
        # Créer des étudiants manquants si nécessaire
        while len(students) < count:
            username = f'student_{len(students) + 1}'
            
            # Vérifier que l'utilisateur n'existe pas déjà
            if not User.objects.filter(username=username).exists():
                student = User.objects.create_user(
                    username=username,
                    first_name=f'Étudiant',
                    last_name=f'{len(students) + 1}',
                    email=f'{username}@test.com',
                    password='password123'
                )
                students.append(student)
                
                self.stdout.write(f'Étudiant créé: {username}')
        
        return students[:count]
    
    def generate_student_profile(self):
        """Générer un profil d'étudiant avec des caractéristiques de progression"""
        profiles = [
            {
                'type': 'excellent',
                'base_score': (16, 20),
                'progression': 'stable_high',
                'consistency': 0.9,
                'engagement': 0.9
            },
            {
                'type': 'good',
                'base_score': (12, 16),
                'progression': 'improving',
                'consistency': 0.7,
                'engagement': 0.7
            },
            {
                'type': 'average',
                'base_score': (10, 14),
                'progression': 'stable_medium',
                'consistency': 0.6,
                'engagement': 0.6
            },
            {
                'type': 'struggling',
                'base_score': (6, 12),
                'progression': 'declining',
                'consistency': 0.4,
                'engagement': 0.4
            },
            {
                'type': 'inconsistent',
                'base_score': (8, 16),
                'progression': 'volatile',
                'consistency': 0.3,
                'engagement': 0.5
            }
        ]
        
        return random.choice(profiles)
    
    def generate_performance_history(self, student, tracking_service, subjects, 
                                   test_types, days_count, profile):
        """Générer un historique de performances pour un étudiant"""
        start_date = timezone.now() - timedelta(days=days_count)
        
        # Nombre de tests à générer (1-3 par semaine)
        total_tests = random.randint(days_count // 7, (days_count // 7) * 3)
        
        for i in range(total_tests):
            # Date aléatoire dans la période
            days_offset = random.randint(0, days_count)
            test_date = start_date + timedelta(days=days_offset)
            
            # Choisir une matière et un type de test
            subject = random.choice(subjects)
            test_type = random.choice(test_types)
            test_name = f"{test_type} {subject}"
            
            # Calculer le score basé sur le profil
            score = self.calculate_score(profile, i, total_tests)
            
            # Créer la tendance de performance (sans test_name qui n'existe pas dans le modèle)
            PerformanceTrend.objects.create(
                student=student,
                score=score,
                subject=subject,
                date=test_date
            )
        
        # Mettre à jour les analytics
        tracking_service.analytics_service.update_student_analytics(student)
    
    def calculate_score(self, profile, test_index, total_tests):
        """Calculer un score basé sur le profil et la progression"""
        base_min, base_max = profile['base_score']
        progression = profile['progression']
        consistency = profile['consistency']
        
        # Score de base
        base_score = random.uniform(base_min, base_max)
        
        # Ajustement selon la progression
        progress_factor = test_index / max(total_tests - 1, 1)
        
        if progression == 'improving':
            # Amélioration progressive
            improvement = progress_factor * 4  # Jusqu'à +4 points
            base_score += improvement
        elif progression == 'declining':
            # Dégradation progressive  
            decline = progress_factor * 3  # Jusqu'à -3 points
            base_score -= decline
        elif progression == 'volatile':
            # Variations importantes
            variation = random.uniform(-3, 3)
            base_score += variation
        elif progression == 'stable_high':
            # Stable avec légères variations
            variation = random.uniform(-0.5, 0.5)
            base_score += variation
        elif progression == 'stable_medium':
            # Stable avec variations modérées
            variation = random.uniform(-1, 1)
            base_score += variation
        
        # Ajustement de consistance
        if random.random() > consistency:
            # Score incohérent occasionnel
            inconsistency = random.uniform(-2, 2)
            base_score += inconsistency
        
        # S'assurer que le score reste dans les limites
        return max(0, min(20, round(base_score, 1)))
    
    def generate_course_visits(self, student, tracking_service, subjects, 
                             days_count, profile):
        """Générer des visites de cours pour un étudiant"""
        engagement = profile['engagement']
        
        # Nombre de visites basé sur l'engagement
        visits_per_week = int(engagement * 10)  # 0-10 visites par semaine
        total_visits = (days_count // 7) * visits_per_week
        
        start_date = timezone.now() - timedelta(days=days_count)
        
        for i in range(total_visits):
            # Date aléatoire
            days_offset = random.randint(0, days_count)
            visit_date = start_date + timedelta(days=days_offset)
            
            # Matière aléatoire
            subject = random.choice(subjects)
            course_name = f"Cours de {subject}"
            
            # Durée basée sur l'engagement
            base_duration = 20 if engagement > 0.7 else 10
            duration = random.randint(base_duration, base_duration * 3)
            
            # Simuler la visite (on ne peut pas changer la date après création)
            # On utilise le service directement
            result = tracking_service.record_course_visit(
                student=student,
                course_name=course_name,
                duration_minutes=duration
            )
            
            # Ajuster la date de dernière activité si nécessaire
            if result['success']:
                from analytics_dashboard.models import StudentAnalytics
                analytics, created = StudentAnalytics.objects.get_or_create(
                    user=student,
                    defaults={
                        'student_name': f"{student.first_name} {student.last_name}".strip() or student.username,
                        'student_email': student.email,
                    }
                )
                # On garde la date la plus récente
                if not hasattr(analytics, 'last_activity') or not analytics.last_activity or visit_date > analytics.last_activity:
                    analytics.last_activity = visit_date
                    analytics.save()
    
    def create_sample_predictions(self, students):
        """Créer des prédictions IA d'exemple"""
        from analytics_dashboard.services import PredictionService
        
        prediction_service = PredictionService()
        
        for student in students:
            try:
                prediction_service.generate_real_prediction(student)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Erreur prédiction pour {student.username}: {e}'
                    )
                )