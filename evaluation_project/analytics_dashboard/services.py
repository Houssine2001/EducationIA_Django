from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
import random
import json

# Import conditionnel pour éviter les erreurs
try:
    from evaluation.models import Submission
except ImportError:
    Submission = None

try:
    from evaluation.models import StudentProgress
except ImportError:
    StudentProgress = None

# Import local
from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel


class AnalyticsService:
    """Service pour calculer et mettre à jour les analytics des étudiants"""
    
    def update_student_analytics(self, student):
        """Met à jour les analytics d'un étudiant"""
        analytics, created = StudentAnalytics.objects.get_or_create(
            user=student,
            defaults={
                'student_name': f"{student.first_name} {student.last_name}" or student.username,
                'student_email': student.email,
            }
        )
        
        # Simuler des données si les modèles evaluation ne sont pas disponibles
        if Submission is None:
            # Données simulées pour les tests
            analytics.total_exercises = random.randint(10, 50)
            analytics.completed_exercises = random.randint(5, analytics.total_exercises)
            analytics.average_score = round(random.uniform(60, 95), 2)
            analytics.success_rate = round(analytics.completed_exercises / analytics.total_exercises * 100, 2)
        else:
            # Logique réelle avec les données de la base
            submissions = Submission.objects.filter(user=student)
            analytics.total_exercises = submissions.count()
            analytics.completed_exercises = submissions.filter(completed=True).count()
            analytics.average_score = submissions.aggregate(avg_score=Avg('score'))['avg_score'] or 0.0
            analytics.success_rate = (analytics.completed_exercises / analytics.total_exercises * 100) if analytics.total_exercises > 0 else 0.0
        
        # Calculer les métriques dérivées
        analytics.learning_velocity = self._calculate_learning_velocity(student)
        analytics.consistency_score = self._calculate_consistency(student)
        analytics.engagement_score = self._calculate_engagement(student)
        analytics.risk_level = self._calculate_risk_level(analytics)
        
        analytics.last_activity = timezone.now()
        analytics.save()
        
        return analytics
    
    def _calculate_learning_velocity(self, student):
        """Calcule la vitesse d'apprentissage"""
        # Simulation pour les tests
        return round(random.uniform(0.5, 2.0), 2)
    
    def _calculate_consistency(self, student):
        """Calcule le score de régularité"""
        # Simulation pour les tests
        return round(random.uniform(0.3, 1.0), 2)
    
    def _calculate_engagement(self, student):
        """Calcule le score d'engagement"""
        # Simulation pour les tests
        return round(random.uniform(0.4, 1.0), 2)
    
    def _calculate_risk_level(self, analytics):
        """Détermine le niveau de risque"""
        if analytics.success_rate >= 80:
            return 'LOW'
        elif analytics.success_rate >= 60:
            return 'MEDIUM'
        elif analytics.success_rate >= 40:
            return 'HIGH'
        else:
            return 'CRITICAL'


class PredictionService:
    """Service pour les prédictions IA"""
    
    def predict_student_risk(self, student):
        """Prédit le risque d'échec d'un étudiant"""
        analytics = StudentAnalytics.objects.filter(user=student).first()
        
        if not analytics:
            return None
        
        # Simulation d'une prédiction IA
        risk_score = random.uniform(0.1, 0.9)
        success_probability = 1 - risk_score
        
        prediction, created = PredictionModel.objects.get_or_create(
            student=student,
            defaults={
                'prediction_type': 'RISK_ASSESSMENT',
                'confidence_score': random.uniform(0.7, 0.95),
                'predicted_outcome': 'SUCCESS' if success_probability > 0.6 else 'RISK',
                'prediction_data': json.dumps({
                    'risk_score': risk_score,
                    'success_probability': success_probability,
                    'factors': ['engagement', 'consistency', 'performance']
                })
            }
        )
        
        return prediction


class ReportService:
    """Service pour générer des rapports"""
    
    def generate_student_report(self, student):
        """Génère un rapport pour un étudiant"""
        analytics = StudentAnalytics.objects.filter(user=student).first()
        
        report = AnalyticsReport.objects.create(
            title=f"Rapport Analytics - {student.get_full_name()}",
            report_type='STUDENT',
            generated_by=student,
            data=json.dumps({
                'student_id': student.id,
                'analytics_summary': {
                    'success_rate': analytics.success_rate if analytics else 0,
                    'risk_level': analytics.risk_level if analytics else 'UNKNOWN',
                    'engagement': analytics.engagement_score if analytics else 0
                }
            }),
            status='COMPLETED'
        )
        
        return report