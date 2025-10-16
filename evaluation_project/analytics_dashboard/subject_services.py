from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json
import math

from .models import SubjectAnalytics, SubjectVisit, SubjectTestResult, SubjectQuiz


class AISubjectAnalyticsService:
    """Service IA pour analyser les performances par matière avec vraies prédictions"""
    
    def __init__(self):
        self.subjects = [
            'Mathématiques', 'Physique', 'Chimie', 'Biologie',
            'Français', 'Anglais', 'Histoire', 'Géographie',
            'Informatique', 'Philosophie', 'Économie', 'Arts'
        ]
        self.quiz_database = self._initialize_quiz_database()
    
    def _initialize_quiz_database(self):
        """Initialise la base de données de quiz"""
        return {
            'Mathématiques': [
                {
                    'question': 'Quelle est la dérivée de x²?',
                    'options': ['x', '2x', 'x²', '2x²'],
                    'correct': 1,
                    'difficulty': 'MEDIUM'
                },
                {
                    'question': 'Résolvez: 2x + 5 = 13',
                    'options': ['x = 4', 'x = 9', 'x = 6', 'x = 8'],
                    'correct': 0,
                    'difficulty': 'EASY'
                },
                {
                    'question': 'Quelle est la limite de (sin x)/x quand x tend vers 0?',
                    'options': ['0', '1', '∞', 'indéterminée'],
                    'correct': 1,
                    'difficulty': 'HARD'
                }
            ],
            'Physique': [
                {
                    'question': 'Quelle est l\'unité de la force?',
                    'options': ['Joule', 'Newton', 'Watt', 'Pascal'],
                    'correct': 1,
                    'difficulty': 'EASY'
                },
                {
                    'question': 'La vitesse de la lumière dans le vide est:',
                    'options': ['3×10⁸ m/s', '3×10⁶ m/s', '3×10¹⁰ m/s', '3×10⁷ m/s'],
                    'correct': 0,
                    'difficulty': 'MEDIUM'
                }
            ],
            'Français': [
                {
                    'question': 'Qui a écrit "Les Misérables"?',
                    'options': ['Émile Zola', 'Victor Hugo', 'Gustave Flaubert', 'Honoré de Balzac'],
                    'correct': 1,
                    'difficulty': 'EASY'
                },
                {
                    'question': 'Quel est le passé simple de "voir" à la 3ème personne du singulier?',
                    'options': ['vit', 'voit', 'voyait', 'eut vu'],
                    'correct': 0,
                    'difficulty': 'MEDIUM'
                }
            ]
            # Ajouter d'autres matières...
        }
    
    def record_visit(self, user, subject_name, duration=30, pages_viewed=1):
        """Enregistre une visite et met à jour les analytics"""
        try:
            # Obtenir ou créer les analytics
            analytics, created = SubjectAnalytics.objects.get_or_create(
                user=user,
                subject_name=subject_name,
                defaults={'subject_code': subject_name[:3].upper()}
            )
            
            # Créer la visite
            visit = SubjectVisit.objects.create(
                subject_analytics=analytics,
                duration_minutes=duration,
                pages_viewed=pages_viewed,
                interaction_score=min(pages_viewed / 10, 1.0)
            )
            
            # Mettre à jour les métriques
            self._update_visit_metrics(analytics)
            self._calculate_ai_predictions(analytics)
            
            analytics.save()
            
            return {
                'status': 'success',
                'new_engagement': analytics.get_engagement_level(),
                'total_visits': analytics.total_visits,
                'prediction': analytics.predicted_success_probability
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_quiz(self, subject_name, difficulty='MEDIUM'):
        """Génère un quiz pour une matière"""
        questions = self.quiz_database.get(subject_name, [])
        if not questions:
            # Générer des questions génériques
            questions = self._generate_generic_questions(subject_name)
        
        # Sélectionner 5 questions aléatoires
        selected_questions = random.sample(questions, min(5, len(questions)))
        
        quiz_data = {
            'subject': subject_name,
            'questions': selected_questions,
            'total_questions': len(selected_questions),
            'max_score': len(selected_questions) * 20,  # 20 points par question
            'time_limit': 10,  # 10 minutes
            'generated_at': timezone.now().isoformat()
        }
        
        return quiz_data
    
    def submit_quiz(self, user, subject_name, quiz_data, user_answers):
        """Traite les résultats du quiz et met à jour les prédictions"""
        try:
            # Calculer le score
            correct_answers = 0
            total_questions = len(quiz_data['questions'])
            
            for i, question in enumerate(quiz_data['questions']):
                user_answer = user_answers.get(str(i))
                if user_answer is not None and int(user_answer) == question['correct']:
                    correct_answers += 1
            
            score = (correct_answers / total_questions) * 100
            passed = score >= 60  # 60% pour réussir
            
            # Obtenir les analytics
            analytics, created = SubjectAnalytics.objects.get_or_create(
                user=user,
                subject_name=subject_name,
                defaults={'subject_code': subject_name[:3].upper()}
            )
            
            # Créer le résultat de test
            test_result = SubjectTestResult.objects.create(
                subject_analytics=analytics,
                test_name=f"Quiz {subject_name} - {timezone.now().strftime('%d/%m/%Y')}",
                score=score,
                max_score=100.0,
                passed=passed,
                time_spent=random.randint(5, 15),  # Temps simulé
                quiz_data={
                    'questions': quiz_data['questions'],
                    'user_answers': user_answers,
                    'correct_answers': correct_answers,
                    'total_questions': total_questions
                }
            )
            
            # Mettre à jour les métriques de test
            self._update_test_metrics(analytics)
            
            # Recalculer les prédictions IA
            prediction_result = self._calculate_ai_predictions(analytics)
            
            analytics.save()
            
            return {
                'status': 'success',
                'score': score,
                'passed': passed,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'new_prediction': analytics.predicted_success_probability,
                'risk_level': analytics.risk_level,
                'recommendations': analytics.recommended_actions,
                'analytics_updated': True
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _update_visit_metrics(self, analytics):
        """Met à jour les métriques de visite"""
        visits = list(SubjectVisit.objects.filter(subject_analytics=analytics))
        
        analytics.total_visits = len(visits)
        
        if visits:
            analytics.total_time_spent = sum(visit.duration_minutes for visit in visits)
            analytics.last_visit = max(visit.visit_date for visit in visits)
            
            # Calculer la fréquence (visites par semaine)
            if len(visits) > 1:
                first_visit = min(visit.visit_date for visit in visits)
                days_diff = (timezone.now() - first_visit).days or 1
                analytics.visit_frequency = len(visits) / max(days_diff / 7, 1)
    
    def _update_test_metrics(self, analytics):
        """Met à jour les métriques de test"""
        test_results = list(SubjectTestResult.objects.filter(subject_analytics=analytics))
        
        analytics.tests_taken = len(test_results)
        
        if test_results:
            scores = [result.score for result in test_results]
            passed_tests = [result for result in test_results if result.passed]
            
            analytics.tests_passed = len(passed_tests)
            analytics.average_test_score = sum(scores) / len(scores)
            analytics.best_score = max(scores)
            analytics.worst_score = min(scores)
            
            test_dates = [result.test_date for result in test_results]
            analytics.first_test_date = min(test_dates)
            analytics.last_test_date = max(test_dates)
            
            # Analyser la tendance d'amélioration
            analytics.improvement_trend = self._calculate_improvement_trend(test_results)
    
    def _calculate_improvement_trend(self, test_results):
        """Calcule la tendance d'amélioration basée sur les derniers tests"""
        if len(test_results) < 2:
            return 'UNKNOWN'
        
        # Trier par date
        sorted_results = sorted(test_results, key=lambda x: x.test_date)
        
        if len(sorted_results) >= 4:
            # Comparer les 2 derniers avec les 2 premiers
            recent_avg = sum(r.score for r in sorted_results[-2:]) / 2
            older_avg = sum(r.score for r in sorted_results[:2]) / 2
        else:
            # Comparer le dernier avec le premier
            recent_avg = sorted_results[-1].score
            older_avg = sorted_results[0].score
        
        improvement = recent_avg - older_avg
        
        if improvement > 10:
            return 'IMPROVING'
        elif improvement < -10:
            return 'DECLINING'
        else:
            return 'STABLE'
    
    def _calculate_ai_predictions(self, analytics):
        """Calcule les prédictions IA basées sur des algorithmes réels"""
        
        # Facteurs d'analyse
        factors = {}
        prediction_score = 0.5  # Score de base
        
        # 1. Facteur d'engagement (30% du score)
        engagement_weight = 0.3
        if analytics.total_visits > 0:
            # Courbe logarithmique pour l'engagement
            visit_score = min(math.log(analytics.total_visits + 1) / math.log(20), 1.0)
            factors['engagement'] = visit_score
            prediction_score += visit_score * engagement_weight
        else:
            factors['engagement'] = 0.0
            prediction_score -= 0.2
        
        # 2. Performance aux tests (40% du score)
        test_weight = 0.4
        if analytics.tests_taken > 0:
            # Score basé sur la moyenne pondérée
            base_performance = analytics.average_test_score / 100
            
            # Bonus pour consistance (moins d'écart-type = mieux)
            if analytics.tests_taken > 1:
                test_results = list(SubjectTestResult.objects.filter(subject_analytics=analytics))
                scores = [r.score for r in test_results]
                std_dev = math.sqrt(sum((x - analytics.average_test_score) ** 2 for x in scores) / len(scores))
                consistency_bonus = max(0, (30 - std_dev) / 30 * 0.1)  # Max 10% bonus
                base_performance += consistency_bonus
            
            factors['test_performance'] = min(base_performance, 1.0)
            prediction_score += factors['test_performance'] * test_weight
        else:
            factors['test_performance'] = 0.0
            prediction_score -= 0.3
        
        # 3. Régularité des visites (15% du score)
        regularity_weight = 0.15
        if analytics.visit_frequency > 0:
            # Courbe optimale: 2-3 visites par semaine
            optimal_frequency = 2.5
            regularity_score = 1.0 - abs(analytics.visit_frequency - optimal_frequency) / optimal_frequency
            regularity_score = max(0, min(regularity_score, 1.0))
            factors['regularity'] = regularity_score
            prediction_score += regularity_score * regularity_weight
        else:
            factors['regularity'] = 0.0
            prediction_score -= 0.1
        
        # 4. Tendance d'amélioration (10% du score)
        trend_weight = 0.1
        trend_scores = {
            'IMPROVING': 0.15,
            'STABLE': 0.05,
            'DECLINING': -0.15,
            'UNKNOWN': 0.0
        }
        trend_impact = trend_scores.get(analytics.improvement_trend, 0.0)
        factors['improvement_trend'] = trend_impact
        prediction_score += trend_impact
        
        # 5. Facteur temps (5% du score)
        time_weight = 0.05
        if analytics.total_time_spent > 0:
            # Temps optimal: environ 5 heures (300 minutes)
            time_score = min(analytics.total_time_spent / 300, 1.0)
            factors['time_investment'] = time_score
            prediction_score += time_score * time_weight
        else:
            factors['time_investment'] = 0.0
        
        # Normaliser le score final
        analytics.predicted_success_probability = max(0.0, min(1.0, prediction_score))
        
        # Déterminer le niveau de risque
        if analytics.predicted_success_probability >= 0.8:
            analytics.risk_level = 'LOW'
        elif analytics.predicted_success_probability >= 0.6:
            analytics.risk_level = 'MEDIUM'
        elif analytics.predicted_success_probability >= 0.4:
            analytics.risk_level = 'HIGH'
        else:
            analytics.risk_level = 'CRITICAL'
        
        # Calculer la confiance de la prédiction
        data_quality = min((analytics.total_visits + analytics.tests_taken * 2) / 20, 1.0)
        analytics.prediction_confidence = data_quality
        
        # Générer des recommandations intelligentes
        analytics.recommended_actions = self._generate_smart_recommendations(analytics, factors)
        analytics.prediction_factors = factors
        
        return {
            'probability': analytics.predicted_success_probability,
            'risk_level': analytics.risk_level,
            'confidence': analytics.prediction_confidence,
            'factors': factors
        }
    
    def _generate_smart_recommendations(self, analytics, factors):
        """Génère des recommandations intelligentes basées sur l'IA"""
        recommendations = []
        
        # Recommandations basées sur l'engagement
        if factors.get('engagement', 0) < 0.3:
            if analytics.total_visits == 0:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'CRITICAL',
                    'message': 'Commencez à étudier cette matière - aucune activité détectée',
                    'action': 'visit_subject'
                })
            else:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'HIGH',
                    'message': f'Augmentez vos visites - objectif: {max(15 - analytics.total_visits, 5)} visites supplémentaires',
                    'action': 'increase_visits'
                })
        
        # Recommandations basées sur les tests
        if factors.get('test_performance', 0) < 0.6:
            if analytics.tests_taken == 0:
                recommendations.append({
                    'type': 'testing',
                    'priority': 'CRITICAL',
                    'message': 'Passez votre premier test pour évaluer votre niveau',
                    'action': 'take_test'
                })
            elif analytics.average_test_score < 60:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'HIGH',
                    'message': f'Améliorez vos résultats - score actuel: {analytics.average_test_score:.1f}%, objectif: 70%+',
                    'action': 'improve_study'
                })
        
        # Recommandations basées sur la régularité
        if factors.get('regularity', 0) < 0.5:
            recommendations.append({
                'type': 'regularity',
                'priority': 'MEDIUM',
                'message': 'Étudiez plus régulièrement - idéal: 2-3 sessions par semaine',
                'action': 'create_schedule'
            })
        
        # Recommandations basées sur la tendance
        if analytics.improvement_trend == 'DECLINING':
            recommendations.append({
                'type': 'intervention',
                'priority': 'CRITICAL',
                'message': 'Vos résultats baissent - changez votre méthode d\'étude ou demandez de l\'aide',
                'action': 'seek_help'
            })
        elif analytics.improvement_trend == 'IMPROVING':
            recommendations.append({
                'type': 'encouragement',
                'priority': 'LOW',
                'message': 'Excellente progression ! Continuez vos efforts',
                'action': 'maintain_effort'
            })
        
        # Recommandations personnalisées selon le niveau de risque
        if analytics.risk_level == 'CRITICAL':
            recommendations.append({
                'type': 'urgent',
                'priority': 'CRITICAL',
                'message': 'ALERTE: Risque d\'échec élevé - action immédiate requise',
                'action': 'emergency_support'
            })
        elif analytics.risk_level == 'LOW' and analytics.predicted_success_probability > 0.9:
            recommendations.append({
                'type': 'excellence',
                'priority': 'LOW',
                'message': 'Vous excellez dans cette matière ! Aidez vos camarades',
                'action': 'peer_tutoring'
            })
        
        return recommendations
    
    def _generate_generic_questions(self, subject_name):
        """Génère des questions génériques pour les matières sans quiz prédéfini"""
        return [
            {
                'question': f'Question de base en {subject_name}',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct': 0,
                'difficulty': 'MEDIUM'
            }
        ]
    
    def get_student_subject_overview(self, user):
        """Obtient un aperçu de toutes les matières avec prédictions IA"""
        overview = []
        
        for subject in self.subjects:
            try:
                analytics, created = SubjectAnalytics.objects.get_or_create(
                    user=user,
                    subject_name=subject,
                    defaults={'subject_code': subject[:3].upper()}
                )
                
                # Si nouveau, initialiser avec des prédictions de base
                if created:
                    self._calculate_ai_predictions(analytics)
                    analytics.save()
                
                overview.append({
                    'subject_name': subject,
                    'analytics': analytics,
                    'engagement_level': analytics.get_engagement_level(),
                    'success_rate': analytics.calculate_success_rate(),
                    'prediction_summary': {
                        'probability': analytics.predicted_success_probability,
                        'risk_level': analytics.risk_level,
                        'confidence': analytics.prediction_confidence
                    },
                    'has_quiz_available': subject in self.quiz_database
                })
                
            except Exception as e:
                print(f"Erreur pour {subject}: {e}")
                # Créer des données par défaut
                overview.append({
                    'subject_name': subject,
                    'analytics': SubjectAnalytics(
                        user=user,
                        subject_name=subject,
                        subject_code=subject[:3].upper()
                    ),
                    'engagement_level': 'AUCUN',
                    'success_rate': 0.0,
                    'prediction_summary': {
                        'probability': 0.5,
                        'risk_level': 'MEDIUM',
                        'confidence': 0.0
                    },
                    'has_quiz_available': False
                })
        
        return overview