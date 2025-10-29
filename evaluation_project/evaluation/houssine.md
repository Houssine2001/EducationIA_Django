# 🎓 GUIDE COMPLET DU DOSSIER EVALUATION
**Analyse détaillée de tous les fichiers, APIs, bibliothèques et fonctions**

---

## 📋 TABLE DES MATIÈRES

1. [Structure du dossier](#structure)
2. [Fichiers Core](#fichiers-core)
3. [Fichiers d'Analyse IA](#fichiers-analyse-ia)
4. [Fichiers de Services](#fichiers-services)
5. [Fichiers d'Admin](#fichiers-admin)
6. [Dossier Management Commands](#management-commands)
7. [Dossier Migrations](#migrations)
8. [Résumé des APIs et Bibliothèques](#apis-et-bibliotheques)

---

## <a name="structure"></a>
## 📁 STRUCTURE DU DOSSIER

```
evaluation/
├── __init__.py                    # Initialisation du package
├── models.py                      # 5 modèles principaux
├── views.py                       # Vues Django (étudiants/professeurs)
├── urls.py                        # Routes/URLs
├── admin.py                       # Interface d'administration
├── services.py                    # Services métier
├── utils.py                       # Fonctions utilitaires
├── tests.py                       # Tests unitaires
├── apps.py                        # Configuration de l'app
├── auth_backends.py               # Backend d'authentification
│
├── FICHIERS D'ANALYSE IA:
├── analytics.py                   # Analytics des performances
├── ai_feedback.py                 # Génération de feedback IA
├── ai_prediction.py               # Prédictions IA
├── ai_analysis_enhanced.py        # Analyse granulaire des skills
├── ai_concept_analyzer.py         # Analyse conceptuelle avec Hugging Face
├── concept_analysis.py            # Analyse des concepts/topics
├── gamification.py                # Système de badges et classements
│
├── HELPERS:
├── question_generator.py          # Générateur de questions réalistes
├── examples.py                    # Exemples d'utilisation
│
├── management/                    # Commandes Django personnalisées
│   ├── commands/
│   │   ├── generate_test_data.py
│   │   ├── generate_badges.py
│   │   ├── analyze_student_strengths.py
│   │   ├── analyze_detailed_skills.py
│   │   ├── cleanup_test_data.py
│   │   └── cleanup_duplicate_profiles.py
│
└── migrations/                    # Migrations de base de données
    ├── 0001_initial.py
    ├── 0002_userprofile_role.py
    └── 0003_test_source_type.py
```

---

## <a name="fichiers-core"></a>
## 🔑 FICHIERS CORE

---

### 1️⃣ **models.py** - Les 5 Modèles Principaux

#### **Description**
Définit la structure complète de la base de données SQLite avec 5 modèles interconnectés pour gérer les tests, questions, réponses et résultats d'étudiants.

#### **Bibliothèques utilisées**
```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from exercise_generator.fields import CompatibleJSONField
```

#### **Les 5 Modèles**

---

#### **MODÈLE 1: UserProfile**
**Utilité**: Profil étendu d'un utilisateur (étudiant/professeur)

```python
class UserProfile(models.Model):
    # Liaison avec Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(choices=[('student', 'Étudiant'), ('teacher', 'Professeur')])
    
    # Statistiques
    total_tests_taken = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    level = models.IntegerField(default=1)  # Pour gamification
    
    # Données IA
    strengths = CompatibleJSONField(default=list)  # ["math", "logique"]
    weaknesses = CompatibleJSONField(default=list)  # ["grammaire"]
    ai_recommendations = CompatibleJSONField(default=dict)  # Recommendations IA
    badges = CompatibleJSONField(default=list)  # Badges gagnés
```

**Fonctions principales**:
```python
def update_statistics(self):
    """Recalcule les stats après un test"""
    
def get_level_info(self):
    """Retourne info du niveau (XP, progression)"""
```

---

#### **MODÈLE 2: Test**
**Utilité**: Représente un test/évaluation créé par un professeur

```python
class Test(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)  # "Mathématiques", "Français"
    
    # Propriétés
    difficulty = models.CharField(choices=[('easy', 'Facile'), ('medium', 'Moyen')])
    duration = models.IntegerField()  # Durée en minutes
    passing_score = models.FloatField(default=50.0)  # Score pour passer
    
    # Source du test
    source_type = models.CharField(
        choices=[
            ('manual', 'Test Manuel - Créé par Professeur'),
            ('ai_generated', 'Test Généré par IA')
        ]
    )
    
    # Tags pour IA
    tags = CompatibleJSONField(default=list)  # ["algèbre", "niveau-2"]
    skills_tested = CompatibleJSONField(default=list)  # Compétences
    ai_metadata = CompatibleJSONField(default=dict)  # Données IA
```

**Fonctions**:
```python
def is_ai_generated(self):
    """Vérifie si le test est généré par IA"""
    return self.source_type == 'ai_generated'

def update_statistics(self):
    """Recalcule moyenne, tentatives, etc."""
```

---

#### **MODÈLE 3: Question**
**Utilité**: Une question individuelle d'un test

```python
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    
    # Types: QCM, Vrai/Faux, Réponse courte, Rédaction, Texte à trous
    question_type = models.CharField(max_length=20)
    question_text = models.TextField()
    points = models.FloatField(default=1.0)
    
    # Réponses (JSON pour QCM)
    options = CompatibleJSONField(default=list)
    # Format: [{"text": "Option A", "is_correct": true}, ...]
    correct_answer = models.TextField()  # Pour vrai/faux
    
    # Explications
    explanation = models.TextField()  # Pourquoi c'est correct
    hint = models.TextField()  # Indice
    
    # Analyse IA
    skills = CompatibleJSONField(default=list)  # ["calcul", "raisonnement"]
    ai_analysis = CompatibleJSONField(default=dict)  # Analyse de difficulté
    common_mistakes = CompatibleJSONField(default=list)  # Erreurs fréquentes
    
    # Statistiques
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
```

**Fonctions**:
```python
def calculate_success_rate(self):
    """Calcule le % de réussite de cette question"""
    if self.times_answered > 0:
        return (self.times_correct / self.times_answered) * 100
    return 0
```

---

#### **MODÈLE 4: Submission**
**Utilité**: Une soumission d'étudiant à un test (ses réponses)

```python
class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    
    # Réponses de l'étudiant (JSON)
    answers = CompatibleJSONField(default=dict)
    # Format: {
    #   "question_123": {
    #     "answer": "A",
    #     "time_spent": 120,
    #     "is_correct": true,
    #     "feedback": "Correct!"
    #   }
    # }
    
    # Statut
    status = models.CharField(choices=[
        ('in_progress', 'En cours'),
        ('submitted', 'Soumis'),
        ('graded', 'Noté')
    ])
    
    # Temps
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True)
    time_spent = models.IntegerField()  # En secondes
    
    # Résultats
    score = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    
    # Feedback IA
    ai_feedback = CompatibleJSONField(default=dict)
    performance_analysis = CompatibleJSONField(default=dict)
```

---

#### **MODÈLE 5: Result**
**Utilité**: Résultats détaillés avec analyse après un test

```python
class Result(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    
    # Scores
    total_score = models.FloatField()
    percentage_score = models.FloatField()
    grade = models.CharField(max_length=5)  # "A+", "A", "B", etc.
    
    # Scores par type de question
    mcq_score = models.FloatField()
    true_false_score = models.FloatField()
    essay_score = models.FloatField()
    
    # Analyse par compétence
    skills_breakdown = CompatibleJSONField(default=dict)
    # Format: {
    #   "mathématiques": {
    #     "score": 85,
    #     "percentage": 85,
    #     "questions_answered": 10,
    #     "questions_correct": 8
    #   }
    # }
    
    # Comparaisons
    rank = models.IntegerField(null=True)  # Classement
    percentile = models.FloatField(null=True)  # Percentile (0-100)
    
    # Analyse temporelle
    questions_per_minute = models.FloatField()
    average_time_per_question = models.FloatField()
    time_efficiency = models.FloatField()
    
    # Analyse IA TRÈS DÉTAILLÉE
    ai_analysis = CompatibleJSONField(default=dict)
    recommendations = CompatibleJSONField(default=list)
    error_patterns = CompatibleJSONField(default=list)  # Patterns d'erreurs
    learning_gaps = CompatibleJSONField(default=list)  # Lacunes identifiées
```

**Fonctions**:
```python
def assign_grade(self):
    """Attribue une note lettre A-F basée sur %"""
    if self.percentage_score >= 90:
        return 'A+'
    elif self.percentage_score >= 85:
        return 'A'
    # ... etc
```

---

### 2️⃣ **views.py** - Les Vues Django

#### **Description**
Gère les routes HTTP pour les étudiants et professeurs. ~500 lignes de code.

#### **Parties principales**:

---

#### **VUES ÉTUDIANTS**

**`student_dashboard(request)`** - Tableau de bord étudiant
```python
@login_required
def student_dashboard(request):
    """
    Affiche un dashboard complet avec:
    - Score moyen et statistiques
    - Temps d'étude
    - Progression par matière
    - Points forts/faibles identifiés par IA
    - Badges et gamification
    - Tests disponibles
    - Recommandations personnalisées
    """
    
    # 1. Récupérer le profil
    profile = UserProfile.objects.get(user=request.user)
    
    # 2. Générer analytics complètes
    analytics = StudentAnalytics(profile).get_complete_statistics()
    
    # 3. Générer recommandations IA
    update_student_profile_with_recommendations(profile)
    
    # 4. Gamification
    gamification = GamificationService(profile)
    badges = gamification.check_and_award_badges()
    level_info = gamification.get_level_info()
    
    # 5. Tests disponibles
    available_tests = Test.objects.filter(status='published')
    
    return render(request, 'dashboard.html', {
        'analytics': analytics,
        'level_info': level_info,
        'badges': badges,
        'available_tests': available_tests
    })
```

**`start_test(request, test_id)`** - Démarre un test
```python
@login_required
def start_test(request, test_id):
    """
    Crée une nouvelle soumission et démarre le test
    """
    test = get_object_or_404(Test, id=test_id, status='published')
    
    # Créer une soumission
    submission = TestService.start_test(request.user, test)
    
    return redirect('take_test', submission_id=submission.id)
```

**`take_test(request, submission_id)`** - Interface de passage du test
```python
@login_required
def take_test(request, submission_id):
    """
    Affiche l'interface de passage du test avec:
    - Questions une par une
    - Minuteur si timed
    - Sauvegarde auto des réponses
    """
    submission = Submission.objects.get(id=submission_id)
    
    # Calculer le temps restant
    time_elapsed = (now - submission.started_at).total_seconds()
    time_remaining = max(0, submission.test.duration * 60 - time_elapsed)
    
    return render(request, 'take_test.html', {
        'submission': submission,
        'questions': submission.test.questions.all(),
        'time_remaining': time_remaining
    })
```

**`submit_test(request, submission_id)`** - Soumet un test
```python
@login_required
@require_http_methods(["POST"])
def submit_test(request, submission_id):
    """
    1. Récupère les réponses
    2. Corrige automatiquement (AutoGrading)
    3. Crée un Result détaillé
    4. Génère feedback IA
    5. Met à jour le profil étudiant
    """
    submission = Submission.objects.get(id=submission_id)
    
    # Récupérer les réponses POST
    answers = {}
    for question in submission.test.questions.all():
        answers[question.id] = request.POST.get(f'q_{question.id}')
    
    # Correction automatique
    grading_results = TestService.submit_test(submission, answers)
    
    # Créer le résultat
    result = ResultService.create_detailed_result(submission, grading_results)
    
    # Générer feedback IA
    ai_feedback = AIFeedbackGenerator.generate_comprehensive_feedback(
        result, submission
    )
    
    return redirect('view_result', result_id=result.id)
```

**`view_result(request, result_id)`** - Affiche les résultats
```python
@login_required
def view_result(request, result_id):
    """
    Affiche les résultats détaillés avec:
    - Score global et par compétence
    - Correctifs des questions
    - Feedback IA détaillé
    - Recommandations d'apprentissage
    """
    result = Result.objects.get(id=result_id)
    
    # Récupérer les questions avec corrections
    questions_with_answers = []
    for question in result.test.questions.all():
        student_answer = result.submission.answers.get(str(question.id))
        questions_with_answers.append({
            'question': question,
            'student_answer': student_answer,
            'is_correct': student_answer.get('is_correct'),
            'feedback': student_answer.get('feedback')
        })
    
    return render(request, 'view_result.html', {
        'result': result,
        'questions': questions_with_answers
    })
```

---

#### **VUES PROFESSEURS**

**`teacher_dashboard(request)`** - Dashboard professeur
```python
@login_required
def teacher_dashboard(request):
    """
    Affiche:
    - Tests créés par le prof
    - Statistiques des tests
    - Nombre de soumissions
    - Performances moyennes
    """
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    tests = Test.objects.filter(created_by=request.user)
    
    stats = {
        'total_tests': tests.count(),
        'published_tests': tests.filter(status='published').count(),
        'total_submissions': Submission.objects.filter(
            test__created_by=request.user
        ).count(),
    }
    
    return render(request, 'teacher_dashboard.html', {
        'tests': tests,
        'stats': stats
    })
```

---

### 3️⃣ **urls.py** - Les Routes

#### **Description**
Définit toutes les URLs de l'app evaluation

```python
urlpatterns = [
    # AUTHENTIFICATION
    path('signup/', views.signup, name='signup'),
    
    # PROFESSEURS
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/test/create/', views.create_test, name='create_test'),
    path('teacher/test/<test_id>/edit/', views.edit_test, name='edit_test'),
    path('teacher/test/<test_id>/statistics/', views.test_statistics, name='test_statistics'),
    
    # ÉTUDIANTS
    path('', views.student_dashboard, name='student_dashboard'),
    path('test/<test_id>/', views.test_detail, name='test_detail'),
    path('test/<test_id>/start/', views.start_test, name='start_test'),
    path('submission/<submission_id>/take/', views.take_test, name='take_test'),
    path('submission/<submission_id>/submit/', views.submit_test, name='submit_test'),
    path('result/<result_id>/', views.view_result, name='view_result'),
    path('progress/', views.student_progress, name='student_progress'),
    
    # API AJAX
    path('api/save-answer/', views.save_answer_ajax, name='save_answer_ajax'),
]
```

---

### 4️⃣ **admin.py** - Interface d'Administration

#### **Description**
Configure l'interface Django admin avec 5 admin classes

```python
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin pour les profils utilisateurs"""
    list_display = ['user', 'student_id', 'class_level', 'average_score']
    list_filter = ['class_level', 'is_active', 'created_at']
    search_fields = ['user__username', 'student_id']
    
    # Sections repliables
    fieldsets = (
        ('Informations', {'fields': ('user', 'student_id')}),
        ('Statistiques', {'fields': ('average_score', 'level')}),
        ('Analyse IA', {
            'fields': ('strengths', 'weaknesses', 'ai_recommendations'),
            'classes': ('collapse',)  # Replié par défaut
        }),
    )
```

---

### 5️⃣ **services.py** - Services Métier

#### **Description**
Classes de services pour la logique métier

---

#### **CLASSE: AutoGrading**

**Utilité**: Correction automatique des tests

```python
class AutoGrading:
    """Service de correction automatique"""
    
    @staticmethod
    def grade_mcq_question(question, student_answer):
        """
        Corrige une QCM
        
        Args:
            question: Instance Question
            student_answer: "A", "B", etc.
            
        Returns:
            {
                'is_correct': bool,
                'points_earned': float,
                'feedback': str
            }
        """
        # Trouver la bonne réponse
        correct_options = [opt for opt in question.options 
                          if opt.get('is_correct', False)]
        correct_answer = correct_options[0].get('id')
        
        is_correct = student_answer == correct_answer
        
        return {
            'is_correct': is_correct,
            'points_earned': question.points if is_correct else 0,
            'feedback': 'Correct!' if is_correct else 'Incorrect'
        }
    
    @staticmethod
    def grade_submission(submission):
        """
        Corrige une soumission complète
        
        Returns:
            {
                'total_points': float,
                'earned_points': float,
                'percentage': float,
                'passed': bool,
                'skills_performance': dict,
                'detailed_results': dict
            }
        """
        test = submission.test
        total_points = 0
        earned_points = 0
        skills_performance = {}
        
        for question in test.questions.all():
            total_points += question.points
            
            # Récupérer la réponse
            answer_data = submission.answers.get(str(question.id), {})
            student_answer = answer_data.get('answer')
            
            # Correction selon le type
            if question.question_type == 'mcq':
                result = AutoGrading.grade_mcq_question(question, student_answer)
            elif question.question_type == 'true_false':
                result = AutoGrading.grade_true_false_question(question, student_answer)
            
            # ...
            earned_points += result['points_earned']
            
            # Analyser par compétence
            for skill in question.skills:
                if skill not in skills_performance:
                    skills_performance[skill] = {'earned': 0, 'total': 0}
                skills_performance[skill]['total'] += question.points
                skills_performance[skill]['earned'] += result['points_earned']
        
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        return {
            'total_points': total_points,
            'earned_points': earned_points,
            'percentage': percentage,
            'passed': percentage >= test.passing_score,
            'skills_performance': skills_performance
        }
```

---

#### **CLASSE: TestService**

**Utilité**: Gestion des tests

```python
class TestService:
    """Service pour les tests"""
    
    @staticmethod
    def start_test(student, test):
        """Démarre un test pour un étudiant"""
        submission = Submission.objects.create(
            student=student,
            test=test,
            status='in_progress',
            started_at=timezone.now()
        )
        return submission
    
    @staticmethod
    def submit_test(submission, answers):
        """Soumet un test et le corrige"""
        submission.answers = answers
        submission.submitted_at = timezone.now()
        submission.time_spent = int(
            (submission.submitted_at - submission.started_at).total_seconds()
        )
        submission.save()
        
        # Correction auto
        grading_results = AutoGrading.grade_submission(submission)
        
        return grading_results
```

---

#### **CLASSE: ResultService**

**Utilité**: Gestion des résultats

```python
class ResultService:
    """Service pour les résultats"""
    
    @staticmethod
    def create_detailed_result(submission, grading_results):
        """Crée un Result détaillé"""
        result = Result.objects.create(
            submission=submission,
            student=submission.student,
            test=submission.test,
            total_score=grading_results['earned_points'],
            percentage_score=grading_results['percentage'],
            skills_breakdown=grading_results['skills_performance']
        )
        
        # Assigner la note
        result.grade = result.assign_grade()
        result.save()
        
        return result
    
    @staticmethod
    def update_user_profile_stats(student, result):
        """Met à jour le profil étudiant"""
        profile = UserProfile.objects.get(user=student)
        
        profile.total_tests_taken += 1
        
        # Recalculer la moyenne
        all_results = Result.objects.filter(student=student)
        avg = all_results.aggregate(Avg('percentage_score'))['percentage_score__avg']
        profile.average_score = round(avg, 2)
        
        # Ajouter à l'historique
        if not profile.performance_history:
            profile.performance_history = []
        
        profile.performance_history.append({
            'date': timezone.now().isoformat(),
            'score': result.percentage_score,
            'test_id': result.test.id,
            'test_title': result.test.title
        })
        
        profile.save()
```

---

### 6️⃣ **utils.py** - Utilitaires

```python
def get_or_create_user_profile_safe(user):
    """
    Récupère ou crée le profil d'un utilisateur
    Gère les duplicatas en retournant le plus récent
    """
    profile = UserProfile.objects.filter(user=user).order_by('-created_at').first()
    
    if not profile:
        profile = UserProfile.objects.create(
            user=user,
            level='intermediate'
        )
    
    return profile


def validate_score(score):
    """Valide un score (0-100)"""
    try:
        score = float(score)
        return 0 <= score <= 100
    except (ValueError, TypeError):
        return False


def calculate_average(scores):
    """Calcule la moyenne d'une liste de scores"""
    if not scores:
        return 0
    return sum(scores) / len(scores)
```

---

## <a name="fichiers-analyse-ia"></a>
## 🤖 FICHIERS D'ANALYSE IA

---

### 7️⃣ **analytics.py** - Analyse des Performances

#### **Description**
Génère des statistiques détaillées sur les performances des étudiants

#### **Bibliothèques**
```python
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import statistics  # Python standard lib
```

#### **CLASSE: StudentAnalytics**

**Utilité**: Analyse complète des performances d'un étudiant

```python
class StudentAnalytics:
    """
    Génère des statistiques détaillées incluant:
    - Scores globaux (moyenne, médiane, écart-type)
    - Temps d'étude
    - Progression dans le temps
    - Performances par matière
    - Tendances (amélioration/déclin)
    - Points forts/faibles
    """
    
    def __init__(self, student_profile):
        self.profile = student_profile
        self.user = student_profile.user
    
    def get_complete_statistics(self):
        """Retourne TOUTES les stats"""
        all_results = Result.objects.filter(student=self.user).order_by('-created_at')
        
        return {
            'scores': self._calculate_score_statistics(all_results),
            'study_time': self._calculate_study_time(all_results),
            'progression': self._calculate_progression(all_results),
            'subjects': self._calculate_subject_performance(all_results),
            'trends': self._calculate_trends(all_results),
            'strengths': [...],  # Points forts
            'weaknesses': [...],  # Points faibles
            'metadata': {'total_tests': all_results.count(), ...}
        }
    
    def _calculate_score_statistics(self, results):
        """
        Analyse les scores:
        - Moyenne
        - Médiane
        - Min/Max
        - Écart-type
        """
        scores = [r.percentage_score for r in results]
        
        return {
            'average': round(statistics.mean(scores), 2),
            'median': round(statistics.median(scores), 2),
            'min': min(scores),
            'max': max(scores),
            'std_deviation': round(statistics.stdev(scores), 2)
        }
    
    def _calculate_study_time(self, results):
        """
        Calcule le temps d'étude total et par période
        """
        total_minutes = 0
        
        for result in results:
            if result.submission.start_time and result.submission.submitted_at:
                delta = result.submission.submitted_at - result.submission.start_time
                total_minutes += delta.total_seconds() / 60
        
        return {
            'total_minutes': round(total_minutes, 2),
            'total_hours': round(total_minutes / 60, 2),
            'last_7_days': [...],
            'last_30_days': [...]
        }
    
    def _calculate_progression(self, results):
        """
        Analyse la progression dans le temps
        Divise en early vs recent, calcule la tendance
        """
        chronological = list(results.order_by('created_at'))
        
        if len(chronological) < 2:
            return {'trend': 'stable', 'improvement': 0}
        
        split_point = len(chronological) // 2
        early_avg = statistics.mean([r.percentage_score for r in chronological[:split_point]])
        recent_avg = statistics.mean([r.percentage_score for r in chronological[split_point:]])
        
        improvement = recent_avg - early_avg
        
        if improvement > 5:
            trend = 'improving'  # ↗️
        elif improvement < -5:
            trend = 'declining'  # ↘️
        else:
            trend = 'stable'  # →
        
        return {
            'trend': trend,
            'improvement': round(improvement, 2),
            'recent_average': round(recent_avg, 2),
            'early_average': round(early_avg, 2)
        }
    
    def _calculate_subject_performance(self, results):
        """
        Analyse les performances par matière (subject)
        """
        subjects = defaultdict(list)
        
        for result in results:
            subject = result.test.subject
            subjects[subject].append({
                'score': result.percentage_score,
                'date': result.created_at,
                'test_title': result.test.title
            })
        
        subject_stats = {}
        for subject, scores_data in subjects.items():
            scores = [s['score'] for s in scores_data]
            
            subject_stats[subject] = {
                'average': round(statistics.mean(scores), 2),
                'count': len(scores),
                'trend': self._calculate_subject_trend(scores_data),
                'recent_scores': scores[-3:]  # 3 derniers
            }
        
        return subject_stats
```

---

#### **CLASSE: RecommendationEngine**

**Utilité**: Génère des recommandations personnalisées

```python
class RecommendationEngine:
    """
    Génère des recommendations basées sur:
    - Matières faibles
    - Tendances de progression
    - Types d'erreurs
    - Historique
    """
    
    def generate_recommendations(self):
        """Retourne Top 10 recommendations"""
        recommendations = []
        
        # Recommendations pour matières faibles
        recommendations.extend(self._recommend_weak_subjects())
        
        # Recommendations basées sur tendances
        recommendations.extend(self._recommend_from_trends())
        
        # Recommendations sur temps d'étude
        recommendations.extend(self._recommend_study_time())
        
        # Trier par priorité
        recommendations.sort(
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 0),
            reverse=True
        )
        
        return recommendations[:10]  # Top 10
    
    def _recommend_weak_subjects(self):
        """Si une matière a <60%, recommander de la revoir"""
        recommendations = []
        
        for weakness in self.analytics['weaknesses']:
            if weakness['percentage'] < 60:
                recommendations.append({
                    'subject': weakness['subject'],
                    'priority': 'high',
                    'title': f"Revoir {weakness['subject']}",
                    'description': f"Vous avez {weakness['percentage']:.0f}% de réussite. Faites 5-10 exercices."
                })
        
        return recommendations
```

---

### 8️⃣ **ai_feedback.py** - Génération de Feedback IA

#### **Description**
Génère un feedback TRÈS DÉTAILLÉ et personnalisé basé sur les performances

#### **CLASSE: AIFeedbackGenerator**

```python
class AIFeedbackGenerator:
    """Génère du feedback IA comprenant"""
    
    @staticmethod
    def generate_comprehensive_feedback(result, submission):
        """
        Génère un feedback qui inclut:
        - Points forts (avec % précis)
        - Points faibles (avec causes)
        - Recommandations spécifiques
        - Stratégies par type de question
        - Analyse de gestion du temps
        """
        
        analysis = {
            'strengths': [],        # ["Excellente maîtrise de React"]
            'weaknesses': [],       # ["Difficulté avec les Hooks"]
            'recommendations': [],  # ["Pratiquer les Hooks"]
            'skill_mastery': {},    # Par compétence
            'error_patterns': [],   # Types d'erreurs
            'time_analysis': '',    # Gestion du temps
            'overall_feedback': ''  # Message global
        }
        
        test = result.test
        answers = submission.answers or {}
        
        # Analyser chaque question
        correct_count = 0
        incorrect_count = 0
        skills_performance = {}
        
        for question in test.questions.all():
            q_id = str(question.id)
            answer_data = answers.get(q_id, {})
            is_correct = answer_data.get('is_correct', False)
            
            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
            
            # Analyser par compétence
            for skill in question.skills:
                if skill not in skills_performance:
                    skills_performance[skill] = {'correct': 0, 'total': 0}
                
                skills_performance[skill]['total'] += 1
                if is_correct:
                    skills_performance[skill]['correct'] += 1
        
        # Générer feedback par compétence
        for skill, perf in skills_performance.items():
            percentage = (perf['correct'] / perf['total'] * 100)
            
            if percentage >= 80:
                analysis['strengths'].append(
                    f"🌟 Excellente maîtrise de {skill} ({percentage:.0f}%)"
                )
                analysis['skill_mastery'][skill] = {
                    'level': 'expert',
                    'percentage': round(percentage, 1)
                }
            
            elif percentage < 60:
                analysis['weaknesses'].append(
                    f"⚠️ À améliorer: {skill} ({percentage:.0f}%)"
                )
                analysis['recommendations'].append(
                    f"💡 Pratiquer {skill} - Faites 5-10 exercices"
                )
        
        # Feedback global basé sur le score
        score = result.percentage_score
        total_q = test.questions.count()
        
        if score >= 90:
            analysis['overall_feedback'] = (
                f"🏆 Excellent! {correct_count}/{total_q} correctes ({score:.0f}%). "
                f"Vous maîtrisez parfaitement le sujet!"
            )
        elif score >= 75:
            analysis['overall_feedback'] = (
                f"✅ Très bon résultat! {correct_count}/{total_q} correctes ({score:.0f}%). "
                f"Quelques révisions suffiront."
            )
        elif score >= 60:
            analysis['overall_feedback'] = (
                f"📊 Résultat correct. {correct_count}/{total_q} correctes ({score:.0f}%). "
                f"Concentrez-vous sur les {incorrect_count} points manqués."
            )
        else:
            analysis['overall_feedback'] = (
                f"📚 Vous devez revoir ce sujet. Seulement {correct_count}/{total_q} correctes. "
                f"Commencez par les bases."
            )
        
        return analysis
    
    @staticmethod
    def generate_learning_path(student, subject):
        """
        Génère un parcours d'apprentissage personnalisé
        """
        results = Result.objects.filter(
            student=student,
            test__subject=subject
        ).order_by('-created_at')[:5]
        
        if not results:
            return {
                'status': 'new_learner',
                'recommendations': [
                    f"Commencer par les bases de {subject}",
                    "Pratiquer régulièrement (15-30 min/jour)",
                    "Revoir les concepts difficiles"
                ]
            }
        
        avg_score = statistics.mean([r.percentage_score for r in results])
        
        return {
            'current_level': 'beginner' if avg_score < 60 else 'intermediate' if avg_score < 80 else 'advanced',
            'average_score': round(avg_score, 2),
            'recommendations': [...]
        }
```

---

### 9️⃣ **ai_prediction.py** - Prédictions IA

#### **Description**
Prédit le niveau futur d'un étudiant (Faible, Moyen, Pro)

#### **CLASSE: StudentLevelPredictor**

```python
class StudentLevelPredictor:
    """
    Prédit le niveau futur en utilisant:
    - Scores moyens
    - Tendances
    - Consistance
    - Taux d'amélioration
    - Niveau d'activité
    """
    
    WEIGHTS = {
        'average_score': 0.35,      # 35% du score
        'trend': 0.25,               # 25% de la tendance
        'consistency': 0.15,        # 15% de la régularité
        'improvement_rate': 0.15,   # 15% du taux d'amélioration
        'activity_level': 0.10      # 10% de l'activité
    }
    
    def predict_future_level(self, timeframe_months=3):
        """
        Prédit le niveau dans 3 mois
        
        Returns:
            {
                'future_level': 'Pro' | 'Moyen' | 'Faible',
                'current_level': 'Pro' | 'Moyen' | 'Faible',
                'confidence': 0-100,
                'key_factors': ['Forte progression', ...],
                'recommendations': ['Continuer ainsi', ...]
            }
        """
        
        results = Result.objects.filter(
            submission__student=self.user
        ).select_related('submission__test')
        
        if results.count() < 2:
            return self._default_prediction(timeframe_months)
        
        # Calculer les métriques
        metrics = self._calculate_metrics(results)
        
        # Score prédictif pondéré
        prediction_score = (
            metrics['average_score'] * self.WEIGHTS['average_score'] +
            metrics['trend'] * self.WEIGHTS['trend'] +
            metrics['consistency'] * self.WEIGHTS['consistency'] +
            metrics['improvement_rate'] * self.WEIGHTS['improvement_rate'] +
            metrics['activity_level'] * self.WEIGHTS['activity_level']
        )
        
        # Déterminer le niveau
        future_level = 'Pro' if prediction_score >= 75 else 'Moyen' if prediction_score >= 50 else 'Faible'
        
        # Confiance (plus de tests = plus de confiance)
        confidence = min(95, 50 + (results.count() / 20 * 45))
        
        return {
            'future_level': future_level,
            'current_level': self._determine_level(metrics['average_score']),
            'confidence': round(confidence, 1),
            'key_factors': self._identify_key_factors(metrics),
            'recommendations': self._generate_recommendations(metrics, future_level)
        }
    
    def _calculate_metrics(self, results):
        """Calcule 5 métriques clés"""
        scores = [r.percentage_score for r in results]
        
        # 1. Score moyen
        average_score = statistics.mean(scores)
        
        # 2. Tendance (pente de régression linéaire)
        trend = self._calculate_trend(scores)
        
        # 3. Consistance (100 - écart-type)
        consistency = max(0, 100 - (statistics.stdev(scores) * 2))
        
        # 4. Taux d'amélioration (moyenne des changements)
        improvement_rate = statistics.mean([
            scores[i] - scores[i-1] for i in range(1, len(scores))
        ])
        
        # 5. Activité (tests par mois)
        days = (results.last().created_at - results.first().created_at).days
        activity_level = results.count() / max(days/30, 0.5)
        
        return {
            'average_score': average_score,
            'trend': trend,
            'consistency': consistency,
            'improvement_rate': improvement_rate,
            'activity_level': activity_level
        }
    
    def _calculate_trend(self, scores):
        """Calcule la pente de régression linéaire"""
        if len(scores) < 2:
            return 0
        
        n = len(scores)
        x = list(range(n))
        y = scores
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
```

---

### 🔟 **ai_analysis_enhanced.py** - Analyse Granulaire des Compétences

#### **Description**
Analyse TRÈS PRÉCISE au niveau des compétences spécifiques (React Hooks, SQL Joins, etc.)

#### **CLASSE: EnhancedSkillAnalyzer**

```python
class EnhancedSkillAnalyzer:
    """
    Détecte les compétences granulaires comme:
    - "Hooks React (useState, useEffect)"
    - "Jointures SQL (INNER, LEFT, RIGHT)"
    - "Async/await en JavaScript"
    
    Au lieu de simplement "React" ou "JavaScript"
    """
    
    SKILL_PATTERNS = {
        'react': {
            'hooks': [r'useState', r'useEffect', r'useContext', r'useReducer'],
            'components': [r'component', r'props', r'state', r'lifecycle'],
            'routing': [r'react router', r'route', r'navigation'],
            'state_management': [r'redux', r'context api', r'store'],
            'performance': [r'memo', r'optimization', r'lazy loading'],
        },
        'javascript': {
            'es6': [r'arrow function', r'let', r'const', r'template literal'],
            'async': [r'promise', r'async', r'await', r'callback'],
            'dom': [r'dom', r'getelementbyid', r'queryselector'],
            'arrays': [r'map', r'filter', r'reduce', r'forEach'],
        },
        'sql': {
            'queries': [r'select', r'where', r'order by'],
            'joins': [r'join', r'inner join', r'left join', r'right join'],
            'dml': [r'insert', r'update', r'delete'],
            'functions': [r'count', r'sum', r'avg', r'max']
        }
    }
    
    def detect_skill_from_question(self, question_text, options=None):
        """
        Détecte les compétences spécifiques d'une question
        
        Returns:
            [('react', 'hooks'), ('react', 'components'), ...]
        """
        detected_skills = []
        full_text = (question_text + ' ' + ' '.join([str(o) for o in (options or [])])).lower()
        
        for subject, skills in self.SKILL_PATTERNS.items():
            for skill_name, patterns in skills.items():
                for pattern in patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        detected_skills.append((subject, skill_name))
                        break  # Une seule par compétence
        
        return detected_skills
    
    def get_detailed_analysis(self, min_questions=3):
        """
        Retourne l'analyse détaillée par compétence
        
        Returns:
            {
                'strengths': [
                    {
                        'subject': 'React',
                        'skill': 'Hooks React (useState, useEffect)',
                        'percentage': 85,
                        'level': 'excellence'
                    }
                ],
                'weaknesses': [...],
                'recommendations': [...]
            }
        """
        strengths = []
        weaknesses = []
        
        for subject, skills in self.skill_scores.items():
            for skill_name, scores in skills.items():
                if scores['total'] < min_questions:
                    continue
                
                percentage = (scores['correct'] / scores['total'] * 100)
                skill_label = self._get_skill_label(subject, skill_name)
                subject_label = self._get_subject_label(subject)
                
                if percentage >= 80:
                    strengths.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'percentage': round(percentage, 1),
                        'level': 'excellence'
                    })
                elif percentage < 60:
                    weaknesses.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'percentage': round(percentage, 1),
                        'severity': 'high' if percentage < 40 else 'medium'
                    })
        
        return {
            'strengths': sorted(strengths, key=lambda x: x['percentage'], reverse=True)[:10],
            'weaknesses': sorted(weaknesses, key=lambda x: x['percentage'])[:10]
        }
```

---

### 1️⃣1️⃣ **ai_concept_analyzer.py** - Analyseur Conceptuel Hugging Face

#### **Description**
Utilise l'API Hugging Face pour l'analyse IA avancée

#### **APIs utilisées**
```python
# API Hugging Face Inference
https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2
```

#### **CLASSE: AIConceptAnalyzer**

```python
class AIConceptAnalyzer:
    """
    Utilise Mistral-7B pour l'analyse IA avancée
    """
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.api_token = settings.HUGGINGFACE_API_TOKEN
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def analyze_test_performance(self, test_name, subject, questions_data, score):
        """
        Analyse complète d'une performance de test
        
        Args:
            test_name: "Test de Mathématiques"
            subject: "Mathématiques"
            questions_data: [
                {
                    'question': 'Résoudre 2x=4',
                    'concept': 'Équations',
                    'is_correct': true,
                    'student_answer': 'x=2'
                }
            ]
            score: 85.5
            
        Returns:
            {
                'strengths': ['Excellente maîtrise des équations'],
                'weaknesses': ['Difficulté avec les inéquations'],
                'recommendations': ['Pratiquer les inéquations'],
                'detailed_feedback': '...'
            }
        """
        
        # Construire le prompt pour Mistral
        prompt = self._build_analysis_prompt(test_name, subject, questions_data, score)
        
        try:
            # Appeler l'API Hugging Face
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 800,
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result[0].get('generated_text', '')
                analysis = self._parse_ai_response(generated_text)
            else:
                # Fallback si API fail
                analysis = self._generate_basic_analysis(questions_data, score, subject)
            
            return analysis
        
        except Exception as e:
            print(f"Erreur API: {e}")
            return self._generate_basic_analysis(questions_data, score, subject)
    
    def _build_analysis_prompt(self, test_name, subject, questions_data, score):
        """Construit le prompt pour Mistral"""
        from collections import Counter
        
        correct_concepts = [q.get('concept') for q in questions_data if q.get('is_correct')]
        incorrect_concepts = [q.get('concept') for q in questions_data if not q.get('is_correct')]
        
        prompt = f"""[INST] Tu es un expert pédagogique.

Test: {test_name}
Matière: {subject}
Score: {score:.1f}%

Concepts réussis: {', '.join(Counter(correct_concepts).most_common(3))}
Concepts échoués: {', '.join(Counter(incorrect_concepts).most_common(3))}

Génère une analyse JSON:
{{
    "strengths": ["Point fort 1", "Point fort 2"],
    "weaknesses": ["Point faible 1", "Point faible 2"],
    "recommendations": ["Recommandation 1", "Recommandation 2"],
    "feedback": "Feedback détaillé"
}}

Réponds UNIQUEMENT avec le JSON. [/INST]"""
        
        return prompt
    
    def _parse_ai_response(self, generated_text):
        """Parse la réponse JSON de Mistral"""
        try:
            # Extraire le JSON
            start = generated_text.find('{')
            end = generated_text.rfind('}') + 1
            json_str = generated_text[start:end]
            data = json.loads(json_str)
            
            return {
                'strengths': data.get('strengths', [])[:5],
                'weaknesses': data.get('weaknesses', [])[:5],
                'recommendations': data.get('recommendations', [])[:5],
                'detailed_feedback': data.get('feedback', '')
            }
        except Exception as e:
            print(f"Erreur parsing: {e}")
            return self._extract_manual_analysis(generated_text)
```

---

### 1️⃣2️⃣ **gamification.py** - Système de Badges

#### **Description**
Système de gamification avec badges, niveaux et classements

#### **CLASSE: GamificationService**

```python
class GamificationService:
    """
    Gère la gamification:
    - Badges (20+ types différents)
    - Niveaux et XP
    - Classements (leaderboards)
    """
    
    BADGES = {
        'perfect_score': {
            'name': 'Score Parfait',
            'description': 'Obtenir 100% à un test',
            'icon': '🏆',
            'points': 100
        },
        'high_achiever': {
            'name': 'Haut Niveau',
            'description': 'Obtenir >90% à 5 tests',
            'icon': '⭐',
            'points': 50
        },
        'fast_learner': {
            'name': 'Apprenant Rapide',
            'description': 'Améliorer de 20% en 1 semaine',
            'icon': '🚀',
            'points': 40
        },
        'daily_streak_7': {
            'name': 'Série de 7 jours',
            'description': 'Passer un test pendant 7 jours consécutifs',
            'icon': '🔥',
            'points': 25
        },
        # ... 20+ autres badges
    }
    
    LEVELS = [
        {'level': 1, 'xp_required': 0, 'title': 'Débutant'},
        {'level': 2, 'xp_required': 100, 'title': 'Novice'},
        {'level': 3, 'xp_required': 250, 'title': 'Apprenti'},
        {'level': 4, 'xp_required': 500, 'title': 'Étudiant'},
        {'level': 5, 'xp_required': 1000, 'title': 'Avancé'},
        {'level': 10, 'xp_required': 12000, 'title': 'Légende'},
    ]
    
    def check_and_award_badges(self):
        """
        Vérifie et attribue les nouveaux badges
        
        Processus:
        1. Récupérer tous les résultats
        2. Vérifier chaque condition
        3. Attribuer les nouveaux badges
        4. Ajouter les points XP
        """
        
        current_badges = self.profile.badges or []
        current_badge_ids = [b['badge_id'] for b in current_badges]
        
        new_badges = []
        
        results = Result.objects.filter(student=self.user)
        
        # Vérifier Score Parfait
        if 'perfect_score' not in current_badge_ids and results.filter(percentage_score=100).exists():
            new_badges.append(self._award_badge('perfect_score'))
        
        # Vérifier High Achiever (5 tests >90%)
        if 'high_achiever' not in current_badge_ids and results.filter(percentage_score__gte=90).count() >= 5:
            new_badges.append(self._award_badge('high_achiever'))
        
        # Vérifier Fast Learner (amélioration 20% en 1 semaine)
        if 'fast_learner' not in current_badge_ids and self._check_fast_improvement(results):
            new_badges.append(self._award_badge('fast_learner'))
        
        # ... Vérifier 15+ autres conditions
        
        # Mettre à jour le profil
        if new_badges:
            self.profile.badges = current_badges + new_badges
            total_xp_gained = sum([b['points'] for b in new_badges])
            self.profile.total_xp = (self.profile.total_xp or 0) + total_xp_gained
            self.profile.level = self._calculate_level(self.profile.total_xp)
            self.profile.save()
        
        return new_badges
    
    def get_leaderboard(self, period='all_time', limit=10):
        """
        Retourne le classement des étudiants
        
        Args:
            period: 'all_time' | 'monthly' | 'weekly'
            limit: Nombre de résultats
            
        Returns:
            [
                {
                    'rank': 1,
                    'username': 'alice',
                    'average_score': 92.5,
                    'test_count': 15,
                    'xp': 1250,
                    'level': 5
                },
                ...
            ]
        """
        now = timezone.now()
        
        if period == 'weekly':
            date_filter = now - timedelta(days=7)
        elif period == 'monthly':
            date_filter = now - timedelta(days=30)
        else:
            date_filter = None
        
        results_query = Result.objects.all()
        if date_filter:
            results_query = results_query.filter(created_at__gte=date_filter)
        
        # Calculer les moyennes par étudiant
        leaderboard_data = results_query.values('student').annotate(
            avg_score=Avg('percentage_score'),
            test_count=Count('id')
        ).order_by('-avg_score')[:limit]
        
        # Construire le leaderboard
        leaderboard = []
        for rank, item in enumerate(leaderboard_data, start=1):
            user = User.objects.get(id=item['student'])
            profile = UserProfile.objects.get(user=user)
            
            leaderboard.append({
                'rank': rank,
                'username': user.username,
                'average_score': round(item['avg_score'], 2),
                'test_count': item['test_count'],
                'level': profile.level,
                'xp': profile.total_xp,
                'badges_count': len(profile.badges or [])
            })
        
        return leaderboard
```

---

## <a name="fichiers-services"></a>
## ⚙️ FICHIERS DE SERVICES

---

### 1️⃣3️⃣ **question_generator.py** - Générateur de Questions

#### **Description**
Génère des questions réalistes avec des templates pour chaque matière

```python
QUESTION_TEMPLATES = {
    'Mathématiques': {
        'algèbre': [
            "Résoudre l'équation du second degré: x² + {a}x + {b} = 0",
            "Factoriser l'expression: {a}x² + {b}x + {c}",
        ],
        'géométrie': [
            "Calculer l'aire d'un triangle avec base {a}cm et hauteur {b}cm",
            "Trouver le périmètre d'un cercle de rayon {a}cm",
        ]
    },
    'Informatique': {
        'python_basics': [
            "Quel est le type de données retourné par len([1, 2, 3])?",
            "Comment déclarer une variable en Python?",
        ]
    }
    # ... 10+ matières
}

def generate_realistic_question(subject, skill=None, params=None):
    """
    Génère une question réaliste
    
    Returns:
        {
            'question_text': 'Résoudre 2x=4',
            'options': ['x=2', 'x=4', 'x=1'],
            'correct_answer': 'x=2',
            'skill': 'Équations',
            'difficulty': 'easy'
        }
    """
    if params is None:
        params = {
            'a': random.randint(1, 10),
            'b': random.randint(1, 10)
        }
   
# 🎓 GUIDE TECHNIQUE COMPLET - DOSSIER EVALUATION

**Analyse détaillée pour votre professeur**

---

## 📋 TABLE DES MATIÈRES

1. [Architecture Générale](#architecture)
2. [Bibliothèques Utilisées](#bibliotheques)
3. [APIs et Services IA](#apis-ia)
4. [Modèles de Données](#modeles)
5. [Modules d'Analyse](#modules)
6. [Flux de Données](#flux)
7. [Technologies Clés](#technologies)

---

## <a name="architecture"></a>
## 🏗️ ARCHITECTURE GÉNÉRALE

```
evaluation/
├── Core Django (5 modèles interconnectés)
├── Services Métier (Grading, Analytics, Gamification)
├── Modules IA (Concept Analysis, Feedback, Predictions)
├── Views (Student/Teacher dashboards)
└── Admin (Interface d'administration)
```

### Flux Principal

```
Étudiant passe un test
    ↓
Soumission créée (Submission model)
    ↓
Correction automatique (AutoGrading service)
    ↓
Résultat généré (Result model)
    ↓
Analyse IA (AIFeedbackGenerator, AIConceptAnalyzer)
    ↓
Profil mis à jour (UserProfile avec recommandations)
    ↓
Dashboard affiche insights
```

---

## <a name="bibliotheques"></a>
## 📦 BIBLIOTHÈQUES UTILISÉES

### 1. **Django Framework**
```python
# Version: 4.1.13
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
```

**Utilité**: Framework web principal pour l'application

---

### 2. **MongoDB & Djongo**
```python
# Djongo version: 1.3.6
from djongo import models
from pymongo import MongoClient

# Utilisé pour:
# - Stockage hybride SQLite + MongoDB
# - Champs JSON flexibles (CompatibleJSONField)
# - Gestion des données IA complexes
```

**Raison**: Flexibilité pour stocker des données structurées (JSON) sans schéma rigide

---

### 3. **Python Standard Library**
```python
import json              # Sérialisation JSON
import statistics       # Calculs statistiques (mean, median, stdev)
import re              # Expressions régulières pour analyse de texte
from collections import defaultdict, Counter  # Structures de données
from datetime import datetime, timedelta      # Gestion des dates
from typing import Dict, List, Tuple         # Type hints
```

**Utilité**: Outils standards pour l'analyse et manipulation de données

---

### 4. **Requests Library**
```python
import requests
# Pour appels API externes (Hugging Face)
response = requests.post(
    "https://api-inference.huggingface.co/models/...",
    headers={"Authorization": f"Bearer {api_token}"},
    json={...}
)
```

---

## <a name="apis-ia"></a>
## 🤖 APIs ET SERVICES IA UTILISÉS

### 1. **Hugging Face - Mistral 7B Instruct**

#### **Endpoint Principal**
```
URL: https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2
Authentification: Token Bearer
```

#### **Utilisé dans**: `ai_concept_analyzer.py`

#### **Cas d'Usage**: Analyse TRÈS DÉTAILLÉE des performances

```python
class AIConceptAnalyzer:
    """Utilise Mistral 7B pour générer des analyses précises"""
    
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    def analyze_test_performance(self, test_name, subject, questions_data, score):
        """
        Exemple: Après un test de React
        
        INPUT:
        - Test: "React Hooks Advanced"
        - Subject: "JavaScript/React"
        - Score: 85%
        - Questions: [
            {"question": "Utiliser useState et useEffect ensemble?", "concept": "Hooks", "is_correct": true},
            {"question": "Différence entre useCallback et useMemo?", "concept": "Hooks", "is_correct": false},
            ...
          ]
        
        PROMPT ENVOYÉ À MISTRAL:
        [INST] Tu es un expert pédagogique...
        Test: React Hooks Advanced
        Matière: JavaScript/React
        Score: 85%
        
        Concepts réussis:
        - React Hooks (2/3 questions correctes)
        - JSX (3/3)
        - Components (2/2)
        
        Concepts échoués:
        - Performance Optimization (0/2)
        
        Génère une analyse JSON...
        [/INST]
        
        OUTPUT (Généré par IA):
        {
            "strengths": [
                "Excellente maîtrise des Hooks React (useState, useEffect)",
                "Bonne compréhension de la syntaxe JSX",
                "Concepts de base des composants React maîtrisés"
            ],
            "weaknesses": [
                "Lacune importante en optimisation des performances",
                "useMemo et useCallback nécessitent plus de pratique"
            ],
            "recommendations": [
                "Refaire des exercices sur useMemo/useCallback",
                "Pratiquer l'optimisation avec React DevTools",
                "Lire la documentation officielle sur la performance"
            ],
            "feedback": "Excellent niveau général. Voici vos axes d'amélioration..."
        }
        """
```

#### **Avantages**
- ✅ Analyse en langage naturel (pas juste scores chiffrés)
- ✅ Recommandations spécifiques et actionnables
- ✅ Comprend le contexte pédagogique
- ✅ Détection automatique des patterns d'erreurs

#### **Alternative Fallback**
Si l'API Hugging Face est indisponible → `_generate_basic_analysis()` génère des insights basés sur les patterns détectés localement

---

### 2. **NLP Intégré Localement**

Pas de librairie NLP externe (spaCy, NLTK) utilisée.

**À la place**: Regex patterns + règles métier spécifiques

```python
# Dans ai_analysis_enhanced.py
SKILL_PATTERNS = {
    'react': {
        'hooks': [
            r'useState', r'useEffect', r'useContext', r'useReducer',
            r'useMemo', r'useCallback', r'useRef', r'custom hook'
        ],
        'components': [
            r'component', r'props', r'state', r'lifecycle',
            r'render', r'class component', r'functional component'
        ],
        'routing': [
            r'react router', r'route', r'navigation', r'link'
        ],
        # ... 70+ patterns techniques définis
    },
    'python': {...},
    'sql': {...},
    'javascript': {...},
    'django': {...},
}

# Utilisation: Détecter "utilisateur connaît useEffect"
def detect_skill_from_question(question_text):
    for skill_name, patterns in SKILL_PATTERNS['react']['hooks'].items():
        for pattern in patterns:
            if re.search(pattern, question_text, re.IGNORECASE):
                return skill_name  # Détecté !
```

**Pourquoi pas spaCy?** 
- Trop lourd pour ces patterns simples
- Regex suffisant pour extraction de mots-clés techniques
- Moins de dépendances = déploiement plus simple

---

### 3. **Hugging Face Inference API**

#### **Modèle Alternatif Supporté** (Peut être changé)
```python
# Au lieu de Mistral 7B, on pourrait utiliser:

# Option 1: Llama 2 Chat
model_id = "meta-llama/Llama-2-7b-chat-hf"

# Option 2: GPT-J (Gratuit, open-source)
model_id = "EleutherAI/gpt-j-6B"

# Option 3: Flan-T5 (Pour tâches spécifiques)
model_id = "google/flan-t5-large"

# Configuration flexible:
self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
```

---

## <a name="modeles"></a>
## 🗄️ MODÈLES DE DONNÉES (5 Modèles Core)

### **Modèle 1: UserProfile**
```python
class UserProfile(models.Model):
    """Profil étudiant étendu avec IA"""
    
    # Structure:
    user              # Link to Django User
    student_id        # ID étudiant
    strengths         # JSON: ["mathématiques", "logique"]
    weaknesses        # JSON: ["grammaire", "orthographe"]
    ai_recommendations # JSON: AI-generated recommendations
    performance_history # JSON: Historique des scores
    skill_progress     # JSON: Progression par compétence
    badges            # JSON: Badges gagnés (gamification)
    
    # Utilisation dans le flux:
    # 1. Créé quand l'étudiant s'inscrit
    # 2. Mis à jour après chaque test
    # 3. Consultée pour dashboard et recommandations
```

### **Modèle 2: Test**
```python
class Test(models.Model):
    """Test/évaluation avec métadonnées IA"""
    
    # Core data:
    title              # "Test React Hooks"
    subject            # "JavaScript/React"
    difficulty         # "medium"
    duration           # 60 (minutes)
    
    # IA metadata:
    tags               # JSON: ["react", "hooks", "advanced"]
    skills_tested      # JSON: ["Hooks", "Components", "Performance"]
    ai_metadata        # JSON: {"recommended_for": [...], "difficulty_score": 0.65}
    
    # Pour statistiques:
    total_attempts
    average_score_obtained
```

### **Modèle 3: Question**
```python
class Question(models.Model):
    """Une question avec analyse IA détaillée"""
    
    # Contenu:
    question_text      # "Quelle est la différence entre..."
    question_type      # "mcq", "true_false", "essay"
    options            # JSON: [{"text": "Option A", "is_correct": true}, ...]
    correct_answer     # "A" ou texte
    
    # Analyse détaillée:
    skills             # JSON: ["React Hooks", "Performance"]
    common_mistakes    # JSON: [{"mistake": "...", "frequency": 0.25}, ...]
    ai_analysis        # JSON: {"difficulty_score": 0.5, "cognitive_level": "application"}
    
    # Stats:
    times_answered
    times_correct
    average_time_spent
```

### **Modèle 4: Submission**
```python
class Submission(models.Model):
    """Les réponses d'un étudiant à un test"""
    
    student            # Link to User
    test               # Link to Test
    status             # "in_progress", "graded"
    
    # Les réponses:
    answers            # JSON: {
                       #   "question_123": {
                       #     "answer": "A",
                       #     "time_spent": 120,
                       #     "is_correct": true
                       #   }
                       # }
    
    # Timing:
    started_at
    submitted_at
    time_spent         # Secondes
    
    # Feedback IA:
    ai_feedback        # JSON: Feedback automatique
    performance_analysis # JSON: Analyse de performance
```

### **Modèle 5: Result**
```python
class Result(models.Model):
    """Résultats détaillés APRÈS un test (avec analyse IA)"""
    
    submission         # Link to Submission (1:1)
    student            # Link to User
    test               # Link to Test
    
    # Scores:
    total_score        # 19/20
    percentage_score   # 95%
    grade              # "A+"
    
    # Scores par type:
    mcq_score
    true_false_score
    essay_score
    
    # Analyse par compétence:
    skills_breakdown   # JSON: {
                       #   "React Hooks": {
                       #     "score": 90,
                       #     "percentage": 90,
                       #     "questions_answered": 10,
                       #     "questions_correct": 9
                       #   }
                       # }
    
    # Analyse IA TRÈS DÉTAILLÉE:
    ai_analysis        # JSON: IA insights complets
    recommendations    # JSON: Recommandations personnalisées
    error_patterns     # JSON: Patterns d'erreurs détectés
    learning_gaps      # JSON: Lacunes identifiées
```

---

## <a name="modules"></a>
## 📊 MODULES D'ANALYSE IA

### **Module 1: AIConceptAnalyzer** (`ai_concept_analyzer.py`)

**Fonction**: Analyse précise des concepts avec Hugging Face

```python
analyzer = AIConceptAnalyzer()

# Analyse détaillée d'un test
analysis = analyzer.analyze_test_performance(
    test_name="React Advanced",
    subject="JavaScript/React",
    questions_data=[
        {"question": "...", "concept": "Hooks", "is_correct": True},
        ...
    ],
    score=85.0
)

# Retour:
{
    'strengths': [
        "Excellente maîtrise des Hooks React",
        "Bonne compréhension des composants"
    ],
    'weaknesses': [
        "Performance optimization nécessite travail"
    ],
    'recommendations': [
        "Pratiquer useMemo et useCallback"
    ],
    'detailed_feedback': "Texte narratif complet..."
}
```

**Flux Interne**:
1. Build prompt pédagogique
2. Appel API Mistral 7B
3. Parse réponse JSON
4. Valide et nettoie (élimine messages génériques)
5. Retourne insights actionnables

---

### **Module 2: EnhancedSkillAnalyzer** (`ai_analysis_enhanced.py`)

**Fonction**: Détection GRANULAIRE des compétences

```python
analyzer = EnhancedSkillAnalyzer()

# Détecter les compétences d'une question
skills = analyzer.detect_skill_from_question(
    "Comment utiliser useState et useEffect ensemble?"
)
# Retour: [('react', 'hooks'), ('react', 'state_management')]

# Analyser les résultats
analysis = analyzer.analyze_student_results_detailed(student, results)
# Retour:
{
    'strengths': [
        {
            'subject': 'React',
            'skill': 'Hooks React (useState, useEffect, etc.)',
            'percentage': 92.5,
            'level': 'excellence'
        }
    ],
    'weaknesses': [
        {
            'subject': 'React',
            'skill': 'Optimisation des performances',
            'percentage': 45.0,
            'severity': 'high'
        }
    ],
    'recommendations': [...]
}
```

**Mappings Techniques** (70+ patterns):
```python
SKILL_PATTERNS = {
    'react': {
        'hooks': [r'useState', r'useEffect', r'useContext', ...],
        'components': [r'component', r'props', r'lifecycle', ...],
        'state_management': [r'redux', r'context api', ...],
        'performance': [r'memo', r'optimization', r'suspense', ...],
    },
    'python': {
        'oop': [r'class', r'inheritance', r'polymorphism', ...],
        'async': [r'async', r'await', r'asyncio', ...],
    },
    'sql': {
        'joins': [r'join', r'inner join', r'left join', ...],
        'functions': [r'count', r'sum', r'avg', r'max', ...],
    },
    # ... 10+ technologies supportées
}
```

---

### **Module 3: StudentAnalytics** (`analytics.py`)

**Fonction**: Statistiques complètes des performances

```python
analytics = StudentAnalytics(student_profile)

# Récupérer ALL statistics
stats = analytics.get_complete_statistics()

# Retour:
{
    'scores': {
        'average': 82.5,
        'median': 85.0,
        'min': 65,
        'max': 95,
        'std_deviation': 8.2
    },
    'study_time': {
        'total_hours': 12.5,
        'last_7_days': 3.2,
        'last_30_days': 10.5
    },
    'progression': {
        'trend': 'improving',  # ou 'declining', 'stable'
        'improvement': +8.5,
        'progression_data': [...]
    },
    'subjects': {
        'React': {'average': 88, 'trend': 'improving'},
        'SQL': {'average': 75, 'trend': 'stable'}
    },
    'trends': {
        'weekly': {'change': +5.2, 'trend': 'improving'},
        'monthly': {'change': +12.1, 'trend': 'improving'},
        'consistency': {'score': 85.5, 'label': 'Très régulier'}
    }
}
```

---

### **Module 4: RecommendationEngine** (dans `analytics.py`)

**Fonction**: Générer recommandations personnalisées

```python
engine = RecommendationEngine(profile, analytics_data)
recommendations = engine.generate_recommendations()

# Retour: [
#   {
#       'priority': 'high',
#       'title': 'Renforcer React Hooks',
#       'description': 'Points faibles identifiés en Hooks React...',
#       'actions': ['Faire 10 exercices', 'Relire docs officielles']
#   },
#   ...
# ]
```

---

### **Module 5: StudentLevelPredictor** (`ai_prediction.py`)

**Fonction**: Prédire le niveau FUTUR de l'étudiant

```python
predictor = StudentLevelPredictor(profile)

# Prédiction sur 3 mois
prediction = predictor.predict_future_level(timeframe_months=3)

# Retour:
{
    'current_level': 'Moyen',      # Basé sur score actuel
    'future_level': 'Pro',         # Basé sur tendances
    'confidence': 87.5,            # % de confiance (50-95%)
    'key_factors': [
        'Forte progression observée (+8.5% par mois)',
        'Très régulier dans les efforts',
        'Activité: 3 tests/semaine'
    ],
    'timeframe': '3 mois',
    'recommendations': [
        'Maintenez votre rythme - excellent progression!',
        'Explorez des sujets avancés'
    ],
    'metrics': {
        'average_score': 82.5,
        'trend': 1.25,  # Pente de régression linéaire
        'consistency': 85.5,
        'improvement_rate': +2.1,
        'activity_level': 3.2  # tests/mois
    }
}
```

**Calcul de Confiance**:
```
confidence = (
    test_count_factor * 0.5 +        # Plus de tests = plus de confiance
    consistency_score * 0.3 +         # Résultats réguliers
    activity_level_factor * 0.2       # Activité régulière
)
```

---

### **Module 6: AIFeedbackGenerator** (`ai_feedback.py`)

**Fonction**: Feedback TRÈS détaillé et personnalisé

```python
feedback = AIFeedbackGenerator.generate_comprehensive_feedback(result, submission)

# Retour:
{
    'overall_feedback': "🏆 Excellent travail! 95% - Vous maîtrisez parfaitement...",
    'strengths': [
        "🌟 **React Hooks** - Maîtrise excellente (92%) - 11/12 correctes",
        "✅ **JSX** - Bonne maîtrise (87%) - 7/8 correctes"
    ],
    'weaknesses': [
        "❌ **Performance Optimization** - Lacune importante (30%) - 2/7 correctes"
    ],
    'recommendations': [
        "🎯 **Priorité #1**: Concentrez-vous sur React Hooks (92%) et JSX (87%)",
        "📝 **Révision ciblée** - Refaites les exercices sur Performance",
        "💡 **Stratégie QCM** - Lisez TOUTES les options avant de choisir"
    ],
    'skill_mastery': {
        'React Hooks': {'percentage': 92.0, 'level': 'Expert'},
        'Performance': {'percentage': 30.0, 'level': 'Débutant'}
    },
    'error_patterns': [
        "🔍 Difficulté avec les **Questions Rédactionnelles** - 2/5 correctes (40%)"
    ],
    'time_management_analysis': "⏱️ Vous avez utilisé 95% du temps - Vous devriez pratiquer en vous chronométrant",
    'encouragement': "🌟 Vous êtes au niveau expert!..."
}
```

---

### **Module 7: GamificationService** (`gamification.py`)

**Fonction**: Badges, niveaux, classements

```python
gamification = GamificationService(profile)

# Vérifier et attribuer badges
new_badges = gamification.check_and_award_badges()

# Retour:
[
    {
        'badge_id': 'perfect_score',
        'name': 'Score Parfait',
        'description': 'Obtenir 100% à un test',
        'icon': '🏆',
        'color': 'gold',
        'rarity': 'epic',
        'points': 100,
        'earned_at': '2025-10-29T14:30:00'
    }
]

# Récupérer infos du niveau
level_info = gamification.get_level_info()
# Retour:
{
    'current_level': 5,
    'current_title': 'Avancé',
    'current_xp': 1250,
    'next_level': 6,
    'next_title': 'Expert',
    'xp_for_next_level': 750,
    'progress_percentage': 62.5
}

# Obtenir leaderboard
leaderboard = gamification.get_leaderboard(period='weekly', limit=10)
```

**Badges Disponibles** (15+ types):
- Score Parfait (100%)
- Haut Niveau (90%+ à 5 tests)
- Régulier (70%+ à 10 tests)
- Apprenant Rapide (+20% en 1 semaine)
- Série de 7 jours (1 test/jour pendant 7 jours)
- Maître de Matière (90%+ moyenne dans une matière)
- ... et plus

---

## <a name="flux"></a>
## 🔄 FLUX DE DONNÉES COMPLET

### **Étape 1: Étudiant Passe un Test**
```
student_dashboard() → start_test() → take_test()
```

### **Étape 2: Soumission du Test**
```python
# Dans take_test():
submission = Submission.objects.create(
    student=user,
    test=test,
    status='in_progress',
    started_at=now
)
```

### **Étape 3: Correction Automatique**
```python
# Dans submit_test():
grading_results = AutoGrading.grade_submission(submission)
# Retour: {
#     'earned_points': 19,
#     'percentage': 95,
#     'passed': True,
#     'skills_performance': {...}
# }
```

### **Étape 4: Création du Résultat**
```python
result = ResultService.create_detailed_result(submission, grading_results)
# Crée Result model avec scores détaillés
```

### **Étape 5: Analyse IA**
```python
# Feedback précis
ai_feedback = AIFeedbackGenerator.generate_comprehensive_feedback(result, submission)
result.ai_feedback = ai_feedback
result.save()

# Analyse conceptuelle
concept_analyzer = AIConceptAnalyzer()
analysis = concept_analyzer.analyze_test_performance(...)
result.ai_analysis = analysis
result.save()
```

### **Étape 6: Mise à Jour du Profil**
```python
profile = user.profile
profile.total_tests_taken += 1

# Recalculer moyenne
all_results = Result.objects.filter(student=user)
profile.average_score = all_results.aggregate(Avg('percentage_score'))
profile.save()

# Générer recommandations
update_student_profile_with_recommendations(profile)
# Retour: Profile.ai_recommendations mis à jour avec insights
```

### **Étape 7: Dashboard Affiche Tout**
```python
student_dashboard(request)
# Affiche:
# - Analytics complètes
# - Recommandations personnalisées
# - Badges gagnés
# - Leaderboard
# - Progression
```

---

## <a name="technologies"></a>
## 🛠️ TECHNOLOGIES CLÉS

### **Backend**
| Technologie | Version | Utilité |
|------------|---------|---------|
| Django | 4.1.13 | Framework web principal |
| Djongo | 1.3.6 | ORM MongoDB pour Django |
| Python | 3.8+ | Langage principal |
| SQLite | - | Base de données locale |
| MongoDB | 4.4+ | Stockage flexible JSON |

### **IA et ML**
| Service | Utilité |
|---------|---------|
| **Hugging Face API** | Analyse en langage naturel avec Mistral 7B |
| **Regex Patterns** | Détection de compétences techniques |
| **Python Statistics** | Analyses statistiques (moyenne, écart-type) |
| **Linear Regression** | Détection de tendances |

### **APIs Externes**
| API | Endpoint | Usage |
|-----|----------|-------|
| Hugging Face Inference | `https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2` | Analyse IA avancée |

---

## 📊 EXEMPLE COMPLET DE CAS D'USAGE

### **Scénario: Alice complète un test React**

```python
# 1. Alice démarre le test
start_test(request, test_id="react_hooks_test")
→ Submission créée à 14:00

# 2. Alice répond aux questions pendant 45 minutes
# Questions traitées:
# Q1: "useState vs useEffect?" - CORRECT ✓
# Q2: "Hooks dans composants classe?" - INCORRECT ✗
# Q3: "Performance memo?" - INCORRECT ✗
# Q4: "Rédaction sur Hooks" - CORRECT (9/10)

# 3. Alice soumet à 14:45
submit_test(request, submission_id)

# 4. CORRECTION AUTOMATIQUE (AutoGrading)
AutoGrading.grade_submission()
{
    'total_points': 20,
    'earned_points': 15,
    'percentage': 75.0,
    'skills_performance': {
        'React Hooks': {'correct': 2, 'total': 3},
        'Performance': {'correct': 0, 'total': 1}
    }
}

# 5. CRÉATION DU RÉSULTAT
Result.objects.create(
    student=alice,
    submission=submission,
    percentage_score=75.0,
    grade='B'
)

# 6. ANALYSE IA PAR HUGGING FACE
# Prompt envoyé:
"""
Test: React Hooks Advanced
Concepts réussis:
- React Hooks (2/3 correctes)
Concepts échoués:
- Performance (0/1 correcte)

Analyse...
"""

# Mistral génère:
{
    'strengths': [
        "Bonne compréhension des Hooks React (67%)",
    ],
    'weaknesses': [
        "Optimisation des performances à retravailler",
    ],
    'recommendations': [
        "Pratiquez React.memo et useMemo",
        "Lisez la section performance de la docs",
    ]
}

# 7. MISE À JOUR DU PROFIL D'ALICE
alice.profile.average_score = 78.5  # (75 + 82) / 2
alice.profile.ai_recommendations = [
    "🔴 PRIORITÉ: Optimisation React (0%)",
    "📈 Continuez avec React Hooks (67%)",
    ...
]
alice.profile.save()

# 8. VÉRIFICATION DES BADGES
GamificationService(alice.profile).check_and_award_badges()
# Résultat: Alice gagne le badge "Dedicated Student" (20 tests)

# 9. AFFICHAGE DANS LE DASHBOARD
student_dashboard(alice)
# Affiche:
# ✅ Score: 75%
# 📊 Moyenne: 78.5%
# 🎯 Points forts: React Hooks
# ⚠️ À améliorer: Performance
# 💡 Recommandations IA: [...]
# 🏆 Badge: Dedicated Student (+20 XP)
# 📈 Niveau: 5/10 (Avancé)
```

---

## 🔐 SÉCURITÉ & GESTION DES ERREURS

### **Gestion des Erreurs IA**
```python
try:
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        analysis = response.json()
    else:
        # FALLBACK: Analyse basique
        analysis = _generate_basic_analysis(questions_data, score)
except Exception as e:
    # FALLBACK: Génère toujours des insights (jamais vide)
    analysis = _generate_basic_analysis(questions_data, score)
```

### **Validations**
```python
# Valider les scores
def validate_score(score):
    return 0 <= score <= 100

# Nettoyer les analyses (éliminer messages génériques)
def _validate_and_clean_analysis(analysis):
    # Élimine "Aucune faiblesse détectée"
    # Force génération spécifique basée sur concepts
```

---

## 📈 AMÉLIORATIONS FUTURES

```python
# 1. Intégrer NLP avancé (spaCy)
from spacy import load
nlp = load("fr_core_news_sm")

# 2. Machine Learning pour prédictions
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()

# 3. Cache pour API Hugging Face
@cache(timeout=3600)
def analyze_with_huggingface():
    pass

# 4. Batch processing pour analyses en masse
def analyze_batch_students():
    students = UserProfile.objects.filter(total_tests__gt=5)
    # Analyser 100 étudiants en parallèle
```

---

## 📞 RÉSUMÉ POUR VOTRE PROFESSEUR

### **Points Clés à Présenter**
1. ✅ **5 modèles Django** interconnectés
2. ✅ **3 services de correction**: AutoGrading, Feedback, Predictions
3. ✅ **7 modules IA** avec Hugging Face Mistral 7B
4. ✅ **Analyse granulaire** des 70+ compétences techniques
5. ✅ **Recommandations personnalisées** basées sur données étudiants
6. ✅ **Gamification complète**: 15+ badges, leaderboards, XP
7. ✅ **Flux complet** de test → analyse → insights → profil

### **Technologies Utilisées**
- Django 4.1.13 + Djongo 1.3.6
- MongoDB + SQLite
- Hugging Face Mistral 7B (IA)
- Regex + Statistics (NLP basique local)
- Python standard library

### **Bibliothèques Principales**
```
django==4.1.13
djongo==1.3.6
pymongo==4.6.0
gunicorn==21.2.0
python-dotenv==1.0.0
requests==2.31.0  # Pour appels API
```

---

**Prêt à présenter à votre professeur !** 🎓

