# ==========================================
# Analytics Service - Statistiques Étudiants
# ==========================================
"""
Service d'analyse des performances étudiantes.
Génère des statistiques détaillées, détecte les tendances,
et calcule les métriques de progression.
"""

from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import statistics


class StudentAnalytics:
    """
    Service pour générer des statistiques détaillées sur les performances étudiantes.
    
    Fonctionnalités:
    - Calcul du temps d'étude total
    - Analyse de la progression dans le temps
    - Identification des matières faibles
    - Génération de recommandations personnalisées
    - Calcul des tendances (amélioration/déclin)
    """
    
    def __init__(self, student_profile):
        """
        Initialiser le service d'analytics pour un étudiant.
        
        Args:
            student_profile: Instance de UserProfile de l'étudiant
        """
        self.profile = student_profile
        self.user = student_profile.user
    
    
    def get_complete_statistics(self):
        """
        Récupérer toutes les statistiques complètes de l'étudiant.
        
        Retourne un dictionnaire avec:
        - Scores globaux
        - Temps d'étude
        - Progression temporelle
        - Performances par matière
        - Tendances
        - Points forts/faibles
        
        Returns:
            dict: Statistiques complètes
        """
        from evaluation.models import Result, Submission, Test
        
        # Récupérer tous les résultats de l'étudiant
        all_results = Result.objects.filter(student=self.user).order_by('-created_at')
        
        # Si aucun résultat, retourner stats vides
        if all_results.count() == 0:
            return self._get_empty_stats()
        
        # 1. SCORES GLOBAUX
        scores_stats = self._calculate_score_statistics(all_results)
        
        # 2. TEMPS D'ÉTUDE
        study_time_stats = self._calculate_study_time(all_results)
        
        # 3. PROGRESSION TEMPORELLE
        progression_stats = self._calculate_progression(all_results)
        
        # 4. PERFORMANCES PAR MATIÈRE
        subject_performance = self._calculate_subject_performance(all_results)
        
        # 5. TENDANCES (amélioration/déclin)
        trends = self._calculate_trends(all_results)
        
        # 6. POINTS FORTS ET FAIBLES
        strengths_weaknesses = self._identify_strengths_weaknesses(subject_performance)
        
        # 7. MÉTADONNÉES
        metadata = {
            'total_tests': all_results.count(),
            'tests_passed': all_results.filter(percentage_score__gte=60).count(),
            'tests_failed': all_results.filter(percentage_score__lt=60).count(),
            'last_test_date': all_results.first().created_at if all_results.count() > 0 else None,
            'first_test_date': all_results.last().created_at if all_results.count() > 0 else None,
        }
        
        return {
            'scores': scores_stats,
            'study_time': study_time_stats,
            'progression': progression_stats,
            'subjects': subject_performance,
            'trends': trends,
            'strengths': strengths_weaknesses['strengths'],
            'weaknesses': strengths_weaknesses['weaknesses'],
            'metadata': metadata,
        }
    
    
    def _calculate_score_statistics(self, results):
        """
        Calculer les statistiques de scores.
        
        Args:
            results: QuerySet de Result
            
        Returns:
            dict: Statistiques de scores
        """
        scores = [r.percentage_score for r in results]
        
        if not scores:
            return {}
        
        return {
            'average': round(statistics.mean(scores), 2),
            'median': round(statistics.median(scores), 2),
            'min': min(scores),
            'max': max(scores),
            'std_deviation': round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            'total_points_earned': sum([r.total_score for r in results]),
            'total_points_possible': sum([r.total_score / r.percentage_score * 100 if r.percentage_score > 0 else 0 for r in results]),
        }
    
    
    def _calculate_study_time(self, results):
        """
        Calculer le temps d'étude total et moyen.
        
        Logique:
        - Récupère les soumissions associées aux résultats
        - Calcule le temps entre start_time et submitted_at
        - Agrège par jour/semaine/mois
        
        Args:
            results: QuerySet de Result
        Returns:
            dict: Statistiques de temps d'étude
        """
        from evaluation.models import Submission
        
        # Récupérer toutes les soumissions terminées
        # FIX: Utiliser filter au lieu d'exclude pour compatibilité Djongo
        submissions = Submission.objects.filter(
            student=self.user,
            status='completed',
            submitted_at__isnull=False  # Au lieu de exclude(submitted_at__isnull=True)
        )
        
        total_minutes = 0
        study_sessions = []
        
        for submission in submissions:
            if submission.start_time and submission.submitted_at:
                # Calculer la durée en minutes
                duration = (submission.submitted_at - submission.start_time).total_seconds() / 60
                total_minutes += duration
                study_sessions.append({
                    'date': submission.submitted_at.date(),
                    'duration': duration,
                    'test': submission.test.title
                })
        
        # Calculer par période
        now = timezone.now()
        last_7_days = submissions.filter(submitted_at__gte=now - timedelta(days=7))
        last_30_days = submissions.filter(submitted_at__gte=now - timedelta(days=30))
        
        # Temps moyen par session
        avg_time = total_minutes / len(study_sessions) if study_sessions else 0
        
        return {
            'total_minutes': round(total_minutes, 2),
            'total_hours': round(total_minutes / 60, 2),
            'average_per_test': round(avg_time, 2),
            'last_7_days': round(sum([
                (s.submitted_at - s.start_time).total_seconds() / 60 
                for s in last_7_days if s.start_time and s.submitted_at
            ]), 2) if last_7_days.count() > 0 else 0,
            'last_30_days': round(sum([
                (s.submitted_at - s.start_time).total_seconds() / 60 
                for s in last_30_days if s.start_time and s.submitted_at
            ]), 2) if last_30_days.count() > 0 else 0,
            'sessions': study_sessions,
            'total_sessions': len(study_sessions),
        }
    
    
    def _calculate_progression(self, results):
        """
        Calculer la progression dans le temps.
        
        Logique:
        - Compare les scores des 5 premiers tests vs 5 derniers
        - Calcule la moyenne mobile (moving average)
        - Détecte la tendance générale (↗️ ↘️ →)
        
        Args:
            results: QuerySet de Result (ordonnés par date décroissante)
            
        Returns:
            dict: Statistiques de progression
        """
        # Inverser pour avoir chronologique
        chronological_results = list(results.order_by('created_at'))
        
        if len(chronological_results) < 2:
            return {
                'trend': 'stable',
                'improvement': 0,
                'recent_average': 0,
                'early_average': 0,
                'progression_data': []
            }
        
        # Diviser en groupes
        total_tests = len(chronological_results)
        split_point = total_tests // 2
        
        early_tests = chronological_results[:split_point]
        recent_tests = chronological_results[split_point:]
        
        # Calculer moyennes
        early_avg = statistics.mean([r.percentage_score for r in early_tests])
        recent_avg = statistics.mean([r.percentage_score for r in recent_tests])
        
        improvement = recent_avg - early_avg
        
        # Déterminer la tendance
        if improvement > 5:
            trend = 'improving'  # ↗️
        elif improvement < -5:
            trend = 'declining'  # ↘️
        else:
            trend = 'stable'  # →
        
        # Données pour graphique (moyenne mobile sur 3 tests)
        progression_data = []
        for i in range(len(chronological_results)):
            start = max(0, i - 2)
            end = i + 1
            window = chronological_results[start:end]
            avg = statistics.mean([r.percentage_score for r in window])
            
            progression_data.append({
                'test_number': i + 1,
                'score': chronological_results[i].percentage_score,
                'moving_average': round(avg, 2),
                'date': chronological_results[i].created_at.strftime('%Y-%m-%d'),
                'test_name': chronological_results[i].test.title
            })
        
        return {
            'trend': trend,
            'improvement': round(improvement, 2),
            'recent_average': round(recent_avg, 2),
            'early_average': round(early_avg, 2),
            'progression_data': progression_data,
            'total_tests_analyzed': total_tests
        }
    
    
    def _calculate_subject_performance(self, results):
        """
        Calculer les performances par matière.
        
        Logique:
        - Groupe les résultats par test.subject
        - Calcule moyenne, min, max par matière
        - Compte le nombre de tests par matière
        
        Args:
            results: QuerySet de Result
            
        Returns:
            dict: Performances par matière
        """
        # Grouper par matière
        subjects = defaultdict(list)
        
        for result in results:
            subject = result.test.subject
            subjects[subject].append({
                'score': result.percentage_score,
                'points': result.total_score,
                'max_points': result.test.total_points,
                'date': result.created_at,
                'test_id': result.test.id,
                'test_title': result.test.title
            })
        
        # Calculer stats par matière
        subject_stats = {}
        for subject, scores_data in subjects.items():
            scores = [s['score'] for s in scores_data]
            
            subject_stats[subject] = {
                'average': round(statistics.mean(scores), 2),
                'min': min(scores),
                'max': max(scores),
                'count': len(scores),
                'total_points': sum([s['points'] for s in scores_data]),
                'max_possible': sum([s['max_points'] for s in scores_data]),
                'last_score': scores_data[0]['score'],  # Le plus récent
                'trend': self._calculate_subject_trend(scores_data),
                'tests': scores_data[:5]  # Les 5 derniers tests
            }
        
        return subject_stats
    
    
    def _calculate_subject_trend(self, scores_data):
        """
        Calculer la tendance pour une matière spécifique.
        
        Args:
            scores_data: Liste de dicts avec scores
            
        Returns:
            str: 'improving', 'declining', ou 'stable'
        """
        if len(scores_data) < 3:
            return 'stable'
        
        # Comparer les 2 derniers avec les 2 précédents
        recent = scores_data[:2]
        previous = scores_data[2:4]
        
        recent_avg = statistics.mean([s['score'] for s in recent])
        previous_avg = statistics.mean([s['score'] for s in previous])
        
        diff = recent_avg - previous_avg
        
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        else:
            return 'stable'
    
    
    def _calculate_trends(self, results):
        """
        Calculer les tendances globales.
        
        Returns:
            dict: Tendances diverses
        """
        now = timezone.now()
        
        # Tendance sur les 7 derniers jours
        recent_7 = results.filter(created_at__gte=now - timedelta(days=7))
        previous_7 = results.filter(
            created_at__gte=now - timedelta(days=14),
            created_at__lt=now - timedelta(days=7)
        )
        
        trends = {
            'weekly': self._compare_periods(recent_7, previous_7),
            'monthly': self._compare_periods(
                results.filter(created_at__gte=now - timedelta(days=30)),
                results.filter(
                    created_at__gte=now - timedelta(days=60),
                    created_at__lt=now - timedelta(days=30)
                )
            ),
            'consistency': self._calculate_consistency(results)
        }
        
        return trends
    
    
    def _compare_periods(self, recent, previous):
        """Comparer deux périodes."""
        if recent.count() == 0 or previous.count() == 0:
            return {'change': 0, 'trend': 'stable'}
        
        recent_avg = recent.aggregate(Avg('percentage'))['percentage_score__avg']
        previous_avg = previous.aggregate(Avg('percentage'))['percentage_score__avg']
        
        if recent_avg is None or previous_avg is None:
            return {'change': 0, 'trend': 'stable'}
        
        change = recent_avg - previous_avg
        
        return {
            'change': round(change, 2),
            'trend': 'improving' if change > 5 else 'declining' if change < -5 else 'stable',
            'recent_average': round(recent_avg, 2),
            'previous_average': round(previous_avg, 2)
        }
    
    
    def _calculate_consistency(self, results):
        """
        Calculer la régularité des scores (faible écart-type = plus régulier).
        """
        scores = [r.percentage_score for r in results]
        
        if len(scores) < 2:
            return {'score': 0, 'label': 'Insuffisant'}
        
        std = statistics.stdev(scores)
        
        # Score de régularité (0-100)
        consistency_score = max(0, 100 - (std * 2))
        
        if consistency_score >= 80:
            label = 'Très régulier'
        elif consistency_score >= 60:
            label = 'Régulier'
        elif consistency_score >= 40:
            label = 'Irrégulier'
        else:
            label = 'Très irrégulier'
        
        return {
            'score': round(consistency_score, 2),
            'label': label,
            'std_deviation': round(std, 2)
        }
    
    
    def _identify_strengths_weaknesses(self, subject_performance):
        """
        Identifier les points forts et faibles basés sur les performances par matière.
        
        Args:
            subject_performance: Dict des performances par matière
            
        Returns:
            dict: Points forts et faibles
        """
        if not subject_performance:
            return {'strengths': [], 'weaknesses': []}
        
        # Trier par moyenne
        sorted_subjects = sorted(
            subject_performance.items(),
            key=lambda x: x[1]['average'],
            reverse=True
        )
        
        # Points forts (>= 75%)
        strengths = [
            {
                'subject': subject,
                'average': data['average'],
                'count': data['count'],
                'trend': data['trend']
            }
            for subject, data in sorted_subjects
            if data['average'] >= 75
        ]
        
        # Points faibles (< 60%)
        weaknesses = [
            {
                'subject': subject,
                'average': data['average'],
                'count': data['count'],
                'trend': data['trend'],
                'needs_improvement': True
            }
            for subject, data in sorted_subjects
            if data['average'] < 60
        ]
        
        return {
            'strengths': strengths[:5],  # Top 5
            'weaknesses': weaknesses[:5]  # Top 5
        }
    
    
    def _get_empty_stats(self):
        """Retourner des stats vides si aucun résultat."""
        return {
            'scores': {},
            'study_time': {'total_minutes': 0, 'total_hours': 0},
            'progression': {'trend': 'stable', 'improvement': 0},
            'subjects': {},
            'trends': {},
            'strengths': [],
            'weaknesses': [],
            'metadata': {'total_tests': 0}
        }


class RecommendationEngine:
    """
    Moteur de recommandations personnalisées pour les étudiants.
    
    Génère des recommandations basées sur:
    - Les matières faibles
    - Les tendances de progression
    - Les types d'erreurs commises
    - L'historique d'apprentissage
    """
    
    def __init__(self, student_profile, analytics_data):
        """
        Initialiser le moteur de recommandations.
        
        Args:
            student_profile: Instance de UserProfile
            analytics_data: Données d'analytics (de StudentAnalytics)
        """
        self.profile = student_profile
        self.analytics = analytics_data
    
    
    def generate_recommendations(self):
        """
        Générer toutes les recommandations personnalisées.
        
        Returns:
            list: Liste de recommandations avec priorités
        """
        recommendations = []
        
        # 1. Recommandations basées sur les matières faibles
        recommendations.extend(self._recommend_weak_subjects())
        
        # 2. Recommandations basées sur les tendances
        recommendations.extend(self._recommend_from_trends())
        
        # 3. Recommandations basées sur le temps d'étude
        recommendations.extend(self._recommend_study_time())
        
        # 4. Recommandations basées sur la régularité
        recommendations.extend(self._recommend_consistency())
        
        # Trier par priorité (high > medium > low)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:10]  # Top 10 recommandations
    
    
    def _recommend_weak_subjects(self):
        """Recommandations pour matières faibles."""
        recommendations = []
        
        for weakness in self.analytics['weaknesses']:
            subject = weakness['subject']
            avg = weakness['average']
            
            recommendations.append({
                'type': 'weak_subject',
                'priority': 'high',
                'subject': subject,
                'title': f"Améliorer en {subject}",
                'description': f"Votre moyenne en {subject} est de {avg}%. Nous recommandons de réviser les concepts de base.",
                'actions': [
                    f"Revoir les chapitres de {subject}",
                    f"Refaire les exercices ratés en {subject}",
                    f"Demander de l'aide à l'enseignant"
                ],
                'resources': [
                    {'type': 'chapter', 'name': f'Chapitres {subject}'},
                    {'type': 'exercises', 'name': 'Exercices de révision'}
                ],
                'icon': 'book',
                'color': 'danger'
            })
        
        return recommendations
    
    
    def _recommend_from_trends(self):
        """Recommandations basées sur les tendances."""
        recommendations = []
        
        progression = self.analytics['progression']
        
        if progression['trend'] == 'declining':
            recommendations.append({
                'type': 'declining_trend',
                'priority': 'high',
                'title': "Attention : Baisse de performances",
                'description': f"Vos scores ont baissé de {abs(progression['improvement'])}% récemment.",
                'actions': [
                    "Revoir les derniers chapitres",
                    "Augmenter le temps d'étude",
                    "Identifier les blocages"
                ],
                'icon': 'arrow-down',
                'color': 'warning'
            })
        
        elif progression['trend'] == 'improving':
            recommendations.append({
                'type': 'positive_feedback',
                'priority': 'low',
                'title': "Excellente progression !",
                'description': f"Vos scores se sont améliorés de {progression['improvement']}%. Continuez ainsi !",
                'actions': [
                    "Maintenir le rythme",
                    "Approfondir les sujets maîtrisés"
                ],
                'icon': 'arrow-up',
                'color': 'success'
            })
        
        return recommendations
    
    
    def _recommend_study_time(self):
        """Recommandations sur le temps d'étude."""
        recommendations = []
        
        study_time = self.analytics['study_time']
        
        if study_time['total_hours'] < 5:  # Moins de 5 heures total
            recommendations.append({
                'type': 'increase_study_time',
                'priority': 'medium',
                'title': "Augmenter le temps d'étude",
                'description': f"Vous avez étudié seulement {study_time['total_hours']:.1f}h au total.",
                'actions': [
                    "Planifier 30 min d'étude par jour",
                    "Créer un emploi du temps"
                ],
                'icon': 'clock',
                'color': 'info'
            })
        
        return recommendations
    
    
    def _recommend_consistency(self):
        """Recommandations sur la régularité."""
        recommendations = []
        
        consistency = self.analytics['trends'].get('consistency', {})
        
        if consistency.get('score', 0) < 50:
            recommendations.append({
                'type': 'improve_consistency',
                'priority': 'medium',
                'title': "Améliorer la régularité",
                'description': "Vos scores sont irréguliers. Une pratique régulière aide à progresser.",
                'actions': [
                    "Faire des petits tests réguliers",
                    "Réviser quotidiennement"
                ],
                'icon': 'calendar-check',
                'color': 'warning'
            })
        
        return recommendations


# ==========================================
# Fonction utilitaire pour mettre à jour le profil
# ==========================================

def update_student_profile_with_recommendations(student_profile):
    """
    Mettre à jour le profil étudiant avec les dernières recommandations.
    
    Processus:
    1. Générer analytics complètes
    2. Générer recommandations personnalisées
    3. Sauvegarder dans UserProfile.ai_recommendations (JSON)
    4. Mettre à jour les stats du profil
    
    Args:
        student_profile: Instance de UserProfile
        
    Returns:
        dict: Les nouvelles recommandations
    """
    # 1. Générer analytics
    analytics_service = StudentAnalytics(student_profile)
    analytics_data = analytics_service.get_complete_statistics()
    
    # 2. Générer recommandations
    recommendation_engine = RecommendationEngine(student_profile, analytics_data)
    recommendations = recommendation_engine.generate_recommendations()
    
    # 3. Sauvegarder dans le profil
    student_profile.ai_recommendations = recommendations
    
    # 4. Mettre à jour les stats
    student_profile.average_score = analytics_data['scores'].get('average', 0)
    student_profile.total_tests_taken = analytics_data['metadata']['total_tests']
    
    # Sauvegarder
    student_profile.save()
    
    return recommendations
