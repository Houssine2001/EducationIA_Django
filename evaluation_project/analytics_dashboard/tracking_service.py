# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\tracking_service.py

from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import StudentAnalytics, PerformanceTrend
from .services import AnalyticsService
import json

class StudentTrackingService:
    """Service pour tracker l'évolution des étudiants en temps réel"""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
    
    def record_test_completion(self, student, test_name, score, subject="General"):
        """Enregistrer la completion d'un test par un étudiant"""
        try:
            # Créer ou mettre à jour l'entrée de performance
            performance_trend = PerformanceTrend.objects.create(
                student=student,
                score=score,
                subject=subject,
                date=timezone.now()
            )
            
            # Mettre à jour les analytics de l'étudiant
            self.analytics_service.update_student_analytics(student)
            
            # Calculer l'évolution récente
            evolution_data = self._calculate_evolution(student)
            
            return {
                'success': True,
                'performance_trend_id': performance_trend.id,
                'evolution_data': evolution_data,
                'message': f'Test {test_name} enregistré avec succès'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de l\'enregistrement du test'
            }
    
    def record_course_visit(self, student, course_name, duration_minutes=None):
        """Enregistrer la visite d'un cours par un étudiant"""
        try:
            # Mettre à jour la dernière activité
            analytics, created = StudentAnalytics.objects.get_or_create(
                user=student,
                defaults={
                    'success_rate': 0.0,
                    'average_score': 0.0,
                    'total_tests_taken': 0,
                    'risk_level': 'LOW'
                }
            )
            
            analytics.last_activity = timezone.now()
            
            # Ajouter des données de visite si disponibles
            visit_data = {
                'course_name': course_name,
                'visit_time': timezone.now().isoformat(),
                'duration_minutes': duration_minutes
            }
            
            # Stocker l'historique des visites
            if hasattr(analytics, 'visit_history'):
                try:
                    visits = json.loads(analytics.visit_history or '[]')
                except:
                    visits = []
            else:
                visits = []
            
            visits.append(visit_data)
            
            # Garder seulement les 50 dernières visites
            visits = visits[-50:]
            
            # Mettre à jour le score d'engagement
            analytics.engagement_score = self._calculate_engagement_score(visits)
            analytics.save()
            
            return {
                'success': True,
                'message': f'Visite du cours {course_name} enregistrée'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de l\'enregistrement de la visite'
            }
    
    def _calculate_evolution(self, student):
        """Calculer l'évolution récente d'un étudiant"""
        try:
            # Récupérer les 10 derniers scores
            recent_trends = PerformanceTrend.objects.filter(
                student=student
            ).order_by('-date')[:10]
            
            if recent_trends.count() < 2:
                return {
                    'trend': 'INSUFFICIENT_DATA',
                    'percentage_change': 0,
                    'message': 'Données insuffisantes'
                }
            
            # Calculer la tendance
            scores = [trend.score for trend in reversed(recent_trends)]
            
            # Moyenne des 3 premiers vs 3 derniers scores
            if len(scores) >= 6:
                early_avg = sum(scores[:3]) / 3
                recent_avg = sum(scores[-3:]) / 3
            else:
                early_avg = scores[0]
                recent_avg = scores[-1]
            
            percentage_change = ((recent_avg - early_avg) / early_avg) * 100 if early_avg > 0 else 0
            
            # Déterminer la tendance
            if percentage_change > 10:
                trend = 'IMPROVING'
            elif percentage_change < -10:
                trend = 'DECLINING'
            else:
                trend = 'STABLE'
            
            return {
                'trend': trend,
                'percentage_change': round(percentage_change, 1),
                'early_average': round(early_avg, 1),
                'recent_average': round(recent_avg, 1),
                'total_tests': len(scores)
            }
            
        except Exception as e:
            return {
                'trend': 'ERROR',
                'error': str(e),
                'percentage_change': 0
            }
    
    def _calculate_engagement_score(self, visits):
        """Calculer le score d'engagement basé sur les visites"""
        try:
            if not visits:
                return 0.0
            
            # Analyser la fréquence des visites
            now = timezone.now()
            recent_visits = []
            
            for visit in visits:
                try:
                    visit_time = datetime.fromisoformat(visit['visit_time'].replace('Z', '+00:00'))
                    if (now - visit_time).days <= 7:  # Visites de la semaine
                        recent_visits.append(visit)
                except:
                    continue
            
            # Score basé sur la fréquence et la durée
            frequency_score = min(len(recent_visits) / 10.0, 1.0)  # Max 10 visites par semaine
            
            # Score de durée moyenne
            total_duration = 0
            duration_count = 0
            
            for visit in recent_visits:
                if visit.get('duration_minutes'):
                    total_duration += visit['duration_minutes']
                    duration_count += 1
            
            if duration_count > 0:
                avg_duration = total_duration / duration_count
                duration_score = min(avg_duration / 60.0, 1.0)  # Max 1h par visite
            else:
                duration_score = 0.3  # Score par défaut si pas de durée
            
            # Score final (moyenne pondérée)
            engagement_score = (frequency_score * 0.7) + (duration_score * 0.3)
            
            return round(engagement_score, 2)
            
        except Exception:
            return 0.0
    
    def get_student_evolution_summary(self, student):
        """Récupérer un résumé de l'évolution d'un étudiant"""
        try:
            analytics = StudentAnalytics.objects.filter(user=student).first()
            evolution_data = self._calculate_evolution(student)
            
            # Récupérer les tendances récentes
            recent_trends = PerformanceTrend.objects.filter(
                student=student
            ).order_by('-date')[:5]
            
            # Calculer les statistiques
            total_tests = PerformanceTrend.objects.filter(student=student).count()
            
            # Progression par matière
            subject_progress = {}
            for trend in PerformanceTrend.objects.filter(student=student):
                subject = trend.subject
                if subject not in subject_progress:
                    subject_progress[subject] = []
                subject_progress[subject].append(trend.score)
            
            # Moyennes par matière
            subject_averages = {}
            for subject, scores in subject_progress.items():
                subject_averages[subject] = {
                    'average': sum(scores) / len(scores),
                    'total_tests': len(scores),
                    'best_score': max(scores),
                    'latest_score': scores[-1] if scores else 0
                }
            
            return {
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}".strip() or student.username,
                'analytics': {
                    'success_rate': analytics.success_rate if analytics else 0,
                    'average_score': analytics.average_score if analytics else 0,
                    'risk_level': analytics.risk_level if analytics else 'LOW',
                    'engagement_score': getattr(analytics, 'engagement_score', 0),
                    'last_activity': analytics.last_activity if analytics else None
                },
                'evolution': evolution_data,
                'recent_performance': [
                    {
                        'date': trend.date,
                        'score': trend.score,
                        'subject': trend.subject,
                        'test_name': 'Test'  # Champ retiré du modèle
                    } for trend in recent_trends
                ],
                'statistics': {
                    'total_tests': total_tests,
                    'subjects_studied': len(subject_averages),
                    'best_subject': max(subject_averages.items(), 
                                      key=lambda x: x[1]['average'])[0] if subject_averages else None,
                    'improvement_needed': min(subject_averages.items(), 
                                            key=lambda x: x[1]['average'])[0] if subject_averages else None
                },
                'subject_performance': subject_averages
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'student_id': student.id,
                'message': 'Erreur lors de la récupération des données'
            }
    
    def get_class_evolution_summary(self, students_queryset=None):
        """Récupérer un résumé d'évolution pour une classe"""
        try:
            if students_queryset is None:
                students_queryset = User.objects.filter(is_staff=False)
            
            class_data = {
                'total_students': students_queryset.count(),
                'active_students': 0,
                'total_tests': 0,
                'average_performance': 0,
                'students_evolution': []
            }
            
            total_score = 0
            active_count = 0
            
            for student in students_queryset:
                student_summary = self.get_student_evolution_summary(student)
                
                if not student_summary.get('error'):
                    class_data['students_evolution'].append(student_summary)
                    class_data['total_tests'] += student_summary['statistics']['total_tests']
                    
                    # Vérifier l'activité récente
                    if student_summary['analytics']['last_activity']:
                        last_activity = student_summary['analytics']['last_activity']
                        if isinstance(last_activity, str):
                            last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                        
                        if (timezone.now() - last_activity).days <= 7:
                            active_count += 1
                    
                    # Calculer la moyenne
                    total_score += student_summary['analytics']['average_score']
            
            class_data['active_students'] = active_count
            if class_data['students_evolution']:
                class_data['average_performance'] = total_score / len(class_data['students_evolution'])
            
            # Calculer les tendances de classe
            improving_count = sum(1 for s in class_data['students_evolution'] 
                                if s['evolution']['trend'] == 'IMPROVING')
            declining_count = sum(1 for s in class_data['students_evolution'] 
                                if s['evolution']['trend'] == 'DECLINING')
            
            class_data['trends'] = {
                'improving': improving_count,
                'declining': declining_count,
                'stable': len(class_data['students_evolution']) - improving_count - declining_count
            }
            
            return class_data
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Erreur lors de la récupération des données de classe'
            }
    
    def generate_real_time_dashboard_data(self, user):
        """Générer les données en temps réel pour le dashboard"""
        try:
            if user.is_staff:
                # Données administrateur
                return self.get_class_evolution_summary()
            else:
                # Données étudiant
                return self.get_student_evolution_summary(user)
                
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Erreur lors de la génération des données temps réel'
            }