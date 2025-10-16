from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json

from .subject_services import AISubjectAnalyticsService
from .models import SubjectAnalytics


@login_required
def subject_overview(request):
    """Vue d'aperçu des matières avec IA"""
    service = AISubjectAnalyticsService()
    
    # Obtenir l'aperçu des matières
    overview = service.get_student_subject_overview(request.user)
    
    # Calculer les statistiques globales
    stats = {
        'total_subjects': len(overview),
        'critical_count': len([s for s in overview if s['analytics'].risk_level == 'CRITICAL']),
        'high_risk_count': len([s for s in overview if s['analytics'].risk_level == 'HIGH']),
        'success_rate': sum(s['success_rate'] for s in overview) / len(overview) if overview else 0
    }
    
    context = {
        'page_title': 'Mes Matières - Analytics IA',
        'subjects_overview': overview,
        'stats': stats,
        'user': request.user
    }
    
    return render(request, 'analytics_dashboard/subject_overview.html', context)


@login_required
def subject_detail(request, subject_name):
    """Vue détaillée d'une matière"""
    service = AISubjectAnalyticsService()
    
    try:
        analytics = SubjectAnalytics.objects.get(user=request.user, subject_name=subject_name)
        
        # Obtenir l'historique des tests
        test_history = list(analytics.test_results.all().order_by('-test_date'))
        
        # Obtenir l'historique des visites (dernières 10)
        visit_history = list(analytics.visits.all().order_by('-visit_date')[:10])
        
        context = {
            'subject_name': subject_name,
            'analytics': analytics,
            'test_history': test_history,
            'visit_history': visit_history,
            'engagement_level': analytics.get_engagement_level(),
            'success_rate': analytics.calculate_success_rate(),
            'has_quiz_available': subject_name in service.quiz_database
        }
        
        return render(request, 'analytics_dashboard/subject_detail.html', context)
        
    except SubjectAnalytics.DoesNotExist:
        return redirect('analytics_dashboard:subject_overview')


@login_required
def class_subject_analytics(request, subject_name):
    """Analytics d'une matière pour toute la classe (pour les profs)"""
    if not request.user.is_staff:
        return redirect('analytics_dashboard:subject_overview')
    
    # Obtenir tous les analytics de cette matière
    all_analytics = SubjectAnalytics.objects.filter(subject_name=subject_name)
    
    # Calculer les stats de classe
    class_stats = {
        'total_students': all_analytics.count(),
        'average_score': sum(a.average_test_score for a in all_analytics) / all_analytics.count() if all_analytics else 0,
        'high_risk_students': all_analytics.filter(risk_level__in=['HIGH', 'CRITICAL']).count(),
        'top_performers': all_analytics.filter(average_test_score__gte=80).count()
    }
    
    context = {
        'subject_name': subject_name,
        'class_analytics': all_analytics,
        'class_stats': class_stats
    }
    
    return render(request, 'analytics_dashboard/class_subject_analytics.html', context)


@login_required
def subjects_class_list(request):
    """Liste des matières pour l'analytics de classe"""
    if not request.user.is_staff:
        return redirect('analytics_dashboard:subject_overview')
    
    # Obtenir toutes les matières disponibles
    subjects = SubjectAnalytics.objects.values_list('subject_name', flat=True).distinct()
    
    context = {
        'subjects': subjects
    }
    
    return render(request, 'analytics_dashboard/subjects_class_list.html', context)


@login_required
def student_study_plan(request):
    """Plan d'étude personnalisé"""
    service = AISubjectAnalyticsService()
    overview = service.get_student_subject_overview(request.user)
    
    # Générer le plan d'étude
    study_plan = {
        'urgent_subjects': [s for s in overview if s['analytics'].risk_level == 'CRITICAL'],
        'improvement_needed': [s for s in overview if s['analytics'].risk_level == 'HIGH'],
        'maintain_progress': [s for s in overview if s['analytics'].risk_level in ['MEDIUM', 'LOW']],
        'recommendations': []
    }
    
    # Générer des recommandations générales
    for subject in overview:
        if subject['analytics'].recommended_actions:
            for action in subject['analytics'].recommended_actions:
                if action.get('priority') in ['CRITICAL', 'HIGH']:
                    study_plan['recommendations'].append({
                        'subject': subject['subject_name'],
                        'action': action
                    })
    
    context = {
        'study_plan': study_plan,
        'overview': overview
    }
    
    return render(request, 'analytics_dashboard/study_plan.html', context)


# API Endpoints

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def record_visit_api(request):
    """API pour enregistrer une visite"""
    try:
        data = json.loads(request.body)
        subject_name = data.get('subject_name')
        duration = data.get('duration', 30)
        pages_viewed = data.get('pages_viewed', 1)
        
        service = AISubjectAnalyticsService()
        result = service.record_visit(request.user, subject_name, duration, pages_viewed)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def generate_quiz_api(request):
    """API pour générer un quiz"""
    try:
        data = json.loads(request.body)
        subject_name = data.get('subject_name')
        difficulty = data.get('difficulty', 'MEDIUM')
        
        service = AISubjectAnalyticsService()
        quiz_data = service.generate_quiz(subject_name, difficulty)
        
        return JsonResponse({
            'status': 'success',
            'quiz': quiz_data
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def submit_quiz_api(request):
    """API pour soumettre un quiz"""
    try:
        data = json.loads(request.body)
        subject_name = data.get('subject_name')
        quiz_data = data.get('quiz_data')
        user_answers = data.get('user_answers')
        
        service = AISubjectAnalyticsService()
        result = service.submit_quiz(request.user, subject_name, quiz_data, user_answers)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def record_test_result(request):
    """API pour enregistrer un résultat de test"""
    try:
        data = json.loads(request.body)
        subject_name = data.get('subject_name')
        score = data.get('score')
        
        # Simple enregistrement sans quiz
        service = AISubjectAnalyticsService()
        analytics, created = SubjectAnalytics.objects.get_or_create(
            user=request.user,
            subject_name=subject_name,
            defaults={'subject_code': subject_name[:3].upper()}
        )
        
        # Créer un résultat de test simple
        from .models import SubjectTestResult
        SubjectTestResult.objects.create(
            subject_analytics=analytics,
            test_name=f"Test {subject_name}",
            score=score,
            passed=score >= 60
        )
        
        # Mettre à jour les analytics
        service._update_test_metrics(analytics)
        service._calculate_ai_predictions(analytics)
        analytics.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def api_subject_data(request, subject_name):
    """API pour obtenir les données d'une matière"""
    try:
        analytics = SubjectAnalytics.objects.get(user=request.user, subject_name=subject_name)
        
        data = {
            'subject_name': analytics.subject_name,
            'total_visits': analytics.total_visits,
            'tests_taken': analytics.tests_taken,
            'average_score': analytics.average_test_score,
            'success_rate': analytics.calculate_success_rate(),
            'prediction': analytics.predicted_success_probability,
            'risk_level': analytics.risk_level,
            'engagement': analytics.get_engagement_level()
        }
        
        return JsonResponse(data)
        
    except SubjectAnalytics.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)


@login_required
def api_all_subjects_summary(request):
    """API pour obtenir un résumé de toutes les matières"""
    service = AISubjectAnalyticsService()
    overview = service.get_student_subject_overview(request.user)
    
    summary = []
    for subject in overview:
        summary.append({
            'subject_name': subject['subject_name'],
            'engagement_level': subject['engagement_level'],
            'success_rate': subject['success_rate'],
            'prediction': subject['prediction_summary']['probability'],
            'risk_level': subject['prediction_summary']['risk_level']
        })
    
    return JsonResponse({'subjects': summary})