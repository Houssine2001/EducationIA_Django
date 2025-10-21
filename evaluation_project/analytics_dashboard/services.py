from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
import random
import json
import math

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
from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel, PerformanceTrend


class AnalyticsService:
    """Service pour calculer et mettre à jour les analytics des étudiants"""
    
    def update_student_analytics(self, student):
        """Met à jour les analytics d'un étudiant avec des données réelles"""
        analytics, created = StudentAnalytics.objects.get_or_create(
            user=student,
            defaults={
                'student_name': f"{student.first_name} {student.last_name}" or student.username,
                'student_email': student.email,
            }
        )
        
        # Utiliser les données réelles de PerformanceTrend si disponibles
        trends = PerformanceTrend.objects.filter(student=student)
        
        if trends.exists():
            # Calculer à partir des données réelles
            scores = [trend.score for trend in trends]
            analytics.total_exercises = len(scores)
            analytics.completed_exercises = len([score for score in scores if score >= 50])
            analytics.average_score = sum(scores) / len(scores)
            analytics.success_rate = (analytics.completed_exercises / analytics.total_exercises * 100) if analytics.total_exercises > 0 else 0.0
            
            # Métriques avancées basées sur les données réelles
            analytics.learning_velocity = self._calculate_real_velocity(scores)
            analytics.consistency_score = self._calculate_real_consistency(scores)
            analytics.engagement_score = self._calculate_real_engagement(student)
            analytics.risk_level = self._calculate_risk_level(analytics)
        else:
            # Fallback avec données simulées réalistes
            analytics.total_exercises = random.randint(10, 50)
            analytics.completed_exercises = random.randint(5, analytics.total_exercises)
            analytics.average_score = round(random.uniform(60, 95), 2)
            analytics.success_rate = round(analytics.completed_exercises / analytics.total_exercises * 100, 2)
            analytics.learning_velocity = self._calculate_learning_velocity(student)
            analytics.consistency_score = self._calculate_consistency(student)
            analytics.engagement_score = self._calculate_engagement(student)
            analytics.risk_level = self._calculate_risk_level(analytics)
        
        analytics.last_activity = timezone.now()
        analytics.save()
        
        return analytics
    
    def _calculate_real_velocity(self, scores):
        """Calcule la vitesse d'apprentissage réelle basée sur la régression linéaire simple"""
        if len(scores) < 3:
            return 0.0
        
        try:
            n = len(scores)
            sum_x = sum(range(n))
            sum_y = sum(scores)
            sum_xy = sum(i * score for i, score in enumerate(scores))
            sum_x2 = sum(i * i for i in range(n))
            
            # Calcul de la pente (régression linéaire simple)
            velocity = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return round(velocity, 3)
        except:
            return 0.0
    
    def _calculate_real_consistency(self, scores):
        """Calcule la régularité réelle basée sur l'écart-type normalisé"""
        if len(scores) < 2:
            return 1.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Coefficient de variation inversé (plus il est bas, plus c'est régulier)
        if mean_score > 0:
            cv = std_dev / mean_score
            consistency = max(0.0, 1.0 - cv)
        else:
            consistency = 0.0
        
        return round(consistency, 3)
    
    def _calculate_real_engagement(self, student):
        """Calcule l'engagement basé sur la fréquence des activités"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_trends = PerformanceTrend.objects.filter(
            student=student,
            date__gte=thirty_days_ago
        )
        
        # Engagement basé sur la fréquence d'activité
        unique_dates = set()
        for trend in recent_trends:
            unique_dates.add(trend.date.date())
        
        days_active = len(unique_dates)
        engagement = min(1.0, days_active / 30.0)
        
        return round(engagement, 3)
    
    def _calculate_learning_velocity(self, student):
        """Calcule la vitesse d'apprentissage (fallback)"""
        return round(random.uniform(0.5, 2.0), 2)
    
    def _calculate_consistency(self, student):
        """Calcule le score de régularité (fallback)"""
        return round(random.uniform(0.3, 1.0), 2)
    
    def _calculate_engagement(self, student):
        """Calcule le score d'engagement (fallback)"""
        return round(random.uniform(0.4, 1.0), 2)
    
    def _calculate_risk_level(self, analytics):
        """Détermine le niveau de risque basé sur plusieurs métriques"""
        score = analytics.average_score
        success_rate = analytics.success_rate
        engagement = analytics.engagement_score
        
        # Pondération des facteurs
        risk_score = (
            (100 - score) * 0.4 +  # 40% pour le score moyen
            (100 - success_rate) * 0.3 +  # 30% pour le taux de réussite
            (1 - engagement) * 100 * 0.3  # 30% pour l'engagement
        )
        
        if risk_score <= 20:
            return 'LOW'
        elif risk_score <= 40:
            return 'MEDIUM'
        elif risk_score <= 60:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def get_comprehensive_student_data(self, student):
        """Récupère toutes les données d'un étudiant pour les 3 modules analytics"""
        from .models import SubjectAnalytics, SubjectTestResult
        
        # Mise à jour des analytics
        analytics = self.update_student_analytics(student)
        
        # Récupérer les performances par matière
        subject_analytics = SubjectAnalytics.objects.filter(student=student)
        
        # Récupérer l'historique de performances
        performance_trends = PerformanceTrend.objects.filter(
            student=student
        ).order_by('-date')[:30]
        
        # Calculer les matières fortes et faibles
        subjects_data = {}
        for subject_analytic in subject_analytics:
            subjects_data[subject_analytic.subject_name] = {
                'average_score': subject_analytic.average_score,
                'tests_count': subject_analytic.tests_count,
                'success_rate': subject_analytic.success_rate,
                'last_activity': subject_analytic.last_test_date
            }
        
        # Identifier matière forte et faible
        if subjects_data:
            strongest_subject = max(subjects_data.items(), key=lambda x: x[1]['average_score'])
            weakest_subject = min(subjects_data.items(), key=lambda x: x[1]['average_score'])
        else:
            strongest_subject = ('Aucune', {'average_score': 0})
            weakest_subject = ('Aucune', {'average_score': 0})
        
        # Calculer les métriques d'engagement
        current_streak = getattr(analytics, 'current_streak', 0)
        total_study_time = getattr(analytics, 'study_time_minutes', 0)
        
        return {
            'student_analytics': analytics,
            'performance_history': performance_trends,
            'subjects_data': subjects_data,
            'strongest_subject': strongest_subject,
            'weakest_subject': weakest_subject,
            'current_streak': current_streak,
            'total_study_time': total_study_time,
            'chart_data': {
                'labels': [trend.date.strftime('%d/%m') for trend in performance_trends],
                'scores': [trend.score for trend in performance_trends],
                'subjects': [trend.subject for trend in performance_trends]
            }
        }


class PredictionService:
    def __init__(self):
        self.analytics_service = AnalyticsService()
    
    def generate_real_prediction(self, student):
        """
        Génère une prédiction IA RÉALISTE basée sur les vraies données
        """
        from .models import StudentAnalytics, PerformanceTrend, PredictionModel
        
        # 1. Récupérer les données réelles
        try:
            analytics = StudentAnalytics.objects.get(user=student)
        except StudentAnalytics.DoesNotExist:
            # Créer des analytics vides si inexistants
            analytics = StudentAnalytics.objects.create(
                user=student,
                student_name=f"{student.first_name} {student.last_name}".strip() or student.username,
                student_email=student.email,
                average_score=0,
                total_exercises=0,
                study_time_minutes=0,
                current_streak=0
            )
        
        # 2. Récupérer l'historique de performances
        performance_trends = PerformanceTrend.objects.filter(
            student=student
        ).order_by('-date')[:10]  # 10 derniers tests
        
        # 3. CALCUL RÉALISTE DE LA PRÉDICTION
        
        # A. Score moyen actuel (0-100)
        current_score = analytics.average_score if analytics.average_score <= 100 else analytics.average_score * 5
        
        # B. Tendance récente (si l'étudiant progresse ou régresse)
        trend_factor = self._calculate_trend(performance_trends)
        
        # C. Engagement - Calculer manuellement
        engagement_factor = self._calculate_engagement(analytics, performance_trends)
        
        # D. Consistance (si l'étudiant a des résultats stables)
        consistency_factor = self._calculate_consistency(performance_trends)
        
        # E. Nombre de tests (plus de tests = prédiction plus fiable)
        # 🔧 CORRECTION: Convertir en liste pour éviter COUNT() sur LIMIT
        trends = list(performance_trends)
        total_tests = len(trends)
        test_count_factor = min(total_tests / 10, 1.0)  # Max à 10 tests
        
        # 4. FORMULE DE PRÉDICTION RÉALISTE
        
        # Score de base = score actuel
        base_prediction = current_score
        
        # Ajustement selon la tendance (-10 à +10 points)
        trend_adjustment = trend_factor * 10
        
        # Ajustement selon l'engagement (-5 à +5 points)
        engagement_adjustment = (engagement_factor - 0.5) * 10
        
        # Ajustement selon la consistance (-5 à +5 points)
        consistency_adjustment = (consistency_factor - 0.5) * 10
        
        # Prédiction finale
        predicted_score = base_prediction + trend_adjustment + engagement_adjustment + consistency_adjustment
        
        # Limiter entre 0 et 100
        predicted_score = max(0, min(100, predicted_score))
        
        # 5. CALCUL DE LA CONFIANCE
        
        confidence = (
            test_count_factor * 0.4 +      # 40% basé sur le nombre de tests
            consistency_factor * 0.3 +      # 30% basé sur la consistance
            engagement_factor * 0.3         # 30% basé sur l'engagement
        ) * 100
        
        # Confiance minimum de 20%, maximum de 95%
        confidence = max(20, min(95, confidence))
        
        # 6. SAUVEGARDER LA PRÉDICTION
        # 🔧 CORRECTION: Utiliser les champs corrects du modèle PredictionModel
        prediction, created = PredictionModel.objects.get_or_create(
            student=student,
            prediction_type='overall_performance',
            defaults={
                'prediction_value': round(predicted_score, 1),
                'confidence': round(confidence, 1),
                'raw_data': {
                    'predicted_score': round(predicted_score, 1),
                    'confidence_level': round(confidence, 1),
                    'based_on_tests': total_tests,
                    'current_average': analytics.average_score,
                    'trend': trend_factor,
                    'engagement': engagement_factor,
                    'consistency': consistency_factor
                }
            }
        )
        
        if not created:
            # Mettre à jour si existe déjà
            prediction.prediction_value = round(predicted_score, 1)
            prediction.confidence = round(confidence, 1)
            prediction.raw_data = {
                'predicted_score': round(predicted_score, 1),
                'confidence_level': round(confidence, 1),
                'based_on_tests': total_tests,
                'current_average': analytics.average_score,
                'trend': trend_factor,
                'engagement': engagement_factor,
                'consistency': consistency_factor
            }
            prediction.save()
        
        return {
            'predicted_score': round(predicted_score, 1),
            'confidence': round(confidence, 1),
            'current_score': round(current_score, 1),
            'trend': trend_factor,
            'engagement': engagement_factor,
            'consistency': consistency_factor
        }
    
    def _calculate_engagement(self, analytics, performance_trends):
        """
        Calcule l'engagement de l'étudiant (0 à 1)
        Basé sur : nombre de tests, temps d'étude, régularité
        """
        # 🔧 CORRECTION: Convertir en liste pour éviter COUNT() sur LIMIT
        trends = list(performance_trends)
        
        # Facteur 1: Nombre de tests (0-1)
        total_tests = len(trends)
        test_factor = min(total_tests / 20, 1.0)  # 20 tests = engagement max
        
        # Facteur 2: Temps d'étude (0-1)
        study_time_hours = getattr(analytics, 'study_time_minutes', 0) / 60
        time_factor = min(study_time_hours / 50, 1.0)  # 50h = engagement max
        
        # Facteur 3: Streak actuel (0-1)
        current_streak = getattr(analytics, 'current_streak', 0)
        streak_factor = min(current_streak / 14, 1.0)  # 14 jours = engagement max
        
        # Facteur 4: Régularité récente (0-1)
        regularity_factor = self._calculate_regularity(performance_trends)
        
        # Moyenne pondérée
        engagement = (
            test_factor * 0.3 +        # 30% nombre de tests
            time_factor * 0.2 +         # 20% temps d'étude
            streak_factor * 0.2 +       # 20% streak
            regularity_factor * 0.3     # 30% régularité
        )
        
        return max(0, min(1, engagement))
    
    def _calculate_regularity(self, performance_trends):
        """
        Calcule la régularité de l'étudiant (0 à 1)
        1 = très régulier (tests espacés uniformément)
        0 = irrégulier (longues pauses)
        """
        # 🔧 CORRECTION: Convertir en liste pour éviter COUNT() sur LIMIT
        trends = list(performance_trends)
        
        if len(trends) < 2:
            return 0.5  # Neutre
        
        # Calculer les intervalles entre les tests
        intervals = []
        
        for i in range(len(trends) - 1):
            delta = (trends[i].date - trends[i+1].date).days
            intervals.append(delta)
        
        if not intervals:
            return 0.5
        
        # Calculer l'écart-type des intervalles
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # Normaliser : moins d'écart-type = plus régulier
        # On considère qu'un écart-type de 7 jours est acceptable
        regularity = 1 - min(std_dev / 7, 1)
        
        return max(0, min(1, regularity))
    
    def _calculate_trend(self, performance_trends):
        """
        Calcule la tendance de progression (-1 à +1)
        -1 = forte régression
         0 = stable
        +1 = forte progression
        """
        # 🔧 CORRECTION: Convertir en liste pour éviter COUNT() sur LIMIT
        trends = list(performance_trends)
        
        if len(trends) < 2:
            return 0  # Pas assez de données
        
        if len(trends) < 4:
            # Trop peu de données, calculer simplement la pente
            first_score = trends[-1].score
            last_score = trends[0].score
            diff = last_score - first_score
            return max(-1, min(1, diff / 10))  # Normaliser entre -1 et 1
        
        # Séparer en deux groupes
        recent_tests = trends[:len(trends)//2]
        older_tests = trends[len(trends)//2:]
        
        # Moyenne de chaque groupe
        recent_avg = sum(t.score for t in recent_tests) / len(recent_tests) if recent_tests else 0
        older_avg = sum(t.score for t in older_tests) / len(older_tests) if older_tests else 0
        
        # Calculer la tendance
        diff = recent_avg - older_avg
        
        # Normaliser entre -1 et 1
        return max(-1, min(1, diff / 10))
    
    def _calculate_consistency(self, performance_trends):
        """
        Calcule la consistance des résultats (0 à 1)
        0 = très inconsistant (grandes variations)
        1 = très consistant (résultats stables)
        """
        # 🔧 CORRECTION: Convertir en liste pour éviter COUNT() sur LIMIT
        trends = list(performance_trends)
        
        if len(trends) < 2:
            return 0.5  # Neutre si pas assez de données
        
        scores = [t.score for t in trends]
        
        # Calculer l'écart-type
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Normaliser l'écart-type (0 = parfait, 5 = très variable)
        # On inverse pour avoir 1 = consistant
        consistency = 1 - min(std_dev / 5, 1)
        
        return max(0, min(1, consistency))
    
    def generate_predictions(self, student):
        """Génère des prédictions pour un étudiant (méthode legacy)"""
        return self.generate_real_prediction(student)


class ReportService:
    """Service pour générer des rapports détaillés"""
    
    def generate_student_report(self, student):
        """Génère un rapport détaillé pour un étudiant"""
        analytics = StudentAnalytics.objects.filter(user=student).first()
        prediction = PredictionModel.objects.filter(student=student).first()
        
        report_data = {
            'student_id': student.id,
            'student_name': student.get_full_name(),
            'generated_at': timezone.now().isoformat(),
            'analytics_summary': {
                'average_score': analytics.average_score if analytics else 0,
                'success_rate': analytics.success_rate if analytics else 0,
                'risk_level': analytics.risk_level if analytics else 'UNKNOWN',
                'engagement': getattr(analytics, 'engagement_score', 0) if analytics else 0,
                'learning_velocity': getattr(analytics, 'learning_velocity', 0) if analytics else 0
            },
            'predictions': prediction.raw_data if prediction and isinstance(prediction.raw_data, dict) else (json.loads(prediction.raw_data) if prediction and prediction.raw_data else {}),
            'performance_history': self._get_performance_history(student)
        }
        
        report = AnalyticsReport.objects.create(
            title=f"Rapport Analytics IA - {student.get_full_name()}",
            report_type='STUDENT',
            generated_by=student,
            data=json.dumps(report_data),
            status='COMPLETED'
        )
        
        return report
    
    def _get_performance_history(self, student):
        """Récupère l'historique de performance"""
        trends = PerformanceTrend.objects.filter(student=student).order_by('date')[:30]
        return [
            {
                'date': trend.date.isoformat(),
                'score': trend.score,
                'subject': trend.subject
            }
            for trend in trends
        ]


# ============================================================
# 🎮 SYSTÈME GAMIFIÉ - SERVICES
# ============================================================

class ChallengeService:
    """Service pour gérer les défis personnalisés"""
    
    def generate_daily_challenges(self, student):
        """
        Génère 3 défis quotidiens personnalisés basés sur l'IA
        - 1 défi FACILE (zone de confort)
        - 1 défi MOYEN (zone d'apprentissage)  
        - 1 défi DIFFICILE (zone de défi)
        """
        from .models import (
            StudentAnalytics, PerformanceTrend, SubjectAnalytics, 
            Challenge, StudentProfile
        )
        
        # S'assurer que le profil gamifié existe
        profile, _ = StudentProfile.objects.get_or_create(user=student)
        
        # Récupérer les données de performance
        analytics = StudentAnalytics.objects.filter(user=student).first()
        if not analytics:
            return self._generate_beginner_challenges(student)
        
        performance_trends = list(PerformanceTrend.objects.filter(
            student=student
        ).order_by('-date')[:10])
        
        subject_analytics = SubjectAnalytics.objects.filter(user=student)
        
        challenges_data = []
        
        # 1. DÉFI FACILE - Renforcer les acquis
        strong_subjects = subject_analytics.filter(average_test_score__gte=70).order_by('-average_test_score')
        if strong_subjects.exists():
            subject = strong_subjects.first()
            challenge = Challenge.objects.create(
                student=student,
                title=f'🌟 Maître de {subject.subject_name}',
                description=f'Réussir 5 exercices de {subject.subject_name} avec plus de 80%',
                difficulty='EASY',
                subject=subject.subject_name,
                target_data={
                    'exercises_count': 5,
                    'min_score': 80,
                    'time_limit_minutes': 30
                },
                xp_reward=50,
                coins_reward=20,
                badge_reward='Expert Confirmé',
                expires_at=timezone.now() + timedelta(days=1),
                tips=[
                    'Commencez par réviser les concepts de base',
                    'Prenez votre temps sur chaque exercice',
                    'Validez vos réponses avant de soumettre'
                ]
            )
            challenges_data.append(challenge)
        
        # 2. DÉFI MOYEN - Zone d'apprentissage
        medium_subjects = subject_analytics.filter(
            average_test_score__gte=50,
            average_test_score__lt=70
        )
        if medium_subjects.exists():
            subject = medium_subjects.first()
            improvement_target = subject.average_test_score + 10
            challenge = Challenge.objects.create(
                student=student,
                title=f'📚 Progresser en {subject.subject_name}',
                description=f'Améliorer votre score de 10% en {subject.subject_name}',
                difficulty='MEDIUM',
                subject=subject.subject_name,
                target_data={
                    'improvement_percentage': 10,
                    'exercises_count': 7,
                    'min_score': improvement_target,
                    'time_limit_minutes': 45
                },
                xp_reward=100,
                coins_reward=50,
                badge_reward='En Progression',
                expires_at=timezone.now() + timedelta(days=1),
                tips=[
                    'Concentrez-vous sur vos erreurs récentes',
                    'Utilisez des ressources d\'aide si nécessaire',
                    'Pratiquez les exercices types'
                ]
            )
            challenges_data.append(challenge)
        
        # 3. DÉFI DIFFICILE - Sortir de sa zone de confort
        weak_subjects = subject_analytics.filter(average_test_score__lt=50).order_by('average_test_score')
        if weak_subjects.exists():
            subject = weak_subjects.first()
            challenge = Challenge.objects.create(
                student=student,
                title=f'💪 Défi {subject.subject_name}',
                description=f'Surmonter vos difficultés en {subject.subject_name}',
                difficulty='HARD',
                subject=subject.subject_name,
                target_data={
                    'exercises_count': 3,
                    'min_score': 60,
                    'allow_help': True,
                    'time_limit_minutes': 60
                },
                xp_reward=200,
                coins_reward=100,
                badge_reward='Persévérant',
                expires_at=timezone.now() + timedelta(days=1),
                tips=[
                    'Ne vous découragez pas !',
                    'Demandez de l\'aide si besoin',
                    'Chaque erreur est une opportunité d\'apprendre',
                    'Prenez des pauses entre les exercices'
                ],
                motivational_quote=self._get_motivational_quote()
            )
            challenges_data.append(challenge)
        
        return challenges_data
    
    def _generate_beginner_challenges(self, student):
        """Génère des défis pour débutants"""
        from .models import Challenge
        
        challenges = []
        
        # Défi d'initiation
        challenge = Challenge.objects.create(
            student=student,
            title='🎯 Premier Pas',
            description='Complétez votre premier exercice',
            difficulty='EASY',
            target_data={'exercises_count': 1, 'min_score': 50},
            xp_reward=30,
            coins_reward=10,
            badge_reward='Nouveau Venu',
            expires_at=timezone.now() + timedelta(days=2),
            tips=['Prenez votre temps', 'Lisez bien les instructions']
        )
        challenges.append(challenge)
        
        return challenges
    
    def _get_motivational_quote(self):
        """Retourne une citation motivante aléatoire"""
        quotes = [
            "Le succès n'est pas final, l'échec n'est pas fatal : c'est le courage de continuer qui compte.",
            "La seule façon d'apprendre les mathématiques est de faire des mathématiques.",
            "Chaque expert était autrefois un débutant.",
            "L'éducation est l'arme la plus puissante pour changer le monde.",
            "Le génie, c'est 1% d'inspiration et 99% de transpiration.",
        ]
        return random.choice(quotes)
    
    def update_challenge_progress(self, challenge, exercises_completed, current_score):
        """Met à jour la progression d'un défi"""
        target = challenge.target_data
        
        # Calculer la progression
        progress = 0
        if 'exercises_count' in target:
            exercises_progress = (exercises_completed / target['exercises_count']) * 100
            progress = min(exercises_progress, 100)
        
        challenge.current_progress = progress
        challenge.progress_data = {
            'exercises_completed': exercises_completed,
            'current_score': current_score,
            'updated_at': timezone.now().isoformat()
        }
        
        # Vérifier la complétion
        if challenge.check_completion():
            self._reward_challenge_completion(challenge)
        
        challenge.save()
        return challenge
    
    def _reward_challenge_completion(self, challenge):
        """Distribue les récompenses d'un défi complété"""
        from .models import StudentProfile
        
        profile = StudentProfile.objects.get(user=challenge.student)
        
        # Ajouter XP
        level_up = profile.add_xp(challenge.xp_reward)
        
        # Ajouter coins
        profile.coins += challenge.coins_reward
        
        # Ajouter badge
        if challenge.badge_reward:
            profile.add_badge(challenge.badge_reward)
        
        # Mettre à jour les stats
        profile.challenges_completed += 1
        
        # Vérifier le streak
        self._update_streak(profile)
        
        profile.save()
        
        return {
            'level_up': level_up,
            'new_level': profile.level if level_up else None,
            'xp_earned': challenge.xp_reward,
            'coins_earned': challenge.coins_reward,
            'badge_earned': challenge.badge_reward
        }
    
    def _update_streak(self, profile):
        """Met à jour le streak de l'étudiant"""
        today = timezone.now().date()
        last_activity = profile.last_activity.date() if profile.last_activity else None
        
        if last_activity:
            days_diff = (today - last_activity).days
            
            if days_diff == 1:
                # Continuation du streak
                profile.current_streak += 1
                if profile.current_streak > profile.longest_streak:
                    profile.longest_streak = profile.current_streak
            elif days_diff > 1:
                # Streak cassé
                profile.current_streak = 1
        else:
            profile.current_streak = 1


class WeeklyMissionService:
    """Service pour gérer les missions hebdomadaires"""
    
    def generate_weekly_mission(self, student):
        """Génère une mission hebdomadaire ambitieuse"""
        from .models import StudentAnalytics, WeeklyMission
        
        analytics = StudentAnalytics.objects.filter(user=student).first()
        if not analytics:
            return None
        
        # Calculer la semaine actuelle
        now = timezone.now()
        week_number = now.isocalendar()[1]
        year = now.year
        
        # Vérifier si une mission existe déjà pour cette semaine
        existing = WeeklyMission.objects.filter(
            student=student,
            week_number=week_number,
            year=year
        ).first()
        
        if existing:
            return existing
        
        # Calculer l'objectif
        current_avg = analytics.average_score
        target_score = min(100, current_avg + 15)  # +15 points en une semaine
        
        # Dates de la semaine
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Créer les jalons
        milestones = [
            {
                'day': 1,
                'goal': 'Compléter 10 exercices',
                'target_value': 10,
                'current_value': 0,
                'reward': {'xp': 50, 'coins': 25},
                'completed': False
            },
            {
                'day': 3,
                'goal': 'Atteindre 70% de réussite',
                'target_value': 70,
                'current_value': 0,
                'reward': {'xp': 100, 'coins': 50},
                'completed': False
            },
            {
                'day': 5,
                'goal': 'Améliorer 3 matières faibles',
                'target_value': 3,
                'current_value': 0,
                'reward': {'xp': 150, 'coins': 75},
                'completed': False
            },
            {
                'day': 7,
                'goal': f'Atteindre {target_score:.0f}/100',
                'target_value': target_score,
                'current_value': current_avg,
                'reward': {'xp': 300, 'coins': 200, 'badge': 'Champion Hebdomadaire'},
                'completed': False
            }
        ]
        
        mission = WeeklyMission.objects.create(
            student=student,
            week_number=week_number,
            year=year,
            title='🎯 Mission Hebdomadaire : Renaissance Académique',
            description=f'Augmenter votre moyenne à {target_score:.0f}/100',
            target_score=target_score,
            current_score=current_avg,
            milestones=milestones,
            start_date=start_of_week.date(),
            end_date=end_of_week.date(),
            exclusive_badge='Légende de la Semaine'
        )
        
        return mission
    
    def update_mission_progress(self, mission, milestone_index, new_value):
        """Met à jour la progression d'un jalon de mission"""
        if 0 <= milestone_index < len(mission.milestones):
            milestone = mission.milestones[milestone_index]
            milestone['current_value'] = new_value
            
            # Vérifier la complétion
            if new_value >= milestone['target_value']:
                milestone['completed'] = True
                self._reward_milestone(mission.student, milestone['reward'])
            
            mission.milestones[milestone_index] = milestone
            mission.update_progress()
            mission.save()
        
        return mission
    
    def _reward_milestone(self, student, reward):
        """Distribue les récompenses d'un jalon"""
        from .models import StudentProfile
        
        profile = StudentProfile.objects.get(user=student)
        
        if 'xp' in reward:
            profile.add_xp(reward['xp'])
        
        if 'coins' in reward:
            profile.coins += reward['coins']
        
        if 'badge' in reward:
            profile.add_badge(reward['badge'])
        
        profile.save()


class CompetitionService:
    """Service pour gérer les compétitions"""
    
    def create_daily_competition(self):
        """Crée une compétition quotidienne"""
        from .models import Competition
        
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        competition = Competition.objects.create(
            title=f'🏆 Défi Quotidien - {today.strftime("%d %B %Y")}',
            description='Qui sera le champion du jour ? Complétez un maximum d\'exercices avec le meilleur score !',
            competition_type='DAILY',
            rules={
                'scoring': 'score_moyen * nombre_exercices',
                'min_exercises': 5,
                'time_limit_hours': 24
            },
            rewards={
                '1': {'xp': 500, 'coins': 300, 'badge': '🥇 Champion du Jour'},
                '2': {'xp': 300, 'coins': 200, 'badge': '🥈 Vice-Champion'},
                '3': {'xp': 200, 'coins': 100, 'badge': '🥉 Podium'},
                'top10': {'xp': 100, 'coins': 50}
            },
            start_date=today,
            end_date=tomorrow,
            status='ACTIVE',
            max_participants=100
        )
        
        return competition
    
    def create_weekly_competition(self, subject=None):
        """Crée une compétition hebdomadaire"""
        from .models import Competition
        
        now = timezone.now()
        week_end = now + timedelta(days=7)
        
        title = f'🏆 Tournoi Hebdomadaire'
        if subject:
            title += f' - {subject}'
        
        competition = Competition.objects.create(
            title=title,
            description='La grande compétition de la semaine ! Montrez vos compétences et grimpez au classement.',
            competition_type='WEEKLY',
            subject=subject,
            rules={
                'scoring': 'points_totaux + bonus_streak',
                'min_exercises': 20,
                'bonus_streak': True
            },
            rewards={
                '1': {'xp': 2000, 'coins': 1000, 'badge': '👑 Roi de la Semaine'},
                '2': {'xp': 1500, 'coins': 750, 'badge': '⭐ Star Hebdomadaire'},
                '3': {'xp': 1000, 'coins': 500, 'badge': '💎 Top 3'},
                'top10': {'xp': 500, 'coins': 250},
                'top20': {'xp': 250, 'coins': 100}
            },
            start_date=now,
            end_date=week_end,
            status='ACTIVE',
            max_participants=200
        )
        
        return competition
    
    def join_competition(self, competition, student):
        """Inscrit un étudiant à une compétition"""
        from .models import CompetitionParticipant
        
        # Vérifier la limite de participants
        current_count = competition.participants.count()
        if current_count >= competition.max_participants:
            return None, "Compétition complète"
        
        # Créer la participation
        participant, created = CompetitionParticipant.objects.get_or_create(
            competition=competition,
            student=student
        )
        
        if created:
            return participant, "Inscription réussie"
        else:
            return participant, "Déjà inscrit"
    
    def update_competition_score(self, competition, student, score, exercises_completed, time_spent):
        """Met à jour le score d'un participant"""
        from .models import CompetitionParticipant
        
        participant = CompetitionParticipant.objects.get(
            competition=competition,
            student=student
        )
        
        participant.score = score
        participant.exercises_completed = exercises_completed
        participant.time_spent = time_spent
        participant.save()
        
        # Mettre à jour les rangs
        self._update_competition_ranks(competition)
        
        return participant
    
    def _update_competition_ranks(self, competition):
        """Recalcule les rangs de tous les participants"""
        participants = competition.competitionparticipant_set.order_by('-score', 'last_update')
        
        for index, participant in enumerate(participants, start=1):
            participant.rank = index
            participant.save(update_fields=['rank'])
    
    def finalize_competition(self, competition):
        """Finalise une compétition et distribue les récompenses"""
        from .models import StudentProfile
        
        competition.status = 'FINISHED'
        competition.save()
        
        # Distribuer les récompenses
        leaderboard = competition.get_leaderboard()
        
        for participant in leaderboard:
            rank_str = str(participant.rank)
            reward = None
            
            if rank_str in competition.rewards:
                reward = competition.rewards[rank_str]
            elif participant.rank <= 10 and 'top10' in competition.rewards:
                reward = competition.rewards['top10']
            elif participant.rank <= 20 and 'top20' in competition.rewards:
                reward = competition.rewards['top20']
            
            if reward:
                profile = StudentProfile.objects.get(user=participant.student)
                
                if 'xp' in reward:
                    profile.add_xp(reward['xp'])
                
                if 'coins' in reward:
                    profile.coins += reward['coins']
                
                if 'badge' in reward:
                    profile.add_badge(reward['badge'])
                
                profile.save()
        
        return leaderboard


class BadgeService:
    """Service pour gérer les badges"""
    
    def initialize_badges(self):
        """Crée les badges de base du système"""
        from .models import Badge
        
        badges_data = [
            # Badges de démarrage
            {'name': 'Nouveau Venu', 'icon': '🎯', 'rarity': 'COMMON', 'description': 'Complétez votre premier exercice'},
            {'name': 'Premier Pas', 'icon': '👣', 'rarity': 'COMMON', 'description': 'Terminez votre premier défi'},
            
            # Badges d'expertise
            {'name': 'Expert Confirmé', 'icon': '🌟', 'rarity': 'RARE', 'description': 'Maîtrisez une matière à 80%+'},
            {'name': 'Génie', 'icon': '🧠', 'rarity': 'EPIC', 'description': 'Obtenez 100% sur 5 exercices consécutifs'},
            
            # Badges de persévérance
            {'name': 'Persévérant', 'icon': '💪', 'rarity': 'RARE', 'description': 'Surmontez une matière difficile'},
            {'name': 'Infatigable', 'icon': '🔥', 'rarity': 'EPIC', 'description': 'Maintenez un streak de 30 jours'},
            
            # Badges de compétition
            {'name': 'Champion du Jour', 'icon': '🥇', 'rarity': 'RARE', 'description': '1ère place en compétition quotidienne'},
            {'name': 'Roi de la Semaine', 'icon': '👑', 'rarity': 'EPIC', 'description': '1ère place en compétition hebdomadaire'},
            
            # Badges légendaires
            {'name': 'Légende', 'icon': '⚡', 'rarity': 'LEGENDARY', 'description': 'Atteignez le niveau 50'},
            {'name': 'Perfectionniste', 'icon': '💎', 'rarity': 'LEGENDARY', 'description': '100% sur 50 exercices'},
        ]
        
        created_badges = []
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_badges.append(badge)
        
        return created_badges
    
    def award_badge(self, student, badge_name):
        """Attribue un badge à un étudiant"""
        from .models import Badge, Achievement, StudentProfile
        
        try:
            badge = Badge.objects.get(name=badge_name)
            achievement, created = Achievement.objects.get_or_create(
                student=student,
                badge=badge
            )
            
            if created:
                # Mettre à jour le profil
                profile = StudentProfile.objects.get(user=student)
                profile.add_badge(badge_name)
                profile.save()
                
                # Mettre à jour les stats du badge
                badge.times_awarded += 1
                badge.save()
                
                return achievement
            
            return None
        except Badge.DoesNotExist:
            return None


class StressAnalysisService:
    """Service IA pour analyser le stress et recommander des solutions"""
    
    def analyze_stress_report(self, stress_report):
        """Analyse un rapport de stress et génère des recommandations personnalisées"""
        
        # Analyser la gravité globale
        severity = self._calculate_severity(stress_report)
        
        # Générer l'analyse IA
        analysis = self._generate_ai_analysis(stress_report, severity)
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(stress_report, severity)
        
        # Actions prioritaires
        priority_actions = self._generate_priority_actions(stress_report, severity)
        
        # Exercices recommandés
        exercises = self._recommend_exercises(stress_report)
        
        # Techniques de relaxation
        relaxation = self._recommend_relaxation(stress_report, severity)
        
        # Mettre à jour le rapport
        stress_report.ai_analysis = analysis
        stress_report.ai_recommendations = recommendations
        stress_report.priority_actions = priority_actions
        stress_report.recommended_exercises = exercises
        stress_report.relaxation_techniques = relaxation
        stress_report.status = 'ANALYZED'
        stress_report.save()
        
        return stress_report
    
    def _calculate_severity(self, report):
        """Calcule le niveau de gravité global (0-100)"""
        stress_weight = report.stress_level * 15
        concentration_weight = report.concentration_level * 15
        symptoms_count = len(report.symptoms) * 5
        causes_count = len(report.stress_causes) * 5
        
        severity = stress_weight + concentration_weight + symptoms_count + causes_count
        return min(severity, 100)
    
    def _generate_ai_analysis(self, report, severity):
        """Génère une analyse textuelle du stress"""
        
        stress_desc = dict(report.STRESS_LEVEL_CHOICES)[report.stress_level]
        concentration_desc = dict(report.CONCENTRATION_LEVEL_CHOICES)[report.concentration_level]
        
        analysis = f"""🧠 **Analyse de votre état mental**

**Niveau de stress détecté :** {stress_desc} ({report.stress_level}/5)
**Capacité de concentration :** {concentration_desc} ({report.concentration_level}/5)
**Score de gravité global :** {severity}/100

"""
        
        # Analyse des causes
        if report.stress_causes:
            analysis += "**Principales sources de stress identifiées :**\n"
            for cause in report.stress_causes:
                analysis += f"• {cause}\n"
            analysis += "\n"
        
        # Analyse des symptômes
        if report.symptoms:
            analysis += "**Symptômes ressentis :**\n"
            for symptom in report.symptoms:
                analysis += f"• {symptom}\n"
            analysis += "\n"
        
        # Interprétation globale
        if severity >= 70:
            analysis += """⚠️ **Niveau critique détecté**
Votre niveau de stress est très élevé. Il est important d'agir rapidement pour éviter l'épuisement.
Je vous recommande fortement de consulter un conseiller pédagogique ou un professionnel de santé."""
        elif severity >= 50:
            analysis += """⚡ **Niveau modéré à élevé**
Vous traversez une période de stress important qui affecte votre concentration.
Des actions immédiates peuvent vous aider à retrouver votre équilibre."""
        elif severity >= 30:
            analysis += """💡 **Niveau gérable**
Vous ressentez un stress modéré. C'est normal dans un parcours étudiant.
Quelques ajustements peuvent améliorer significativement votre bien-être."""
        else:
            analysis += """✅ **Niveau bas**
Votre stress est gérable. Continuez vos bonnes habitudes et restez vigilant."""
        
        return analysis
    
    def _generate_recommendations(self, report, severity):
        """Génère des recommandations personnalisées"""
        recommendations = []
        
        # Recommandations basées sur le niveau de stress
        if report.stress_level >= 4:
            recommendations.append({
                'title': '🌊 Pratiquez la respiration profonde',
                'description': 'Faites 5 minutes de respiration abdominale 3 fois par jour : inspirez 4 secondes, retenez 4 secondes, expirez 6 secondes.',
                'impact': 'high',
                'duration': '5 min'
            })
            recommendations.append({
                'title': '🚶 Faites des pauses actives',
                'description': 'Toutes les 45 minutes, levez-vous et marchez 5 minutes. Cela oxygène le cerveau.',
                'impact': 'high',
                'duration': '5 min'
            })
        
        # Recommandations basées sur la concentration
        if report.concentration_level >= 4:
            recommendations.append({
                'title': '⏰ Technique Pomodoro',
                'description': 'Travaillez 25 minutes intensément, puis pause de 5 minutes. Après 4 cycles, pause de 15-30 minutes.',
                'impact': 'high',
                'duration': '25 min'
            })
            recommendations.append({
                'title': '🎯 Éliminez les distractions',
                'description': 'Mettez votre téléphone en mode avion, fermez les réseaux sociaux, utilisez des applications de blocage.',
                'impact': 'high',
                'duration': 'Permanent'
            })
            recommendations.append({
                'title': '🎵 Musique de concentration',
                'description': 'Écoutez de la musique binaurale, des sons de la nature ou de la musique instrumentale (lo-fi, classique).',
                'impact': 'medium',
                'duration': 'Variable'
            })
        
        # Recommandations liées au sommeil
        if report.sleep_hours and report.sleep_hours < 7:
            recommendations.append({
                'title': '😴 Améliorez votre sommeil',
                'description': f'Vous dormez seulement {report.sleep_hours}h. Visez 7-9h : couchez-vous à heure fixe, évitez les écrans 1h avant.',
                'impact': 'critical',
                'duration': 'Quotidien'
            })
        
        # Recommandations liées à l'exercice
        if report.exercise_frequency in ['Jamais', 'Rarement']:
            recommendations.append({
                'title': '💪 Activité physique régulière',
                'description': '30 minutes d\'exercice modéré (marche rapide, yoga, vélo) libèrent des endorphines anti-stress.',
                'impact': 'high',
                'duration': '30 min/jour'
            })
        
        # Recommandations générales
        recommendations.extend([
            {
                'title': '📝 Planifiez votre journée',
                'description': 'Chaque soir, listez 3 tâches prioritaires pour demain. Cela réduit l\'anxiété du lendemain.',
                'impact': 'medium',
                'duration': '10 min'
            },
            {
                'title': '🙏 Pratiquez la gratitude',
                'description': 'Notez 3 choses positives chaque jour. Cela recadre votre mental positivement.',
                'impact': 'medium',
                'duration': '5 min'
            },
            {
                'title': '👥 Parlez-en',
                'description': 'Partagez vos difficultés avec un ami, famille ou conseiller. Le simple fait d\'en parler soulage.',
                'impact': 'high',
                'duration': 'Variable'
            }
        ])
        
        return recommendations
    
    def _generate_priority_actions(self, report, severity):
        """Génère 3 actions prioritaires immédiates"""
        actions = []
        
        if report.stress_level >= 4:
            actions.append({
                'action': 'Faites 5 minutes de respiration profonde MAINTENANT',
                'urgency': 'immediate',
                'icon': '🌊'
            })
        
        if report.concentration_level >= 4:
            actions.append({
                'action': 'Utilisez la technique Pomodoro pour votre prochaine session d\'étude',
                'urgency': 'today',
                'icon': '⏰'
            })
        
        if report.sleep_hours and report.sleep_hours < 7:
            actions.append({
                'action': f'Ce soir, couchez-vous 1h plus tôt (objectif : {report.sleep_hours + 1}h)',
                'urgency': 'today',
                'icon': '😴'
            })
        else:
            actions.append({
                'action': 'Faites une pause de 10 minutes en plein air ou près d\'une fenêtre',
                'urgency': 'today',
                'icon': '🌳'
            })
        
        return actions[:3]
    
    def _recommend_exercises(self, report):
        """Recommande des exercices adaptés au niveau de stress"""
        exercises = []
        
        if report.concentration_level >= 3:
            exercises.extend([
                {
                    'name': 'Exercices courts et variés',
                    'description': 'Alternez entre différentes matières toutes les 20-30 minutes',
                    'benefit': 'Maintient l\'attention'
                },
                {
                    'name': 'Révisions actives',
                    'description': 'Faites des quiz, des flashcards ou expliquez à voix haute',
                    'benefit': 'Meilleure mémorisation'
                }
            ])
        
        if report.stress_level >= 3:
            exercises.extend([
                {
                    'name': 'Sessions plus courtes',
                    'description': 'Réduisez vos sessions à 15-20 minutes avec pauses',
                    'benefit': 'Réduit la pression'
                },
                {
                    'name': 'Matières plaisantes d\'abord',
                    'description': 'Commencez par ce que vous aimez pour créer de l\'élan',
                    'benefit': 'Motivation positive'
                }
            ])
        
        return exercises
    
    def _recommend_relaxation(self, report, severity):
        """Recommande des techniques de relaxation"""
        techniques = [
            {
                'name': '🌊 Respiration 4-7-8',
                'steps': [
                    'Inspirez par le nez pendant 4 secondes',
                    'Retenez votre souffle pendant 7 secondes',
                    'Expirez lentement par la bouche pendant 8 secondes',
                    'Répétez 4 fois'
                ],
                'when': 'Avant de dormir ou en cas de pic de stress',
                'duration': '2 minutes'
            },
            {
                'name': '🧘 Méditation guidée',
                'steps': [
                    'Asseyez-vous confortablement',
                    'Fermez les yeux',
                    'Concentrez-vous sur votre respiration naturelle',
                    'Laissez passer les pensées sans jugement'
                ],
                'when': 'Le matin ou avant une session d\'étude',
                'duration': '5-10 minutes',
                'apps': ['Petit Bambou', 'Headspace', 'Calm']
            },
            {
                'name': '💪 Relaxation musculaire progressive',
                'steps': [
                    'Tendez chaque groupe musculaire 5 secondes',
                    'Relâchez complètement',
                    'Commencez par les pieds, remontez jusqu\'à la tête'
                ],
                'when': 'Le soir pour détendre le corps',
                'duration': '10 minutes'
            }
        ]
        
        if severity >= 70:
            techniques.insert(0, {
                'name': '🆘 Aide professionnelle',
                'steps': [
                    'Contactez le service de santé universitaire',
                    'Parlez à un conseiller pédagogique',
                    'Envisagez un soutien psychologique'
                ],
                'when': 'Dès que possible',
                'duration': 'Variable'
            })
        
        return techniques
    
    def track_improvement(self, student):
        """Suit l'évolution du stress d'un étudiant"""
        from .models import StressReport
        
        reports = StressReport.objects.filter(student=student).order_by('-created_at')[:5]
        
        if len(reports) < 2:
            return None
        
        # Calculer la tendance
        recent_stress = reports[0].stress_level
        previous_stress = sum(r.stress_level for r in reports[1:]) / len(reports[1:])
        
        improvement = previous_stress - recent_stress
        
        return {
            'current_stress': recent_stress,
            'previous_average': previous_stress,
            'improvement': improvement,
            'trend': 'improving' if improvement > 0 else 'worsening' if improvement < 0 else 'stable',
            'total_reports': reports.count()
        }