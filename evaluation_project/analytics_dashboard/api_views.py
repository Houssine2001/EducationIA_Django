# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils import timezone
from .tracking_service import StudentTrackingService
import json

tracking_service = StudentTrackingService()

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_record_test_completion(request):
    """API pour enregistrer la completion d'un test"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        data = json.loads(request.body)
        
        # Récupérer les paramètres
        test_name = data.get('test_name', 'Test')
        score = float(data.get('score', 0))
        subject = data.get('subject', 'General')
        
        # Enregistrer la completion
        result = tracking_service.record_test_completion(
            student=request.user,
            test_name=test_name,
            score=score,
            subject=subject
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'enregistrement du test'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_record_course_visit(request):
    """API pour enregistrer une visite de cours"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        data = json.loads(request.body)
        
        # Récupérer les paramètres
        course_name = data.get('course_name', 'Course')
        duration_minutes = data.get('duration_minutes', None)
        
        if duration_minutes:
            duration_minutes = float(duration_minutes)
        
        # Enregistrer la visite
        result = tracking_service.record_course_visit(
            student=request.user,
            course_name=course_name,
            duration_minutes=duration_minutes
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'enregistrement de la visite'
        }, status=500)

@login_required
def api_get_student_evolution(request, student_id=None):
    """API pour récupérer l'évolution d'un étudiant"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        # Déterminer l'étudiant à analyser
        if student_id and request.user.is_staff:
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'error': 'Étudiant non trouvé'
                }, status=404)
        else:
            student = request.user
        
        # Vérifier les permissions
        if not request.user.is_staff and student != request.user:
            return JsonResponse({
                'error': 'Permission refusée'
            }, status=403)
        
        # Récupérer les données d'évolution
        evolution_data = tracking_service.get_student_evolution_summary(student)
        
        return JsonResponse(evolution_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la récupération des données'
        }, status=500)

@login_required
def api_get_class_evolution(request):
    """API pour récupérer l'évolution d'une classe"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Permission refusée - Administrateur requis'
        }, status=403)
    
    try:
        # Récupérer les paramètres de filtrage
        class_filter = request.GET.get('class_filter', None)
        
        # Définir le queryset d'étudiants
        students_queryset = User.objects.filter(is_staff=False)
        
        if class_filter:
            # Simuler un filtrage par classe basé sur la première lettre
            students_queryset = students_queryset.filter(
                username__istartswith=class_filter.lower()
            )
        
        # Récupérer les données d'évolution de classe
        class_data = tracking_service.get_class_evolution_summary(students_queryset)
        
        return JsonResponse(class_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la récupération des données de classe'
        }, status=500)

@login_required
def api_get_real_time_dashboard(request):
    """API pour récupérer les données du dashboard en temps réel"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        dashboard_data = tracking_service.generate_real_time_dashboard_data(request.user)
        
        # Ajouter des métadonnées
        dashboard_data['timestamp'] = timezone.now().isoformat()
        dashboard_data['user_type'] = 'admin' if request.user.is_staff else 'student'
        
        return JsonResponse(dashboard_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la génération des données temps réel'
        }, status=500)

@login_required
def api_get_performance_trends(request):
    """API pour récupérer les tendances de performance"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        from .models import PerformanceTrend
        from datetime import timedelta
        
        # Récupérer les paramètres
        days = int(request.GET.get('days', 30))
        student_id = request.GET.get('student_id')
        
        # Définir la date limite
        start_date = timezone.now() - timedelta(days=days)
        
        # Construire la requête
        queryset = PerformanceTrend.objects.filter(date__gte=start_date)
        
        if student_id and request.user.is_staff:
            try:
                student = User.objects.get(pk=student_id)
                queryset = queryset.filter(student=student)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Étudiant non trouvé'}, status=404)
        elif not request.user.is_staff:
            queryset = queryset.filter(student=request.user)
        
        # Organiser les données par date
        trends_data = {}
        for trend in queryset.order_by('date'):
            date_key = trend.date.strftime('%Y-%m-%d')
            if date_key not in trends_data:
                trends_data[date_key] = {
                    'date': date_key,
                    'scores': [],
                    'subjects': [],
                    'tests': []
                }
            
            trends_data[date_key]['scores'].append(trend.score)
            trends_data[date_key]['subjects'].append(trend.subject)
            trends_data[date_key]['tests'].append(
f'Test {trend.subject}'
            )
        
        # Calculer les moyennes par jour
        processed_data = []
        for date_data in trends_data.values():
            if date_data['scores']:
                processed_data.append({
                    'date': date_data['date'],
                    'average_score': sum(date_data['scores']) / len(date_data['scores']),
                    'total_tests': len(date_data['scores']),
                    'subjects': list(set(date_data['subjects'])),
                    'best_score': max(date_data['scores']),
                    'worst_score': min(date_data['scores'])
                })
        
        # Trier par date
        processed_data.sort(key=lambda x: x['date'])
        
        return JsonResponse({
            'trends': processed_data,
            'period_days': days,
            'total_data_points': len(processed_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la récupération des tendances'
        }, status=500)

@login_required
def api_get_engagement_metrics(request):
    """API pour récupérer les métriques d'engagement"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\api_views.py
    try:
        from .models import StudentAnalytics
        
        if request.user.is_staff:
            # Données globales pour admin
            analytics_queryset = StudentAnalytics.objects.all()
            
            engagement_data = {
                'total_students': analytics_queryset.count(),
                'highly_engaged': analytics_queryset.filter(
                    engagement_score__gte=0.8
                ).count(),
                'moderately_engaged': analytics_queryset.filter(
                    engagement_score__gte=0.5,
                    engagement_score__lt=0.8
                ).count(),
                'low_engagement': analytics_queryset.filter(
                    engagement_score__lt=0.5
                ).count(),
                'average_engagement': 0
            }
            
            # Calculer la moyenne d'engagement
            engagement_scores = [
                a.engagement_score for a in analytics_queryset 
                if hasattr(a, 'engagement_score') and a.engagement_score
            ]
            
            if engagement_scores:
                engagement_data['average_engagement'] = sum(engagement_scores) / len(engagement_scores)
            
        else:
            # Données personnelles pour étudiant
            analytics = StudentAnalytics.objects.filter(user=request.user).first()
            
            engagement_data = {
                'personal_engagement': getattr(analytics, 'engagement_score', 0) if analytics else 0,
                'consistency_score': getattr(analytics, 'consistency_score', 0) if analytics else 0,
                'learning_velocity': getattr(analytics, 'learning_velocity', 0) if analytics else 0,
                'last_activity': analytics.last_activity.isoformat() if analytics and analytics.last_activity else None
            }
        
        return JsonResponse(engagement_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la récupération des métriques d\'engagement'
        }, status=500)