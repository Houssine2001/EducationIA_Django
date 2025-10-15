from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel
from .services import AnalyticsService, PredictionService, ReportService


@login_required
def dashboard_overview(request):
    """Vue principale du dashboard analytics"""
    # Initialiser le service
    analytics_service = AnalyticsService()
    
    # Mettre à jour les analytics de l'utilisateur actuel
    if request.user.is_authenticated:
        try:
            analytics_service.update_student_analytics(request.user)
        except Exception as e:
            pass  # Ignorer les erreurs pour l'instant
    
    # Statistiques générales
    total_students = User.objects.count()
    total_analytics = StudentAnalytics.objects.count()
    
    # Répartition des risques
    risk_stats = StudentAnalytics.objects.values('risk_level').annotate(
        count=Count('risk_level')
    )
    
    context = {
        'page_title': 'Dashboard Analytics IA',
        'total_students': total_students,
        'total_analytics': total_analytics,
        'risk_stats': list(risk_stats),
        'user_type': 'admin' if request.user.is_staff else 'student',
    }
    
    # Données spécifiques selon le type d'utilisateur
    if request.user.is_staff:
        # Vue administrateur/enseignant
        context.update({
            'recent_reports': AnalyticsReport.objects.all()[:5],
            'recent_predictions': PredictionModel.objects.filter(is_active=True)[:5],
        })
    else:
        # Vue étudiant
        student_analytics = StudentAnalytics.objects.filter(user=request.user).first()
        context.update({
            'student_analytics': student_analytics,
        })
    
    return render(request, 'analytics_dashboard/overview.html', context)


@login_required
def student_analytics(request, student_id):
    """Détails analytics d'un étudiant"""
    student = get_object_or_404(User, id=student_id)
    
    # Mettre à jour les analytics
    service = AnalyticsService()
    analytics = service.update_student_analytics(student)
    
    # Récupérer les prédictions
    prediction_service = PredictionService()
    prediction = prediction_service.predict_student_risk(student)
    
    context = {
        'student': student,
        'analytics': analytics,
        'prediction': prediction,
        'page_title': f'Analytics - {analytics.student_name}'
    }
    
    return render(request, 'analytics_dashboard/student_detail.html', context)


@login_required
def students_list(request):
    """Liste des étudiants avec leurs analytics"""
    students_analytics = StudentAnalytics.objects.select_related('user').all()
    
    # Pagination
    paginator = Paginator(students_analytics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Tous les Étudiants'
    }
    
    return render(request, 'analytics_dashboard/students_list.html', context)


@login_required
def classroom_analytics(request, classroom_id):
    """Analytics d'une classe"""
    classroom = get_object_or_404(ClassroomAnalytics, id=classroom_id)
    
    context = {
        'classroom': classroom,
        'page_title': f'Classe - {classroom.classroom_name}'
    }
    
    return render(request, 'analytics_dashboard/classroom_detail.html', context)


@login_required
def classrooms_list(request):
    """Liste des classes"""
    classrooms = ClassroomAnalytics.objects.all()
    
    context = {
        'classrooms': classrooms,
        'page_title': 'Toutes les Classes'
    }
    
    return render(request, 'analytics_dashboard/classrooms_list.html', context)


@login_required
def reports_list(request):
    """Liste des rapports"""
    reports = AnalyticsReport.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Rapports Analytics'
    }
    
    return render(request, 'analytics_dashboard/reports_list.html', context)


@login_required
def generate_report(request):
    """Générer un nouveau rapport"""
    if request.method == 'POST':
        try:
            service = ReportService()
            report = service.generate_student_report(request.user)
            messages.success(request, 'Rapport généré avec succès!')
            return redirect('analytics_dashboard:report_detail', report_id=report.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération: {str(e)}')
    
    context = {
        'page_title': 'Générer un Rapport'
    }
    
    return render(request, 'analytics_dashboard/generate_report.html', context)


@login_required
def report_detail(request, report_id):
    """Détails d'un rapport"""
    report = get_object_or_404(AnalyticsReport, id=report_id)
    
    context = {
        'report': report,
        'page_title': f'Rapport - {report.title}'
    }
    
    return render(request, 'analytics_dashboard/report_detail.html', context)


@login_required
def predictions_view(request):
    """Vue des prédictions IA"""
    predictions = PredictionModel.objects.filter(is_active=True).order_by('-created_at')[:20]
    
    context = {
        'predictions': predictions,
        'page_title': 'Prédictions IA'
    }
    
    return render(request, 'analytics_dashboard/predictions.html', context)


# =============================================================================
# API VIEWS POUR AJAX
# =============================================================================

@login_required
def api_student_performance(request, student_id):
    """API pour les données de performance d'un étudiant"""
    try:
        analytics = StudentAnalytics.objects.get(user_id=student_id)
        data = {
            'success_rate': analytics.success_rate,
            'average_score': analytics.average_score,
            'risk_level': analytics.risk_level,
            'engagement_score': analytics.engagement_score,
            'learning_velocity': analytics.learning_velocity,
            'consistency_score': analytics.consistency_score,
        }
        return JsonResponse(data)
    except StudentAnalytics.DoesNotExist:
        return JsonResponse({'error': 'Analytics not found'}, status=404)


@login_required
def api_class_trends(request, classroom_id):
    """API pour les tendances d'une classe"""
    try:
        classroom = ClassroomAnalytics.objects.get(id=classroom_id)
        data = {
            'trend': classroom.improvement_trend,
            'average_score': classroom.average_class_score,
            'success_rate': classroom.class_success_rate,
            'total_students': classroom.total_students,
            'active_students': classroom.active_students,
        }
        return JsonResponse(data)
    except ClassroomAnalytics.DoesNotExist:
        return JsonResponse({'error': 'Classroom not found'}, status=404)


@login_required
def api_risk_distribution(request):
    """API pour la distribution des risques"""
    risk_counts = StudentAnalytics.objects.values('risk_level').annotate(
        count=Count('risk_level')
    )
    
    data = {item['risk_level']: item['count'] for item in risk_counts}
    return JsonResponse(data)


@login_required
def api_overview_stats(request):
    """API pour les statistiques générales du dashboard"""
    total_students = StudentAnalytics.objects.count()
    
    # Moyennes générales
    averages = StudentAnalytics.objects.aggregate(
        avg_score=Avg('average_score'),
        avg_success_rate=Avg('success_rate'),
        avg_engagement=Avg('engagement_score')
    )
    
    # Répartition des risques
    risk_distribution = StudentAnalytics.objects.values('risk_level').annotate(
        count=Count('risk_level')
    )
    
    data = {
        'total_students': total_students,
        'averages': averages,
        'risk_distribution': list(risk_distribution),
        'last_updated': timezone.now().isoformat()
    }
    
    return JsonResponse(data)


@login_required
def update_predictions(request):
    """Mettre à jour les prédictions IA"""
    if request.method == 'POST':
        try:
            service = PredictionService()
            updated_count = 0
            
            # Mettre à jour pour les 10 premiers étudiants (pour éviter la surcharge)
            students = User.objects.all()[:10]
            
            for student in students:
                try:
                    service.predict_student_risk(student)
                    updated_count += 1
                except Exception as e:
                    continue
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Prédictions mises à jour pour {updated_count} étudiants'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Erreur: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)


@login_required
def refresh_analytics(request):
    """Actualiser toutes les analytics"""
    if request.method == 'POST':
        try:
            service = AnalyticsService()
            updated_count = 0
            
            # Actualiser pour tous les utilisateurs
            users = User.objects.all()
            
            for user in users:
                try:
                    service.update_student_analytics(user)
                    updated_count += 1
                except Exception as e:
                    continue
            
            return JsonResponse({
                'status': 'success',
                'message': f'Analytics actualisées pour {updated_count} utilisateurs'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)