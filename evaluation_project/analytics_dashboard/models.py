from djongo import models
from django.contrib.auth.models import User
from django.utils import timezone
from bson import ObjectId


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
    
    # Tendances d'apprentissage
    learning_velocity = models.FloatField(default=0.0, help_text="Vitesse d'apprentissage")
    consistency_score = models.FloatField(default=0.0, help_text="Score de régularité")
    difficulty_adaptation = models.FloatField(default=0.0, help_text="Adaptation à la difficulté")
    
    # Prédictions IA
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Faible Risque'),
        ('MEDIUM', 'Risque Moyen'),
        ('HIGH', 'Risque Élevé'),
        ('CRITICAL', 'Risque Critique')
    ], default='LOW')
    
    predicted_success_probability = models.FloatField(default=0.0)
    failure_risk_score = models.FloatField(default=0.0)
    
    # Analyse comportementale
    engagement_score = models.FloatField(default=0.0)
    participation_rate = models.FloatField(default=0.0)
    time_spent_weekly = models.IntegerField(default=0, help_text="Temps en minutes")
    
    # Métadonnées
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_analytics'
        verbose_name = 'Analytics Étudiant'
        verbose_name_plural = 'Analytics Étudiants'
    
    def __str__(self):
        return f"Analytics - {self.student_name}"
    
    def get_risk_level_display(self):
        """Retourne le libellé du niveau de risque"""
        risk_choices = {
            'LOW': 'Faible Risque',
            'MEDIUM': 'Risque Moyen',
            'HIGH': 'Risque Élevé',
            'CRITICAL': 'Risque Critique'
        }
        return risk_choices.get(self.risk_level, self.risk_level)


class PerformanceTrend(models.Model):
    """Modèle pour les tendances de performance dans le temps"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    student_analytics = models.ForeignKey(StudentAnalytics, on_delete=models.CASCADE, related_name='trends')
    date = models.DateField()
    score = models.FloatField()
    exercises_completed = models.IntegerField()
    time_spent_minutes = models.IntegerField()
    difficulty_level = models.CharField(max_length=20, default='MEDIUM')
    
    # Métriques comportementales
    attempts_per_exercise = models.FloatField(default=1.0)
    help_requests = models.IntegerField(default=0)
    completion_time_avg = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'performance_trends'
        ordering = ['-date']
        verbose_name = 'Tendance de Performance'
        verbose_name_plural = 'Tendances de Performance'


class ClassroomAnalytics(models.Model):
    """Analytics au niveau de la classe"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    classroom_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classroom_analytics')
    
    # Métriques collectives
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    average_class_score = models.FloatField(default=0.0)
    class_success_rate = models.FloatField(default=0.0)
    
    # Répartition des risques
    low_risk_count = models.IntegerField(default=0)
    medium_risk_count = models.IntegerField(default=0)
    high_risk_count = models.IntegerField(default=0)
    critical_risk_count = models.IntegerField(default=0)
    
    # Tendances
    improvement_trend = models.CharField(max_length=20, choices=[
        ('POSITIVE', 'Tendance Positive'),
        ('STABLE', 'Stable'),
        ('NEGATIVE', 'Tendance Négative')
    ], default='STABLE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classroom_analytics'
        verbose_name = 'Analytics Classe'
        verbose_name_plural = 'Analytics Classes'
    
    def __str__(self):
        return f"Classe {self.classroom_name} - {self.teacher.get_full_name()}"


class PredictionModel(models.Model):
    """Modèle pour stocker les prédictions IA"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=50, default='RISK_ASSESSMENT')
    confidence_score = models.FloatField(default=0.0)
    predicted_outcome = models.CharField(max_length=50)
    prediction_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_models'
        verbose_name = 'Modèle de Prédiction'
        verbose_name_plural = 'Modèles de Prédiction'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prédiction {self.prediction_type} - {self.student.username}"


class AnalyticsReport(models.Model):
    """Modèle pour les rapports d'analytics"""
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=[
        ('STUDENT', 'Rapport Étudiant'),
        ('CLASSROOM', 'Rapport Classe'),
        ('GLOBAL', 'Rapport Global')
    ])
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'En Attente'),
        ('PROCESSING', 'En Cours'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échec')
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_reports'
        ordering = ['-created_at']
        verbose_name = 'Rapport Analytics'
        verbose_name_plural = 'Rapports Analytics'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"