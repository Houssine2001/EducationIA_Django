"""
Modèles de données pour le système d'évaluation et de suivi des performances avec IA
Utilise SQLite avec Django ORM standard
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


# ============================================
# Modèle 1 : Profil Utilisateur/Étudiant
# ============================================

class UserProfile(models.Model):
    """
    Profil étudiant étendu avec analyse de performance et recommandations IA
    """
    # Liaison avec l'utilisateur Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Informations personnelles
    student_id = models.CharField(max_length=50, blank=True, null=True)  # Retiré unique=True pour compatibilité MongoDB
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Informations académiques
    class_level = models.CharField(max_length=100, blank=True, null=True)  # Niveau scolaire
    specialization = models.CharField(max_length=100, blank=True, null=True)  # Spécialisation
    
    # Statistiques globales
    total_tests_taken = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    total_study_time = models.IntegerField(default=0)  # En minutes
    
    # Gamification
    level = models.IntegerField(default=1)  # Niveau du joueur
    total_xp = models.IntegerField(default=0)  # Points d'expérience totaux
    badges = models.JSONField(default=list)  # Liste des badges obtenus
    
    # Analyse des performances (structure JSON)
    strengths = models.JSONField(default=list)  # Points forts: ["mathématiques", "logique", ...]
    weaknesses = models.JSONField(default=list)  # Points faibles: ["grammaire", "orthographe", ...]
    
    # Recommandations IA
    ai_recommendations = models.JSONField(default=dict)  # Recommandations personnalisées
    learning_style = models.CharField(max_length=50, blank=True, null=True)  # Visuel, auditif, kinesthésique
    
    # Historique et progression (données pour IA)
    performance_history = models.JSONField(default=list)  # Historique des scores
    skill_progress = models.JSONField(default=dict)  # Progression par compétence
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def update_statistics(self):
        """Méthode pour mettre à jour les statistiques après un test"""
        # Logique à implémenter
        pass


# ============================================
# Modèle 2 : Test / Évaluation
# ============================================

class Test(models.Model):
    """
    Modèle pour les tests et évaluations
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
        ('expert', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    # Informations de base
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100)  # Matière: Math, Français, etc.
    topic = models.CharField(max_length=200, blank=True, null=True)  # Sujet spécifique
    
    # Créateur du test
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    
    # Configuration du test
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    duration = models.IntegerField(help_text="Durée en minutes", default=60)
    passing_score = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score minimum pour réussir (%)"
    )
    
    # Paramètres
    total_points = models.FloatField(default=100.0)
    number_of_questions = models.IntegerField(default=0)
    is_timed = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)  # Permettre la révision après soumission
    shuffle_questions = models.BooleanField(default=False)
    
    # Statut et publication
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Tags et catégories pour IA
    tags = models.JSONField(default=list)  # ["algèbre", "équations", "niveau-2"]
    skills_tested = models.JSONField(default=list)  # Compétences évaluées
    
    # Métadonnées pour analyse IA
    ai_metadata = models.JSONField(default=dict)  # Données pour l'IA
    
    # Statistiques du test
    total_attempts = models.IntegerField(default=0)
    average_score_obtained = models.FloatField(default=0.0)
    average_completion_time = models.IntegerField(default=0)  # En minutes
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tests'
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.subject})"
    
    def update_statistics(self):
        """Mise à jour des statistiques du test"""
        # Logique à implémenter
        pass


# ============================================
# Modèle 3 : Question
# ============================================

class Question(models.Model):
    """
    Modèle pour les questions (QCM, Vrai/Faux, Rédaction)
    """
    QUESTION_TYPES = [
        ('mcq', 'QCM (Choix Multiple)'),
        ('true_false', 'Vrai/Faux'),
        ('short_answer', 'Réponse Courte'),
        ('essay', 'Rédaction'),
        ('fill_blank', 'Texte à Trous'),
    ]
    
    # Liaison avec le test
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    
    # Contenu de la question
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    order = models.IntegerField(default=0)  # Ordre d'affichage
    
    # Points et difficulté
    points = models.FloatField(default=1.0, validators=[MinValueValidator(0)])
    difficulty_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Options pour QCM (stockées en JSON)
    # Structure: [{"text": "Option A", "is_correct": true}, {"text": "Option B", "is_correct": false}, ...]
    options = models.JSONField(default=list)
    
    # Réponse correcte (pour vrai/faux, réponse courte)
    correct_answer = models.TextField(blank=True, null=True)
    
    # Explications et feedback
    explanation = models.TextField(blank=True, null=True)  # Explication de la réponse
    hint = models.TextField(blank=True, null=True)  # Indice
    
    # Médias associés (images, vidéos, etc.)
    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=50, blank=True, null=True)  # image, video, audio
    
    # Compétences évaluées
    skills = models.JSONField(default=list)  # ["calcul", "raisonnement logique"]
    
    # Métadonnées pour IA
    ai_analysis = models.JSONField(default=dict)  # Analyse de difficulté, patterns, etc.
    common_mistakes = models.JSONField(default=list)  # Erreurs fréquentes
    
    # Statistiques
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    average_time_spent = models.IntegerField(default=0)  # En secondes
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['test', 'order']
    
    def __str__(self):
        return f"{self.question_type} - {self.question_text[:50]}..."
    
    def calculate_success_rate(self):
        """Calcule le taux de réussite de la question"""
        if self.times_answered > 0:
            return (self.times_correct / self.times_answered) * 100
        return 0


# ============================================
# Modèle 4 : Soumission / Réponses
# ============================================

class Submission(models.Model):
    """
    Modèle pour les soumissions de tests par les étudiants
    """
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('submitted', 'Soumis'),
        ('graded', 'Noté'),
    ]
    
    # Références
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='submissions')
    
    # Statut de la soumission
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Réponses (structure JSON)
    # Structure: {"question_id": {"answer": "...", "time_spent": 120, "is_correct": true}, ...}
    answers = models.JSONField(default=dict)
    
    # Temps et progression
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0)  # En secondes
    
    # Score et évaluation
    score = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    
    # Feedback manuel (si correction manuelle)
    teacher_feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    # Analyse IA
    ai_feedback = models.JSONField(default=dict)  # Feedback automatique de l'IA
    performance_analysis = models.JSONField(default=dict)  # Analyse détaillée
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        verbose_name = 'Soumission'
        verbose_name_plural = 'Soumissions'
        ordering = ['-created_at']
        unique_together = ['student', 'test', 'started_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.test.title} ({self.status})"
    
    def calculate_score(self):
        """Calcule le score de la soumission"""
        # Logique à implémenter
        pass


# ============================================
# Modèle 5 : Résultats & Statistiques
# ============================================

class Result(models.Model):
    """
    Modèle pour les résultats détaillés et statistiques avec analyse IA
    """
    # Références
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='result')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    
    # Scores détaillés
    total_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    grade = models.CharField(max_length=5, blank=True, null=True)  # A+, A, B, C, D, F
    
    # Statistiques par type de question
    mcq_score = models.FloatField(default=0.0)
    true_false_score = models.FloatField(default=0.0)
    essay_score = models.FloatField(default=0.0)
    
    # Analyse par compétence
    skills_breakdown = models.JSONField(default=dict)  # {"mathématiques": 85, "logique": 90, ...}
    
    # Comparaisons et classement
    rank = models.IntegerField(null=True, blank=True)  # Classement par rapport aux autres
    percentile = models.FloatField(null=True, blank=True)  # Percentile
    compared_to_average = models.FloatField(default=0.0)  # Différence avec la moyenne
    
    # Analyse temporelle
    questions_per_minute = models.FloatField(default=0.0)
    average_time_per_question = models.FloatField(default=0.0)  # En secondes
    time_efficiency = models.FloatField(default=0.0)  # Score d'efficacité temporelle
    
    # Analyse IA approfondie
    ai_analysis = models.JSONField(default=dict)
    # Structure suggérée:
    # {
    #     "strengths": ["calcul rapide", "raisonnement logique"],
    #     "weaknesses": ["attention aux détails", "gestion du temps"],
    #     "recommendations": ["Pratiquer les exercices chronométrés", ...],
    #     "predicted_next_score": 85.5,
    #     "learning_trajectory": "progressive",
    #     "confidence_score": 0.92
    # }
    
    # Recommandations personnalisées
    recommendations = models.JSONField(default=list)
    study_suggestions = models.JSONField(default=list)
    
    # Patterns détectés par l'IA
    error_patterns = models.JSONField(default=list)  # Types d'erreurs récurrentes
    learning_gaps = models.JSONField(default=list)  # Lacunes identifiées
    
    # Données pour graphiques et visualisations
    performance_chart_data = models.JSONField(default=dict)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'results'
        verbose_name = 'Résultat'
        verbose_name_plural = 'Résultats'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Résultat: {self.student.username} - {self.test.title} ({self.percentage_score}%)"
    
    def assign_grade(self):
        """Attribue une note lettre basée sur le pourcentage"""
        if self.percentage_score >= 90:
            return 'A+'
        elif self.percentage_score >= 85:
            return 'A'
        elif self.percentage_score >= 80:
            return 'B+'
        elif self.percentage_score >= 75:
            return 'B'
        elif self.percentage_score >= 70:
            return 'C+'
        elif self.percentage_score >= 65:
            return 'C'
        elif self.percentage_score >= 60:
            return 'D'
        else:
            return 'F'

