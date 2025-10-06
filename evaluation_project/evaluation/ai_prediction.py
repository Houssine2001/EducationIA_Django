"""
Système de prédiction IA pour prédire le niveau futur des étudiants.

Ce module utilise l'analyse des données historiques pour prédire:
- Le niveau global futur de l'étudiant (Faible, Moyen, Pro)
- La confiance de la prédiction
- Les facteurs clés influençant la prédiction
- Le délai estimé
"""

from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
import json


class StudentLevelPredictor:
    """
    Prédicteur de niveau futur pour les étudiants basé sur l'IA.
    """
    
    # Seuils de niveau
    LEVEL_THRESHOLDS = {
        'faible': (0, 50),
        'moyen': (50, 75),
        'pro': (75, 100)
    }
    
    # Poids des facteurs
    WEIGHTS = {
        'average_score': 0.35,
        'trend': 0.25,
        'consistency': 0.15,
        'improvement_rate': 0.15,
        'activity_level': 0.10
    }
    
    def __init__(self, user_profile):
        """
        Initialise le prédicteur pour un profil utilisateur.
        
        Args:
            user_profile: Instance de UserProfile
        """
        self.profile = user_profile
        self.user = user_profile.user
        
    def predict_future_level(self, timeframe_months=3):
        """
        Prédit le niveau futur de l'étudiant.
        
        Args:
            timeframe_months: Nombre de mois dans le futur (par défaut 3)
            
        Returns:
            dict: {
                'future_level': str,  # 'Faible', 'Moyen', 'Pro'
                'current_level': str,
                'confidence': float,  # 0-100
                'key_factors': list,
                'timeframe': str,
                'recommendations': list
            }
        """
        from .models import Result, Submission
        
        # Récupérer les résultats
        results = Result.objects.filter(
            submission__student=self.user,
            submission__status='graded'
        ).select_related('submission__test').order_by('created_at')
        
        if results.count() < 2:
            return self._default_prediction(timeframe_months)
        
        # Calculer les métriques
        metrics = self._calculate_metrics(results)
        
        # Calculer le score prédictif
        prediction_score = self._calculate_prediction_score(metrics)
        
        # Déterminer le niveau futur
        future_level = self._determine_level(prediction_score)
        current_level = self._determine_level(metrics['average_score'])
        
        # Calculer la confiance
        confidence = self._calculate_confidence(metrics, results.count())
        
        # Identifier les facteurs clés
        key_factors = self._identify_key_factors(metrics, future_level)
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(metrics, future_level, current_level)
        
        return {
            'future_level': future_level,
            'current_level': current_level,
            'confidence': round(confidence, 1),
            'key_factors': key_factors,
            'timeframe': f"{timeframe_months} mois",
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _calculate_metrics(self, results):
        """Calcule les métriques à partir des résultats."""
        scores = [r.percentage_score for r in results]
        
        # Score moyen
        average_score = sum(scores) / len(scores)
        
        # Tendance (régression linéaire simple)
        trend = self._calculate_trend(scores)
        
        # Consistance (écart-type inversé)
        consistency = self._calculate_consistency(scores)
        
        # Taux d'amélioration
        improvement_rate = self._calculate_improvement_rate(scores)
        
        # Niveau d'activité (tests par mois)
        activity_level = self._calculate_activity_level(results)
        
        # Analyse des forces et faiblesses
        strengths_count = self._count_strengths(results)
        weaknesses_count = self._count_weaknesses(results)
        
        return {
            'average_score': average_score,
            'trend': trend,
            'consistency': consistency,
            'improvement_rate': improvement_rate,
            'activity_level': activity_level,
            'strengths_count': strengths_count,
            'weaknesses_count': weaknesses_count,
            'total_tests': len(scores),
            'recent_scores': scores[-5:] if len(scores) >= 5 else scores
        }
    
    def _calculate_trend(self, scores):
        """Calcule la tendance (pente de la régression linéaire)."""
        if len(scores) < 2:
            return 0
        
        n = len(scores)
        x = list(range(n))
        y = scores
        
        # Régression linéaire simple
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        return slope
    
    def _calculate_consistency(self, scores):
        """Calcule la consistance (100 - écart-type normalisé)."""
        if len(scores) < 2:
            return 100
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Normaliser l'écart-type (0-100 devient 100-0)
        consistency = max(0, 100 - (std_dev * 2))
        return consistency
    
    def _calculate_improvement_rate(self, scores):
        """Calcule le taux d'amélioration (changement moyen entre tests consécutifs)."""
        if len(scores) < 2:
            return 0
        
        improvements = []
        for i in range(1, len(scores)):
            improvements.append(scores[i] - scores[i-1])
        
        return sum(improvements) / len(improvements)
    
    def _calculate_activity_level(self, results):
        """Calcule le niveau d'activité (tests par mois)."""
        if results.count() < 2:
            return 0
        
        first_date = results.first().created_at
        last_date = results.last().created_at
        
        days_diff = (last_date - first_date).days
        if days_diff == 0:
            return results.count()
        
        months = days_diff / 30
        return results.count() / max(months, 0.5)  # Au moins 0.5 mois
    
    def _count_strengths(self, results):
        """Compte les forces identifiées."""
        strengths = set()
        for result in results:
            if result.ai_analysis and 'strengths' in result.ai_analysis:
                for strength in result.ai_analysis['strengths']:
                    if isinstance(strength, dict):
                        strengths.add(strength.get('skill', strength.get('description', '')))
                    else:
                        strengths.add(str(strength))
        return len(strengths)
    
    def _count_weaknesses(self, results):
        """Compte les faiblesses identifiées."""
        weaknesses = set()
        for result in results:
            if result.ai_analysis and 'weaknesses' in result.ai_analysis:
                for weakness in result.ai_analysis['weaknesses']:
                    if isinstance(weakness, dict):
                        weaknesses.add(weakness.get('skill', weakness.get('description', '')))
                    else:
                        weaknesses.add(str(weakness))
        return len(weaknesses)
    
    def _calculate_prediction_score(self, metrics):
        """Calcule le score prédictif pondéré."""
        # Normaliser les métriques
        normalized = {
            'average_score': metrics['average_score'],
            'trend': self._normalize_trend(metrics['trend']),
            'consistency': metrics['consistency'],
            'improvement_rate': self._normalize_improvement(metrics['improvement_rate']),
            'activity_level': self._normalize_activity(metrics['activity_level'])
        }
        
        # Appliquer les poids
        prediction_score = sum(
            normalized[key] * self.WEIGHTS[key]
            for key in self.WEIGHTS.keys()
        )
        
        return prediction_score
    
    def _normalize_trend(self, trend):
        """Normalise la tendance sur une échelle 0-100."""
        # Tendance typique: -5 à +5 points par test
        # Mapper à 0-100
        normalized = 50 + (trend * 10)
        return max(0, min(100, normalized))
    
    def _normalize_improvement(self, improvement_rate):
        """Normalise le taux d'amélioration sur une échelle 0-100."""
        # Taux typique: -10 à +10
        normalized = 50 + (improvement_rate * 5)
        return max(0, min(100, normalized))
    
    def _normalize_activity(self, activity_level):
        """Normalise le niveau d'activité sur une échelle 0-100."""
        # 0-2 tests/mois = faible, 2-4 = moyen, 4+ = élevé
        if activity_level >= 4:
            return 100
        elif activity_level >= 2:
            return 50 + (activity_level - 2) * 25
        else:
            return activity_level * 25
    
    def _determine_level(self, score):
        """Détermine le niveau basé sur le score."""
        if score >= 75:
            return 'Pro'
        elif score >= 50:
            return 'Moyen'
        else:
            return 'Faible'
    
    def _calculate_confidence(self, metrics, test_count):
        """Calcule la confiance de la prédiction."""
        # Base: nombre de tests (plus de tests = plus de confiance)
        test_confidence = min(100, (test_count / 10) * 100)
        
        # Ajuster avec la consistance
        consistency_factor = metrics['consistency'] / 100
        
        # Ajuster avec le niveau d'activité
        activity_factor = min(1.0, metrics['activity_level'] / 4)
        
        # Confiance finale
        confidence = test_confidence * 0.5 + metrics['consistency'] * 0.3 + (activity_factor * 100 * 0.2)
        
        return max(50, min(95, confidence))  # Entre 50% et 95%
    
    def _identify_key_factors(self, metrics, future_level):
        """Identifie les facteurs clés de la prédiction."""
        factors = []
        
        # Score moyen
        if metrics['average_score'] >= 75:
            factors.append(f"Excellente moyenne ({metrics['average_score']:.1f}%)")
        elif metrics['average_score'] >= 50:
            factors.append(f"Moyenne correcte ({metrics['average_score']:.1f}%)")
        else:
            factors.append(f"Moyenne à améliorer ({metrics['average_score']:.1f}%)")
        
        # Tendance
        if metrics['trend'] > 2:
            factors.append("Forte progression observée")
        elif metrics['trend'] > 0:
            factors.append("Progression positive")
        elif metrics['trend'] < -2:
            factors.append("Attention: tendance à la baisse")
        else:
            factors.append("Performances stables")
        
        # Consistance
        if metrics['consistency'] >= 80:
            factors.append("Résultats très constants")
        elif metrics['consistency'] >= 60:
            factors.append("Résultats assez réguliers")
        else:
            factors.append("Résultats variables")
        
        # Activité
        if metrics['activity_level'] >= 4:
            factors.append("Très actif (nombreux tests)")
        elif metrics['activity_level'] >= 2:
            factors.append("Activité régulière")
        else:
            factors.append("Activité limitée")
        
        return factors[:4]  # Maximum 4 facteurs
    
    def _generate_recommendations(self, metrics, future_level, current_level):
        """Génère des recommandations basées sur la prédiction."""
        recommendations = []
        
        if future_level == current_level:
            if future_level == 'Faible':
                recommendations.append("Augmentez votre rythme de travail")
                recommendations.append("Concentrez-vous sur les bases")
            elif future_level == 'Moyen':
                recommendations.append("Continuez vos efforts réguliers")
                recommendations.append("Visez l'excellence pour progresser")
            else:  # Pro
                recommendations.append("Maintenez votre niveau d'excellence")
                recommendations.append("Explorez des sujets avancés")
        
        elif future_level > current_level:
            recommendations.append("Vous êtes sur la bonne voie!")
            recommendations.append("Maintenez votre rythme de progression")
        else:
            recommendations.append("Attention: risque de régression")
            recommendations.append("Revoyez vos méthodes de travail")
        
        # Recommandations basées sur les faiblesses
        if metrics['weaknesses_count'] > 3:
            recommendations.append("Travaillez vos points faibles identifiés")
        
        # Recommandations basées sur l'activité
        if metrics['activity_level'] < 2:
            recommendations.append("Augmentez votre fréquence de pratique")
        
        return recommendations[:3]  # Maximum 3 recommandations
    
    def _default_prediction(self, timeframe_months):
        """Retourne une prédiction par défaut si pas assez de données."""
        return {
            'future_level': 'Moyen',
            'current_level': 'Moyen',
            'confidence': 50.0,
            'key_factors': [
                "Données insuffisantes pour analyse",
                "Complétez plus de tests",
                "Prédiction basique"
            ],
            'timeframe': f"{timeframe_months} mois",
            'recommendations': [
                "Complétez au moins 5 tests",
                "Travaillez régulièrement",
                "Suivez vos progressions"
            ],
            'metrics': {}
        }


def get_student_level_class(average_score):
    """
    Détermine la classe CSS du niveau d'un étudiant.
    
    Args:
        average_score: Score moyen de l'étudiant
        
    Returns:
        str: 'pro', 'moyen', ou 'faible'
    """
    if average_score >= 75:
        return 'pro'
    elif average_score >= 50:
        return 'moyen'
    else:
        return 'faible'


def get_student_level_name(average_score):
    """
    Détermine le nom du niveau d'un étudiant.
    
    Args:
        average_score: Score moyen de l'étudiant
        
    Returns:
        str: 'Pro', 'Moyen', ou 'Faible'
    """
    if average_score >= 75:
        return 'Pro'
    elif average_score >= 50:
        return 'Moyen'
    else:
        return 'Faible'
