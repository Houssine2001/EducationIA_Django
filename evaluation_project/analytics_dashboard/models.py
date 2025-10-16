from djongo import models
from django.contrib.auth.models import User
from django.utils import timezone
from bson import ObjectId
import json


class StudentAnalytics(models.Model):
    """Modèle pour stocker les analytics des étudiants"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    # Informations étudiant
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    
    # Métriques de performance
    total_exercises = models.IntegerField(default=0)
    completed_exercises = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PerformanceTrend(models.Model):
    """Tendances de performance dans le temps"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()
    subject = models.CharField(max_length=100)


class ClassroomAnalytics(models.Model):
    """Analytics par classe"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    class_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    students_count = models.IntegerField(default=0)
    average_performance = models.FloatField(default=0.0)


class PredictionModel(models.Model):
    """Modèle de prédiction IA"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50)
    prediction_value = models.FloatField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class AnalyticsReport(models.Model):
    """Rapports d'analytics"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    title = models.CharField(max_length=200)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class SubjectAnalytics(models.Model):
    """Analytics par matière avec prédictions IA réelles"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    # Informations de base
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_analytics')
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10, default='')
    
    # Métriques de visite
    total_visits = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # en minutes
    last_visit = models.DateTimeField(null=True, blank=True)
    visit_frequency = models.FloatField(default=0.0)  # visites par semaine
    
    # Métriques de test
    tests_taken = models.IntegerField(default=0)
    tests_passed = models.IntegerField(default=0)
    average_test_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    worst_score = models.FloatField(default=0.0)
    last_test_date = models.DateTimeField(null=True, blank=True)
    first_test_date = models.DateTimeField(null=True, blank=True)
    
    # Prédictions IA (calculées dynamiquement)
    predicted_success_probability = models.FloatField(default=0.5)
    risk_level = models.CharField(max_length=20, default='MEDIUM')
    prediction_confidence = models.FloatField(default=0.0)
    improvement_trend = models.CharField(max_length=20, default='UNKNOWN')
    
    # Données de recommandation (stockées en JSON)
    prediction_factors = models.JSONField(default=dict)
    recommended_actions = models.JSONField(default=list)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_engagement_level(self):
        """Calcule le niveau d'engagement"""
        if self.total_visits >= 15:
            return 'ÉLEVÉ'
        elif self.total_visits >= 8:
            return 'MOYEN'
        elif self.total_visits >= 3:
            return 'FAIBLE'
        else:
            return 'AUCUN'
    
    def calculate_success_rate(self):
        """Calcule le taux de réussite"""
        if self.tests_taken > 0:
            return (self.tests_passed / self.tests_taken) * 100
        return 0.0
    
    def get_risk_level_display(self):
        """Affichage du niveau de risque"""
        levels = {
            'LOW': 'Faible',
            'MEDIUM': 'Moyen',
            'HIGH': 'Élevé',
            'CRITICAL': 'Critique'
        }
        return levels.get(self.risk_level, 'Moyen')


class SubjectVisit(models.Model):
    """Enregistrement des visites par matière"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    subject_analytics = models.ForeignKey(SubjectAnalytics, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(default=30)
    pages_viewed = models.IntegerField(default=1)
    interaction_score = models.FloatField(default=0.5)


class SubjectTestResult(models.Model):
    """Résultats des tests par matière"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    subject_analytics = models.ForeignKey(SubjectAnalytics, on_delete=models.CASCADE, related_name='test_results')
    test_name = models.CharField(max_length=200)
    test_date = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()
    max_score = models.FloatField(default=100.0)
    passed = models.BooleanField(default=False)
    time_spent = models.IntegerField(default=0)  # en minutes
    attempts = models.IntegerField(default=1)
    quiz_data = models.JSONField(default=dict)  # Questions et réponses du quiz


class SubjectQuiz(models.Model):
    """Banque de questions par matière"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    subject_name = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=20, default='MEDIUM')  # EASY, MEDIUM, HARD
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)