# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.conf import settings
from backend.mongodb_utils import get_mongodb_client
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

# ============================================================
# 🎮 SIGNAL POUR PROGRESSION AUTOMATIQUE DES DÉFIS
# ============================================================

@receiver(post_save)
def update_challenge_progress_on_exercise_completion(sender, instance, created, **kwargs):
    """
    Signal pour mettre à jour la progression des défis quand un exercice est complété
    Fonctionne avec MongoDB (exercise_generator) et Django ORM (evaluation)
    """
    try:
        # Vérifier si c'est une soumission d'exercice IA complétée
        if sender.__name__ == 'StudentExerciseSubmission' and created:
            print(f"✅ Signal déclenché pour exercice IA: {instance}")
            
            # Récupérer l'utilisateur
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if hasattr(instance, 'student_id'):
                user = User.objects.get(id=instance.student_id)
            elif hasattr(instance, 'student'):
                user = instance.student
            else:
                return
            
            print(f"👤 Utilisateur: {user.username}")
            
            # Récupérer le profil et ajouter XP
            from evaluation.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Ajouter des XP pour l'exercice complété
            xp_gained = 10  # XP de base
            if hasattr(instance, 'score') and instance.score:
                xp_gained += int(instance.score / 10)  # Bonus basé sur le score
            
            profile.total_xp += xp_gained
            profile.save()
            print(f"💫 {xp_gained} XP ajoutés. Total: {profile.total_xp}")
            
            # Mettre à jour les défis actifs
            from .models import Challenge
            active_challenges = Challenge.objects.filter(
                student=user,
                status='ACTIVE',
                expires_at__gte=timezone.now()
            )
            
            print(f"🎯 {active_challenges.count()} défis actifs trouvés")
            
            for challenge in active_challenges:
                if 'exercice' in challenge.title.lower() or challenge.subject:
                    try:
                        # Connexion MongoDB
                        client = get_mongodb_client()
                        db = client[settings.MONGO_DB_NAME]
                        
                        # Compter les exercices complétés depuis le début du défi
                        completed_count = db.student_exercise_submissions.count_documents({
                            'student_id': user.id,
                            'status': 'completed',
                            'submitted_at': {'$gte': challenge.created_at}
                        })
                        
                        # Calculer la nouvelle progression
                        target_value = challenge.target_data.get('target_value', 5)
                        old_progress = challenge.current_progress
                        new_progress = min(100, (completed_count / target_value) * 100)
                        
                        print(f"🎯 Défi '{challenge.title}': {completed_count}/{target_value} exercices")
                        print(f"📊 Progression: {old_progress}% -> {new_progress}%")
                        
                        # Mettre à jour la progression
                        challenge.current_progress = new_progress
                        
                        # Vérifier si le défi est complété
                        if new_progress >= 100 and challenge.status != 'COMPLETED':
                            challenge.status = 'COMPLETED'
                            challenge.completed_at = timezone.now()
                            
                            # Ajouter les récompenses
                            profile.total_xp += challenge.xp_reward
                            profile.coins += challenge.coins_reward
                            profile.save()
                            
                            print(f"🎉 DÉFI COMPLÉTÉ! +{challenge.xp_reward} XP, +{challenge.coins_reward} coins")
                        
                        challenge.save()
                        client.close()
                        
                    except Exception as e:
                        print(f"❌ Erreur MongoDB pour défi '{challenge.title}': {e}")
        
        # Gérer les soumissions de tests Django normaux
        elif sender.__name__ in ['TestSubmission', 'Result'] and created:
            print(f"✅ Signal déclenché pour test Django: {instance}")
            
            if hasattr(instance, 'student'):
                user = instance.student
            elif hasattr(instance, 'user'):
                user = instance.user
            else:
                return
            
            # Même logique pour les tests Django
            from evaluation.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # XP pour test complété
            xp_gained = 15
            if hasattr(instance, 'score') and instance.score:
                xp_gained += int(instance.score / 5)
            elif hasattr(instance, 'percentage_score') and instance.percentage_score:
                xp_gained += int(instance.percentage_score / 5)
            
            profile.total_xp += xp_gained
            profile.save()
            print(f"💫 {xp_gained} XP ajoutés pour test Django. Total: {profile.total_xp}")
    
    except Exception as e:
        print(f"❌ Erreur signal challenge progress: {e}")
        import traceback
        traceback.print_exc()

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
                
                # 🎯 NOUVEAU: Créer un StudentTestResult pour la gamification
                try:
                    from .models import StudentTestResult, Challenge
                    from evaluation.models import UserProfile
                    from .services import ChallengeService
                    
                    # Vérifier si le profil existe (utiliser UserProfile de evaluation)
                    profile, created_profile = UserProfile.objects.get_or_create(user=instance.student)
                    
                    # Créer un StudentTestResult pour la gamification
                    test_result = StudentTestResult.objects.create(
                        student=instance.student,
                        subject=subject,
                        test_name=test_name,
                        score=score,
                        test_id=str(instance.test.pk) if hasattr(instance, 'test') and instance.test else None
                    )
                    print(f"✅ StudentTestResult créé pour gamification: {test_name} - {score}%")
                    
                    # Trouver les défis actifs de l'étudiant
                    active_challenges = Challenge.objects.filter(
                        student=instance.student,
                        status='ACTIVE',
                        expires_at__gte=timezone.now()
                    )
                    
                    print(f"🔍 Défis actifs trouvés: {active_challenges.count()}")
                    
                    if active_challenges.count() == 0:
                        print(f"⚠️ Aucun défi actif pour {instance.student.username}")
                    
                    challenge_service = ChallengeService()
                    
                    for challenge in active_challenges:
                        # Vérifier si le défi correspond à la matière du test
                        challenge_subject = challenge.target_data.get('subject', challenge.subject or '')
                        
                        # Correspondance plus souple des matières
                        subject_match = (
                            not challenge_subject or  # Défi sans matière spécifique
                            challenge_subject.lower() in subject.lower() or 
                            subject.lower() in challenge_subject.lower()
                        )
                        
                        if subject_match:
                            # Compter les tests complétés pour cette matière (ou tous si pas de matière)
                            if challenge_subject:
                                exercises_completed = StudentTestResult.objects.filter(
                                    student=instance.student,
                                    subject__icontains=challenge_subject,
                                    completed_at__gte=challenge.created_at
                                ).count()
                            else:
                                exercises_completed = StudentTestResult.objects.filter(
                                    student=instance.student,
                                    completed_at__gte=challenge.created_at
                                ).count()
                            
                            print(f"📊 Challenge '{challenge.title}': {exercises_completed} exercices complétés")
                            
                            # Mettre à jour la progression du défi
                            updated_challenge = challenge_service.update_challenge_progress(
                                challenge=challenge,
                                exercises_completed=exercises_completed,
                                current_score=score
                            )
                            
                            print(f"✅ Défi mis à jour: {challenge.title} - Progression: {updated_challenge.current_progress}%")
                            
                            # Vérifier si le défi est complété
                            if updated_challenge.status == 'COMPLETED':
                                print(f"🎉 DÉFI COMPLÉTÉ ! {challenge.title} - XP: {challenge.xp_reward}, Coins: {challenge.coins_reward}")
                        else:
                            print(f"⏭️ Défi '{challenge.title}' (matière: {challenge_subject}) ne correspond pas à {subject}")
                    
                    # Mettre à jour le profil - XP automatique pour complétion de test
                    base_xp = int(score / 10)  # 1 XP par 10% de score
                    if score >= 80:
                        base_xp += 20  # Bonus pour excellence
                    elif score >= 60:
                        base_xp += 10  # Bonus pour réussite
                    
                    # Ajouter XP et calculer le niveau
                    old_xp = profile.total_xp
                    profile.total_xp += base_xp
                    new_level = (profile.total_xp // 100) + 1
                    level_up = new_level > profile.level
                    profile.level = new_level
                    profile.updated_at = timezone.now()
                    profile.save()
                    
                    print(f"💫 XP ajoutés au profil: +{base_xp} XP (Total: {profile.total_xp})")
                    if level_up:
                        print(f"🎊 LEVEL UP ! Nouveau niveau: {profile.level}")
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors de la mise à jour des défis de gamification: {e}")
                    import traceback
                    traceback.print_exc()
                    
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

# 🎯 Signal pour les exercices IA (StudentExerciseSubmission)
try:
    from exercise_generator.models import StudentExerciseSubmission
    EXERCISE_GENERATOR_AVAILABLE = True
except ImportError:
    StudentExerciseSubmission = None
    EXERCISE_GENERATOR_AVAILABLE = False

if EXERCISE_GENERATOR_AVAILABLE and StudentExerciseSubmission:
    @receiver(post_save, sender=StudentExerciseSubmission)
    def track_exercise_submission(sender, instance, created, **kwargs):
        """Tracker automatiquement les soumissions d'exercices IA pour la gamification"""
        # Se déclencher seulement quand l'exercice est complété
        if instance.is_completed and instance.student and not instance.student.is_staff:
            try:
                print(f"✅ Signal déclenché pour StudentExerciseSubmission")
                print(f"   Étudiant: {instance.student.username}")
                print(f"   Set: {instance.exercise_set.title if instance.exercise_set else 'Unknown'}")
                print(f"   Score: {instance.score}%")
                
                # Importer les modèles nécessaires
                from .models import StudentTestResult, Challenge
                from evaluation.models import UserProfile
                from .services import ChallengeService
                
                # Récupérer la matière du set d'exercices
                subject = "General"
                if instance.exercise_set and hasattr(instance.exercise_set, 'subject'):
                    subject = instance.exercise_set.subject or "General"
                
                # Récupérer le titre
                test_name = "Exercice IA"
                if instance.exercise_set and hasattr(instance.exercise_set, 'title'):
                    test_name = instance.exercise_set.title
                
                # Créer l'entrée StudentTestResult pour le tracking
                test_result, result_created = StudentTestResult.objects.get_or_create(
                    student=instance.student,
                    subject=subject,
                    test_name=test_name,
                    defaults={'score': instance.score}
                )
                
                if not result_created:
                    # Mettre à jour le score si déjà existant
                    test_result.score = instance.score
                    test_result.save()
                
                print(f"✅ StudentTestResult créé/mis à jour: {test_name} - {instance.score}%")
                
                # Récupérer le profil de l'utilisateur (UserProfile)
                profile, created_profile = UserProfile.objects.get_or_create(
                    user=instance.student,
                    defaults={
                        'role': 'student',
                        'level': 1,
                        'total_xp': 0
                    }
                )
                if created_profile:
                    print(f"🆕 Profil gamifié créé pour {instance.student.username}")
                
                score = instance.score
                
                # Mettre à jour le profil - XP automatique pour complétion d'exercice
                base_xp = int(score / 10)  # 1 XP par 10% de score
                if score >= 80:
                    base_xp += 20  # Bonus pour excellence
                elif score >= 60:
                    base_xp += 10  # Bonus pour réussite
                
                # Ajouter XP et calculer le niveau
                old_xp = profile.total_xp
                profile.total_xp += base_xp
                new_level = (profile.total_xp // 100) + 1
                level_up = new_level > profile.level
                profile.level = new_level
                profile.updated_at = timezone.now()
                profile.save()
                
                print(f"💫 XP ajoutés au profil: +{base_xp} XP (Total: {profile.total_xp})")
                if level_up:
                    print(f"🎊 LEVEL UP ! Nouveau niveau: {profile.level}")
                
                # Rechercher les challenges actifs qui correspondent à l'exercice
                active_challenges = Challenge.objects.filter(
                    student=instance.student,
                    status='ACTIVE',
                    expires_at__gte=timezone.now()
                ).select_related('student')
                
                print(f"🔍 Challenges actifs trouvés: {active_challenges.count()}")
                
                if active_challenges.count() == 0:
                    print(f"⚠️ Aucun challenge actif pour {instance.student.username}")
                
                challenge_service = ChallengeService()
                
                for challenge in active_challenges:
                    # Vérifier si le challenge correspond à la matière de l'exercice
                    challenge_subject = challenge.target_data.get('subject', challenge.subject or '') if challenge.target_data else challenge.subject or ''
                    
                    # Correspondance plus souple des matières
                    subject_match = (
                        not challenge_subject or  # Challenge sans matière spécifique
                        challenge_subject.lower() in subject.lower() or 
                        subject.lower() in challenge_subject.lower()
                    )
                    
                    if subject_match:
                        # Compter les exercices complétés pour cette matière (ou tous si pas de matière)
                        if challenge_subject:
                            exercises_completed = StudentTestResult.objects.filter(
                                student=instance.student,
                                subject__icontains=challenge_subject,
                                completed_at__gte=challenge.created_at
                            ).count()
                        else:
                            exercises_completed = StudentTestResult.objects.filter(
                                student=instance.student,
                                completed_at__gte=challenge.created_at
                            ).count()
                        
                        print(f"📊 Challenge '{challenge.title}': {exercises_completed} exercices complétés")
                        
                        # Mettre à jour la progression du challenge
                        updated_challenge = challenge_service.update_challenge_progress(
                            challenge=challenge,
                            exercises_completed=exercises_completed,
                            current_score=score
                        )
                        
                        print(f"✅ Challenge mis à jour: {challenge.title} - Progression: {updated_challenge.current_progress}%")
                        
                        # Vérifier si le challenge est complété
                        if updated_challenge.status == 'COMPLETED':
                            print(f"🎉 CHALLENGE COMPLÉTÉ ! {challenge.title} - XP: {challenge.xp_reward}, Coins: {challenge.coins_reward}")
                    else:
                        print(f"⏭️ Challenge '{challenge.title}' (matière: {challenge_subject}) ne correspond pas à {subject}")
                
                print(f"✅ Gamification mise à jour avec succès pour l'exercice IA !")
                
            except Exception as e:
                print(f"❌ Erreur dans le signal track_exercise_submission: {e}")
                import traceback
                traceback.print_exc()


# 🎯 SIGNAL CRITIQUE POUR LES RÉSULTATS DE TESTS (evaluation.Result)
try:
    from evaluation.models import Result
    RESULT_MODEL_AVAILABLE = True
except ImportError:
    Result = None
    RESULT_MODEL_AVAILABLE = False

if RESULT_MODEL_AVAILABLE and Result:
    @receiver(post_save, sender=Result)
    def track_test_result_for_gamification(sender, instance, created, **kwargs):
        """
        Signal pour tracker les résultats de tests et mettre à jour la gamification.
        Ce signal se déclenche quand un Result (résultat de test) est créé.
        """
        if not created:
            return
        
        try:
            print(f"\n🎯 === SIGNAL TEST RESULT GAMIFICATION === ")
            print(f"   Student: {instance.student.username}")
            print(f"   Test: {instance.test.title if instance.test else 'N/A'}")
            print(f"   Score: {instance.percentage_score}%")
            
            # Importer les modèles nécessaires
            from .models import StudentTestResult, Challenge
            from evaluation.models import UserProfile
            from .services import ChallengeService
            from evaluation.utils import get_or_create_user_profile_safe
            
            student = instance.student
            test = instance.test
            score = instance.percentage_score or 0
            subject = test.subject if test and hasattr(test, 'subject') else 'Général'
            test_name = test.title if test else 'Test'
            
            # 1. Récupérer/créer le profil utilisateur (avec gestion des duplicatas)
            profile = get_or_create_user_profile_safe(student)
            print(f"   ✅ Profil trouvé: {profile.role}, Level: {profile.level}")
            
            # 2. Ajouter des XP basés sur le score
            xp_base = 20  # XP de base pour avoir complété un test
            xp_bonus = int(score / 5)  # Bonus XP basé sur le score (max 20 XP pour 100%)
            xp_gained = xp_base + xp_bonus
            
            old_xp = profile.total_xp or 0
            profile.total_xp = old_xp + xp_gained
            profile.save()
            
            print(f"   💫 XP ajoutés: +{xp_gained} (base: {xp_base} + bonus: {xp_bonus})")
            print(f"   📊 XP total: {old_xp} → {profile.total_xp}")
            
            # 3. Créer un StudentTestResult pour la gamification
            test_result = StudentTestResult.objects.create(
                student=student,
                subject=subject,
                test_name=test_name,
                score=score,
                test_id=str(test.pk) if test else None
            )
            print(f"   ✅ StudentTestResult créé: ID={test_result.id}")
            
            # 4. Mettre à jour les défis actifs
            active_challenges = Challenge.objects.filter(
                student=student,
                status='ACTIVE',
                expires_at__gte=timezone.now()
            )
            
            print(f"   🎯 Défis actifs: {active_challenges.count()}")
            
            if active_challenges.count() == 0:
                print(f"   ⚠️ Aucun défi actif pour {student.username}")
                # Créer des défis par défaut si aucun n'existe
                try:
                    challenge_service = ChallengeService()
                    new_challenges = challenge_service.generate_daily_challenges(student)
                    print(f"   ✅ {len(new_challenges)} nouveaux défis créés automatiquement")
                    active_challenges = Challenge.objects.filter(
                        student=student,
                        status='ACTIVE',
                        expires_at__gte=timezone.now()
                    )
                except Exception as e:
                    print(f"   ⚠️ Impossible de créer les défis: {e}")
            
            # Mettre à jour chaque défi actif
            challenge_service = ChallengeService()
            
            for challenge in active_challenges:
                challenge_subject = challenge.target_data.get('subject', challenge.subject or '')
                
                # Correspondance flexible des matières
                subject_match = (
                    not challenge_subject or  # Défi général
                    challenge_subject.lower() in subject.lower() or 
                    subject.lower() in challenge_subject.lower()
                )
                
                if subject_match:
                    # Compter les tests complétés depuis le début du défi
                    if challenge_subject:
                        tests_completed = StudentTestResult.objects.filter(
                            student=student,
                            subject__icontains=challenge_subject,
                            completed_at__gte=challenge.created_at
                        ).count()
                    else:
                        tests_completed = StudentTestResult.objects.filter(
                            student=student,
                            completed_at__gte=challenge.created_at
                        ).count()
                    
                    old_progress = challenge.current_progress
                    
                    # Mettre à jour la progression
                    updated_challenge = challenge_service.update_challenge_progress(
                        challenge=challenge,
                        exercises_completed=tests_completed,
                        current_score=score
                    )
                    
                    print(f"   📈 Défi '{challenge.title}': {old_progress}% → {updated_challenge.current_progress}%")
                    
                    if updated_challenge.status == 'COMPLETED':
                        print(f"   🎉 DÉFI COMPLÉTÉ! {challenge.title}")
                        print(f"      Récompenses: +{challenge.xp_reward} XP, +{challenge.coins_reward} coins")
                else:
                    print(f"   ⏭️ Défi '{challenge.title}' ({challenge_subject}) ne correspond pas à {subject}")
            
            # 5. Mettre à jour le tracking service
            tracking_result = tracking_service.record_test_completion(
                student=student,
                test_name=test_name,
                score=score,
                subject=subject
            )
            
            if tracking_result['success']:
                print(f"   ✅ Tracking enregistré avec succès")
            else:
                print(f"   ⚠️ Erreur tracking: {tracking_result.get('error')}")
            
            print(f"   ✅ === GAMIFICATION MISE À JOUR === \n")
            
        except Exception as e:
            print(f"   ❌ ERREUR dans signal Result: {e}")
            import traceback
            traceback.print_exc()
