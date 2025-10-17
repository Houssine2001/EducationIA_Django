from django.db import models
from djongo import models as djongo_models
from bson import ObjectId
from django.contrib.auth.models import User
from django.utils import timezone


class Subject(models.Model):
    """Matière avec ses chapitres"""
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    name = models.CharField(max_length=200)  # Ex: Mathématiques, Physique
    code = models.CharField(max_length=10)  # Ex: MATH, PHYS
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚')  # Emoji pour l'icône
    color = models.CharField(max_length=7, default='#667eea')  # Couleur hex
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'subjects'


class Chapter(models.Model):
    """Chapitre d'une matière"""
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)  # Ordre d'affichage
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)  # Contenu du chapitre
    duration_minutes = models.IntegerField(default=30)  # Durée estimée
    difficulty = models.CharField(max_length=20, choices=[
        ('EASY', 'Facile'),
        ('MEDIUM', 'Moyen'),
        ('HARD', 'Difficile')
    ], default='MEDIUM')
    
    def __str__(self):
        return f"{self.subject.name} - {self.title}"
    
    class Meta:
        db_table = 'chapters'
        ordering = ['order']


class ChapterVisit(models.Model):
    """Enregistrement des visites de chapitres"""
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.IntegerField(default=0)  # Temps passé
    completed = models.BooleanField(default=False)  # Chapitre terminé?
    
    class Meta:
        db_table = 'chapter_visits'


class StudentSubjectProgress(models.Model):
    """Progression d'un étudiant dans une matière"""
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Métriques de visite
    total_visits = models.IntegerField(default=0)
    chapters_visited = models.IntegerField(default=0)
    chapters_completed = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    
    # Métriques de tests
    tests_taken = models.IntegerField(default=0)
    tests_passed = models.IntegerField(default=0)
    average_test_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    
    # Prédiction IA
    predicted_success_rate = models.FloatField(default=0.0)  # 0-100
    confidence_level = models.FloatField(default=0.0)  # 0-100
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
        ('CRITICAL', 'Critique')
    ], default='MEDIUM')
    
    # Engagement
    engagement_score = models.FloatField(default=0.0)  # 0-1
    consistency_score = models.FloatField(default=0.0)  # 0-1
    
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_completion_rate(self):
        """Taux de complétion des chapitres"""
        total_chapters = self.subject.chapters.count()
        if total_chapters == 0:
            return 0.0
        return (self.chapters_completed / total_chapters) * 100
    
    def calculate_visit_engagement(self):
        """Score d'engagement basé sur les visites"""
        total_chapters = self.subject.chapters.count()
        if total_chapters == 0:
            return 0.0
        visit_rate = min(self.chapters_visited / total_chapters, 1.0)
        completion_rate = min(self.chapters_completed / total_chapters, 1.0)
        return (visit_rate * 0.5 + completion_rate * 0.5)
    
    def calculate_test_engagement(self):
        """Score d'engagement basé sur les tests"""
        if self.tests_taken == 0:
            return 0.0
        success_rate = self.tests_passed / self.tests_taken
        score_factor = self.average_test_score / 100
        return (success_rate * 0.6 + score_factor * 0.4)
    
    def update_prediction(self):
        """Met à jour la prédiction de réussite"""
        # Facteurs de prédiction
        visit_engagement = self.calculate_visit_engagement()
        test_engagement = self.calculate_test_engagement()
        
        # Score de base: moyenne des tests
        base_score = self.average_test_score
        
        # Ajustements selon l'engagement
        visit_bonus = visit_engagement * 10  # Max +10%
        test_bonus = test_engagement * 10  # Max +10%
        
        # Facteur de consistance
        consistency_bonus = self.consistency_score * 5  # Max +5%
        
        # Prédiction finale
        predicted = base_score + visit_bonus + test_bonus + consistency_bonus
        predicted = max(0, min(100, predicted))  # Entre 0 et 100
        
        # Confiance basée sur le nombre de données
        data_points = self.total_visits + self.tests_taken
        confidence = min(data_points / 20 * 100, 95)  # Max 95% avec 20+ données
        
        # Niveau de risque
        if predicted >= 70:
            risk = 'LOW'
        elif predicted >= 50:
            risk = 'MEDIUM'
        elif predicted >= 30:
            risk = 'HIGH'
        else:
            risk = 'CRITICAL'
        
        self.predicted_success_rate = round(predicted, 1)
        self.confidence_level = round(confidence, 1)
        self.risk_level = risk
        self.engagement_score = (visit_engagement + test_engagement) / 2
        
    def __str__(self):
        return f"{self.student.username} - {self.subject.name}"
    
    class Meta:
        db_table = 'student_subject_progress'
        unique_together = ['student', 'subject']
