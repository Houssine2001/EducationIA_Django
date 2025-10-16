from djongo import models
from django.contrib.auth.models import User
from django.utils import timezone
from bson import ObjectId
import json
import numpy as np
from datetime import datetime, timedelta


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
    
    # Nouvelles métriques pour prédictions IA réelles
    engagement_score = models.FloatField(default=0.0)  # 0-1
    consistency_score = models.FloatField(default=0.0)  # 0-1
    improvement_trend = models.FloatField(default=0.0)  # -1 à 1
    difficulty_adaptation = models.FloatField(default=0.0)  # 0-1
    time_management_score = models.FloatField(default=0.0)  # 0-1
    
    # Prédictions IA calculées
    predicted_success_probability = models.FloatField(default=0.5)
    risk_level = models.CharField(max_length=20, default='MEDIUM')
    prediction_confidence = models.FloatField(default=0.0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_engagement_score(self):
        """Calcule le score d'engagement basé sur l'activité"""
        if self.total_exercises == 0:
            return 0.0
        
        # Facteurs d'engagement
        completion_rate = self.completed_exercises / max(self.total_exercises, 1)
        frequency_factor = min(self.total_exercises / 10, 1.0)  # Plus d'exercices = plus d'engagement
        
        # Score basé sur la complétion et la fréquence
        engagement = (completion_rate * 0.7) + (frequency_factor * 0.3)
        return min(max(engagement, 0.0), 1.0)
    
    def calculate_consistency_score(self):
        """Calcule le score de consistance basé sur les performances"""
        try:
            from .models import PerformanceTrend
            recent_trends = PerformanceTrend.objects.filter(
                student=self.user,
                date__gte=timezone.now() - timedelta(days=30)
            ).order_by('date')
            
            if len(recent_trends) < 3:
                return 0.5  # Score neutre si pas assez de données
            
            scores = [trend.score for trend in recent_trends]
            std_dev = np.std(scores)
            mean_score = np.mean(scores)
            
            # Plus la variance est faible, plus la consistance est élevée
            if mean_score > 0:
                consistency = max(0, 1 - (std_dev / mean_score))
            else:
                consistency = 0.0
                
            return min(max(consistency, 0.0), 1.0)
        except:
            return 0.5
    
    def calculate_improvement_trend(self):
        """Calcule la tendance d'amélioration"""
        try:
            from .models import PerformanceTrend
            recent_trends = PerformanceTrend.objects.filter(
                student=self.user,
                date__gte=timezone.now() - timedelta(days=30)
            ).order_by('date')
            
            if len(recent_trends) < 2:
                return 0.0
            
            scores = [trend.score for trend in recent_trends]
            
            # Calcul de la pente de régression linéaire simple
            n = len(scores)
            x = list(range(n))
            
            x_mean = sum(x) / n
            y_mean = sum(scores) / n
            
            numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 0.0
            
            slope = numerator / denominator
            
            # Normaliser entre -1 et 1
            return min(max(slope / 10, -1.0), 1.0)
        except:
            return 0.0
    
    def calculate_ai_prediction(self):
        """Calcule la prédiction IA réelle basée sur les métriques"""
        # Mettre à jour les métriques
        self.engagement_score = self.calculate_engagement_score()
        self.consistency_score = self.calculate_consistency_score()
        self.improvement_trend = self.calculate_improvement_trend()
        
        # Calcul de l'adaptation à la difficulté
        if self.average_score > 0:
            self.difficulty_adaptation = min(self.success_rate / 100.0, 1.0)
        else:
            self.difficulty_adaptation = 0.0
        
        # Calcul du score de gestion du temps (basé sur la consistance)
        self.time_management_score = self.consistency_score
        
        # Algorithme de prédiction IA
        weights = {
            'average_score': 0.30,
            'engagement': 0.25,
            'consistency': 0.20,
            'improvement': 0.15,
            'difficulty_adaptation': 0.10
        }
        
        # Normaliser les scores
        normalized_score = min(self.average_score / 100.0, 1.0)
        normalized_improvement = (self.improvement_trend + 1) / 2  # -1,1 -> 0,1
        
        # Calcul de la probabilité de succès
        probability = (
            weights['average_score'] * normalized_score +
            weights['engagement'] * self.engagement_score +
            weights['consistency'] * self.consistency_score +
            weights['improvement'] * normalized_improvement +
            weights['difficulty_adaptation'] * self.difficulty_adaptation
        )
        
        self.predicted_success_probability = min(max(probability, 0.0), 1.0)
        
        # Calcul du niveau de risque
        if probability >= 0.8:
            self.risk_level = 'LOW'
        elif probability >= 0.6:
            self.risk_level = 'MEDIUM'
        elif probability >= 0.4:
            self.risk_level = 'HIGH'
        else:
            self.risk_level = 'CRITICAL'
        
        # Calcul de la confiance de prédiction
        data_quality = min(self.total_exercises / 10.0, 1.0)  # Plus de données = plus de confiance
        metric_consistency = (self.engagement_score + self.consistency_score) / 2
        self.prediction_confidence = (data_quality * 0.6) + (metric_consistency * 0.4)
        
        return {
            'probability': self.predicted_success_probability,
            'risk_level': self.risk_level,
            'confidence': self.prediction_confidence,
            'factors': {
                'engagement': self.engagement_score,
                'consistency': self.consistency_score,
                'improvement': self.improvement_trend,
                'difficulty_adaptation': self.difficulty_adaptation
            }
        }
    
    def get_risk_level_display(self):
        """Affichage du niveau de risque"""
        levels = {
            'LOW': 'Faible',
            'MEDIUM': 'Moyen',
            'HIGH': 'Élevé',
            'CRITICAL': 'Critique'
        }
        return levels.get(self.risk_level, 'Moyen')
    
    def get_ai_recommendations(self):
        """Génère des recommandations IA basées sur les métriques"""
        recommendations = []
        
        if self.engagement_score < 0.3:
            recommendations.append({
                'type': 'ENGAGEMENT',
                'priority': 'HIGH',
                'message': 'Augmentez votre engagement en complétant plus d\'exercices régulièrement.'
            })
        
        if self.consistency_score < 0.4:
            recommendations.append({
                'type': 'CONSISTENCY',
                'priority': 'MEDIUM',
                'message': 'Travaillez sur la régularité de vos performances.'
            })
        
        if self.improvement_trend < -0.2:
            recommendations.append({
                'type': 'IMPROVEMENT',
                'priority': 'CRITICAL',
                'message': 'Vos performances déclinent. Consultez un professeur rapidement.'
            })
        
        if self.average_score < 50:
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'HIGH',
                'message': 'Renforcez vos bases fondamentales dans cette matière.'
            })
        
        return recommendations


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
    raw_data = models.JSONField(default=dict)  # Stockage des métriques utilisées
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
    
    def calculate_real_ai_prediction(self):
        """Calcule une prédiction IA réelle basée sur les données"""
        # Facteurs pour la prédiction
        factors = {}
        
        # 1. Performance actuelle (30%)
        if self.tests_taken > 0:
            performance_factor = min(self.average_test_score / 100.0, 1.0)
        else:
            performance_factor = 0.5
        factors['performance'] = performance_factor
        
        # 2. Tendance d'amélioration (25%)
        if self.tests_taken >= 3:
            # Calculer la tendance basée sur les derniers tests
            recent_tests = SubjectTestResult.objects.filter(
                subject_analytics=self
            ).order_by('-test_date')[:5]
            
            if len(recent_tests) >= 2:
                scores = [test.score for test in recent_tests]
                first_half = scores[:len(scores)//2]
                second_half = scores[len(scores)//2:]
                
                if first_half and second_half:
                    improvement = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
                    trend_factor = min(max((improvement + 50) / 100.0, 0), 1)
                else:
                    trend_factor = 0.5
            else:
                trend_factor = 0.5
        else:
            trend_factor = 0.5
        factors['trend'] = trend_factor
        
        # 3. Engagement/Régularité (20%)
        if self.total_visits > 0:
            engagement_factor = min(self.total_visits / 20.0, 1.0)
            
            # Bonus pour régularité récente
            if self.last_visit:
                days_since_last = (timezone.now() - self.last_visit).days
                recency_bonus = max(0, 1 - (days_since_last / 7.0))  # Bonus si visite récente
                engagement_factor = min(engagement_factor + (recency_bonus * 0.2), 1.0)
        else:
            engagement_factor = 0.0
        factors['engagement'] = engagement_factor
        
        # 4. Consistance (15%)
        if self.tests_taken >= 3:
            scores = [test.score for test in SubjectTestResult.objects.filter(
                subject_analytics=self
            ).order_by('-test_date')[:10]]
            
            if scores:
                variance = np.var(scores)
                mean_score = np.mean(scores)
                if mean_score > 0:
                    consistency_factor = max(0, 1 - (variance / (mean_score * mean_score)))
                else:
                    consistency_factor = 0
            else:
                consistency_factor = 0.5
        else:
            consistency_factor = 0.5
        factors['consistency'] = consistency_factor
        
        # 5. Adaptation difficulté (10%)
        if self.tests_taken > 0:
            success_rate = self.tests_passed / self.tests_taken
            adaptation_factor = success_rate
        else:
            adaptation_factor = 0.5
        factors['adaptation'] = adaptation_factor
        
        # Calcul de la prédiction finale
        weights = {
            'performance': 0.30,
            'trend': 0.25,
            'engagement': 0.20,
            'consistency': 0.15,
            'adaptation': 0.10
        }
        
        prediction = sum(factors[key] * weights[key] for key in weights.keys())
        
        # Ajustements basés sur le contexte
        if self.tests_taken < 3:
            prediction *= 0.8  # Moins de confiance avec peu de données
        
        if self.total_visits == 0:
            prediction *= 0.6  # Pénalité pour absence d'engagement
        
        # Mettre à jour les champs
        self.predicted_success_probability = min(max(prediction, 0.0), 1.0)
        self.prediction_factors = factors
        
        # Déterminer le niveau de risque
        if prediction >= 0.8:
            self.risk_level = 'LOW'
        elif prediction >= 0.6:
            self.risk_level = 'MEDIUM'  
        elif prediction >= 0.4:
            self.risk_level = 'HIGH'
        else:
            self.risk_level = 'CRITICAL'
        
        # Calculer la confiance
        data_points = self.tests_taken + (self.total_visits / 5)
        self.prediction_confidence = min(data_points / 15.0, 1.0)
        
        # Générer des recommandations
        self.recommended_actions = self.generate_ai_recommendations(factors)
        
        return {
            'probability': self.predicted_success_probability,
            'confidence': self.prediction_confidence,
            'risk_level': self.risk_level,
            'factors': factors
        }
    
    def generate_ai_recommendations(self, factors):
        """Génère des recommandations basées sur l'analyse IA"""
        recommendations = []
        
        if factors['performance'] < 0.5:
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'HIGH',
                'message': f'Votre score moyen de {self.average_test_score:.1f}% nécessite une attention immédiate. Révisez les concepts de base.'
            })
        
        if factors['engagement'] < 0.3:
            recommendations.append({
                'type': 'ENGAGEMENT', 
                'priority': 'CRITICAL',
                'message': f'Avec seulement {self.total_visits} visite(s), augmentez votre engagement quotidien.'
            })
        
        if factors['trend'] < 0.4:
            recommendations.append({
                'type': 'TREND',
                'priority': 'HIGH',
                'message': 'Vos performances déclinent. Consultez votre professeur ou demandez de l\'aide.'
            })
        
        if factors['consistency'] < 0.4:
            recommendations.append({
                'type': 'CONSISTENCY',
                'priority': 'MEDIUM',
                'message': 'Vos résultats varient beaucoup. Adoptez une méthode de travail plus régulière.'
            })
        
        return recommendations
    
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