# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .tracking_service import StudentTrackingService

# Importer les modèles avec gestion d'erreur
try:
    from evaluation.models import TestSubmission, Test, StudentProgress
    EVALUATION_AVAILABLE = True
except ImportError:
    TestSubmission = None
    Test = None
    StudentProgress = None
    EVALUATION_AVAILABLE = False

tracking_service = StudentTrackingService()

@receiver(user_logged_in)
def track_student_login(sender, request, user, **kwargs):
    """Tracker la connexion d'un étudiant"""
    if not user.is_staff:
        try:
            tracking_service.record_course_visit(
                student=user,
                course_name="Platform Login",
                duration_minutes=None
            )
        except Exception as e:
            print(f"Erreur lors du tracking de connexion pour {user.username}: {e}")

if EVALUATION_AVAILABLE and TestSubmission:
    @receiver(post_save, sender=TestSubmission)
    def track_test_submission(sender, instance, created, **kwargs):
        """Tracker automatiquement les soumissions de test"""
        if created and instance.student and not instance.student.is_staff:
            try:
                # Calculer le score si disponible
                score = 0
                if hasattr(instance, 'score') and instance.score:
                    score = instance.score
                elif hasattr(instance, 'correct_answers') and hasattr(instance, 'total_questions'):
                    if instance.total_questions > 0:
                        score = (instance.correct_answers / instance.total_questions) * 20
                
                # Déterminer la matière
                subject = "General"
                if hasattr(instance, 'test') and instance.test:
                    if hasattr(instance.test, 'subject'):
                        subject = instance.test.subject
                    elif hasattr(instance.test, 'title'):
                        subject = instance.test.title
                
                # Déterminer le nom du test
                test_name = "Test"
                if hasattr(instance, 'test') and instance.test:
                    if hasattr(instance.test, 'title'):
                        test_name = instance.test.title
                    elif hasattr(instance.test, 'name'):
                        test_name = instance.test.name
                
                # Enregistrer la completion du test
                result = tracking_service.record_test_completion(
                    student=instance.student,
                    test_name=test_name,
                    score=score,
                    subject=subject
                )
                
                if not result['success']:
                    print(f"Erreur tracking test pour {instance.student.username}: {result['error']}")
                    
            except Exception as e:
                print(f"Erreur lors du tracking automatique de test: {e}")

if EVALUATION_AVAILABLE and StudentProgress:
    @receiver(post_save, sender=StudentProgress)
    def track_student_progress(sender, instance, created, **kwargs):
        """Tracker les progrès d'étudiant (visites de cours)"""
        try:
            if instance.student and not instance.student.is_staff:
                # Estimer la durée basée sur les timestamps
                duration_minutes = None
                if hasattr(instance, 'time_spent') and instance.time_spent:
                    duration_minutes = instance.time_spent
                elif hasattr(instance, 'updated_at') and hasattr(instance, 'created_at'):
                    time_diff = instance.updated_at - instance.created_at
                    duration_minutes = time_diff.total_seconds() / 60
                
                # Déterminer le nom du cours
                course_name = "Course"
                if hasattr(instance, 'test') and instance.test:
                    if hasattr(instance.test, 'title'):
                        course_name = f"Étude: {instance.test.title}"
                    elif hasattr(instance.test, 'subject'):
                        course_name = f"Étude: {instance.test.subject}"
                
                # Enregistrer la visite
                tracking_service.record_course_visit(
                    student=instance.student,
                    course_name=course_name,
                    duration_minutes=duration_minutes
                )
                
        except Exception as e:
            print(f"Erreur lors du tracking de progrès: {e}")

# Signaux personnalisés pour l'application analytics
from .models import PerformanceTrend, StudentAnalytics

@receiver(post_save, sender=PerformanceTrend)
def update_analytics_on_performance_change(sender, instance, created, **kwargs):
    """Mettre à jour les analytics quand une nouvelle performance est enregistrée"""
    if created and instance.student:
        try:
            # Mettre à jour les analytics de l'étudiant
            from .services import AnalyticsService
            analytics_service = AnalyticsService()
            analytics_service.update_student_analytics(instance.student)
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour analytics pour {instance.student.username}: {e}")

@receiver(post_delete, sender=PerformanceTrend)
def recalculate_analytics_on_performance_delete(sender, instance, **kwargs):
    """Recalculer les analytics quand une performance est supprimée"""
    if instance.student:
        try:
            from .services import AnalyticsService
            analytics_service = AnalyticsService()
            analytics_service.update_student_analytics(instance.student)
            
        except Exception as e:
            print(f"Erreur lors du recalcul analytics pour {instance.student.username}: {e}")

# Signal pour nettoyer les données anciennes
from django.db.models.signals import pre_save

@receiver(pre_save, sender=StudentAnalytics)
def cleanup_old_data(sender, instance, **kwargs):
    """Nettoyer les anciennes données avant sauvegarde"""
    try:
        # Limiter l'historique des visites à 100 entrées
        if hasattr(instance, 'visit_history') and instance.visit_history:
            import json
            try:
                visits = json.loads(instance.visit_history)
                if len(visits) > 100:
                    # Garder seulement les 100 dernières visites
                    instance.visit_history = json.dumps(visits[-100:])
            except:
                # Si JSON invalide, réinitialiser
                instance.visit_history = '[]'
                
    except Exception as e:
        print(f"Erreur lors du nettoyage des données: {e}")