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
import subprocess
import sys

# Import des modèles analytics
from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel, PerformanceTrend
from .services import AnalyticsService, PredictionService, ReportService

# Import des modèles evaluation avec gestion d'erreur
try:
    from evaluation.models import Test, TestSubmission, StudentProgress
except ImportError:
    Test = None
    TestSubmission = None
    StudentProgress = None

@login_required
def dashboard_overview(request):
    """Vue principale du dashboard analytics avec vraies données"""
    context = {
        'page_title': 'Dashboard Analytics IA',
        'user_type': 'admin' if request.user.is_staff else 'student'
    }
    
    # Actualiser les analytics de l'utilisateur actuel
    analytics_service = AnalyticsService()
    student_analytics = analytics_service.update_student_analytics(request.user)
    
    if request.user.is_staff:
        # Statistiques pour les administrateurs
        context.update({
            'total_students': User.objects.filter(is_staff=False).count(),
            'total_analytics': StudentAnalytics.objects.count(),
            'active_students': StudentAnalytics.objects.filter(
                last_activity__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'total_tests_taken': PerformanceTrend.objects.count(),
            'risk_stats': _get_risk_statistics()
        })
    else:
        # Données pour l'étudiant connecté
        if student_analytics:
            # Récupérer les prédictions IA
            prediction_service = PredictionService()
            prediction = prediction_service.generate_real_prediction(request.user)
            
            # Historique récent des performances
            recent_trends = PerformanceTrend.objects.filter(
                student=request.user
            ).order_by('-date')[:7]
            
            # Données pour le graphique
            chart_data = _prepare_chart_data(request.user)
            
            # Recommandations IA
            ai_recommendations = _get_ai_recommendations(student_analytics, prediction)
            
            context.update({
                'student_analytics': {
                    'predicted_success_probability': _get_prediction_probability(prediction),
                    'prediction_confidence': _get_prediction_confidence(prediction),
                    'risk_level': student_analytics.risk_level,
                    'success_rate': student_analytics.success_rate,
                    'average_score': student_analytics.average_score,
                    'engagement_score': getattr(student_analytics, 'engagement_score', 0.5),
                    'consistency_score': getattr(student_analytics, 'consistency_score', 0.5),
                    'learning_velocity': getattr(student_analytics, 'learning_velocity', 0),
                },
                'performance_history': [
                    {
                        'date': trend.date,
                        'score': trend.score,
                        'subject': trend.subject
                    } for trend in recent_trends
                ],
                'chart_data': chart_data,
                'ai_recommendations': ai_recommendations
            })
    
    return render(request, 'analytics_dashboard/overview.html', context)

def _get_risk_statistics():
    """Calcule les statistiques par niveau de risque"""
    risk_stats = {}
    risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    for level in risk_levels:
        count = StudentAnalytics.objects.filter(risk_level=level).count()
        if count > 0:
            risk_stats[level] = count
    
    return risk_stats

def _get_prediction_probability(prediction):
    """Récupère la probabilité de prédiction"""
    # 🔧 CORRECTION: prediction est un dict, pas un objet
    if prediction and isinstance(prediction, dict):
        return prediction.get('predicted_score', 0) / 100.0  # Convertir en probabilité 0-1
    return 0.5

def _get_prediction_confidence(prediction):
    """Récupère la confiance de la prédiction"""
    # 🔧 CORRECTION: prediction est un dict, pas un objet
    if prediction and isinstance(prediction, dict):
        return prediction.get('confidence', 0) / 100.0  # Convertir en probabilité 0-1
    return 0.5
    return 0.5

def _prepare_chart_data(user):
    """Prépare les données pour le graphique de performance"""
    trends = PerformanceTrend.objects.filter(
        student=user
    ).order_by('date')[:30]
    
    if not trends.exists():
        return None
    
    labels = []
    scores = []
    
    for trend in trends:
        labels.append(trend.date.strftime('%d/%m'))
        scores.append(trend.score)
    
    return {
        'labels': labels,
        'scores': scores
    }

def _get_ai_recommendations(analytics, prediction):
    """Génère des recommandations IA basées sur les analytics"""
    recommendations = []
    
    # 🔧 CORRECTION: prediction est un dict, pas un objet
    if not prediction or not isinstance(prediction, dict):
        return [
            {
                'title': 'Commencer à générer des données',
                'description': 'Passez des tests pour que l\'IA puisse analyser vos performances',
                'priority': 'HIGH'
            }
        ]
    
    try:
        # Les recommandations peuvent être directement dans le dict
        ai_recommendations = prediction.get('recommendations', [])
        
        for rec in ai_recommendations:
            recommendations.append({
                'title': rec,
                'priority': 'MEDIUM'
            })
        
        # Ajouter des recommandations basées sur les métriques
        if analytics.success_rate < 60:
            recommendations.append({
                'title': 'Améliorer le taux de réussite',
                'description': f'Votre taux de réussite ({analytics.success_rate:.1f}%) peut être amélioré',
                'priority': 'HIGH'
            })
        
        if getattr(analytics, 'engagement_score', 0) < 0.5:
            recommendations.append({
                'title': 'Augmenter l\'engagement',
                'description': 'Essayez de faire plus d\'exercices régulièrement',
                'priority': 'MEDIUM'
            })
        
    except Exception as e:
        recommendations.append({
            'title': 'Continuer les exercices',
            'description': 'Continuez à pratiquer pour améliorer vos performances',
            'priority': 'LOW'
        })
    
    return recommendations

@login_required 
def refresh_analytics(request):
    """Actualiser toutes les analytics"""
    if request.method == 'POST':
        try:
            updated_count = 0
            analytics_service = AnalyticsService()
            
            # Actualiser pour tous les utilisateurs non-staff
            users = User.objects.filter(is_staff=False)
            
            for user in users:
                try:
                    analytics_service.update_student_analytics(user)
                    updated_count += 1
                except Exception as e:
                    print(f"Erreur pour {user.username}: {e}")
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

@login_required
def generate_test_data_view(request):
    """Générer des données de test via l'interface"""
    if request.method == 'POST':
        try:
            # Exécuter la commande de génération de données
            result = subprocess.run([
                sys.executable, 'manage.py', 'generate_test_data', '--students', '5'
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Données de test générées avec succès!'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erreur lors de la génération: {result.stderr}'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
def update_predictions(request):
    """Mettre à jour les prédictions IA"""
    if request.method == 'POST':
        try:
            updated_count = 0
            prediction_service = PredictionService()
            
            # Mettre à jour pour tous les étudiants ayant des données
            students = User.objects.filter(is_staff=False)
            
            for student in students:
                try:
                    prediction = prediction_service.generate_real_prediction(student)
                    if prediction:
                        updated_count += 1
                except Exception as e:
                    print(f"Erreur pour {student.username}: {e}")
                    continue
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Prédictions IA mises à jour pour {updated_count} étudiants'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Erreur: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
def student_analytics(request):
    """Analytics détaillées pour un étudiant"""
    analytics_service = AnalyticsService()
    analytics = analytics_service.update_student_analytics(request.user)
    
    context = {
        'analytics': analytics,
        'page_title': 'Mes Analytics Détaillées'
    }
    
    return render(request, 'analytics_dashboard/student_analytics.html', context)

@login_required
def analytics_reports(request):
    """Liste des rapports analytics"""
    reports = AnalyticsReport.objects.filter(
        generated_by=request.user
    ).order_by('-generated_at')[:10]
    
    context = {
        'reports': reports,
        'page_title': 'Mes Rapports Analytics'
    }
    
    return render(request, 'analytics_dashboard/reports.html', context)

@login_required
def generate_report(request):
    """Générer un nouveau rapport"""
    if request.method == 'POST':
        report_service = ReportService()
        report = report_service.generate_student_report(request.user)
        
        messages.success(request, 'Rapport généré avec succès!')
        return redirect('analytics_dashboard:reports')
    
    return redirect('analytics_dashboard:reports')

# Vue pour l'évolution des étudiants
@login_required
def student_evolution_dashboard(request):
    """Dashboard d'évolution des performances étudiantes"""
    context = {
        'page_title': 'Évolution des Étudiants',
    }
    
    if request.user.is_staff:
        # Vue admin : tous les étudiants
        students_data = []
        students = User.objects.filter(is_staff=False)
        
        for student in students:
            analytics = StudentAnalytics.objects.filter(user=student).first()
            recent_trends = PerformanceTrend.objects.filter(
                student=student
            ).order_by('-date')[:5]
            
            if analytics:
                students_data.append({
                    'student': student,
                    'analytics': analytics,
                    'recent_performance': [
                        {'date': t.date, 'score': t.score} for t in recent_trends
                    ]
                })
        
        context['students_data'] = students_data
    else:
        # Vue étudiant : ses propres données
        analytics = StudentAnalytics.objects.filter(user=request.user).first()
        trends = PerformanceTrend.objects.filter(
            student=request.user
        ).order_by('date')
        
        context.update({
            'student_analytics': analytics,
            'performance_trends': trends,
            'chart_data': _prepare_chart_data(request.user)
        })
    
    return render(request, 'analytics_dashboard/student_evolution_dashboard.html', context)

@login_required
def students_list(request):
    """Liste tous les étudiants avec leurs analytics"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    if not request.user.is_staff:
        return redirect('analytics_dashboard:overview')
    
    students = User.objects.filter(is_staff=False).order_by('username')
    students_data = []
    
    for student in students:
        analytics = StudentAnalytics.objects.filter(user=student).first()
        recent_activity = PerformanceTrend.objects.filter(
            student=student
        ).order_by('-date').first()
        
        students_data.append({
            'student': student,
            'analytics': analytics,
            'last_activity': recent_activity.date if recent_activity else None,
            'total_tests': PerformanceTrend.objects.filter(student=student).count()
        })
    
    # Pagination
    paginator = Paginator(students_data, 20)
    page = request.GET.get('page', 1)
    students_page = paginator.get_page(page)
    
    context = {
        'students': students_page,
        'page_title': 'Liste des Étudiants',
        'total_students': len(students_data)
    }
    
    return render(request, 'analytics_dashboard/students_list.html', context)

@login_required
def classrooms_list(request):
    """Liste des classes avec analytics"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    if not request.user.is_staff:
        return redirect('analytics_dashboard:overview')
    
    # Grouper les étudiants par classe simulée (basé sur la première lettre du nom)
    classrooms_data = {}
    students = User.objects.filter(is_staff=False)
    
    for student in students:
        class_name = f"Classe {student.username[0].upper()}" if student.username else "Classe A"
        
        if class_name not in classrooms_data:
            classrooms_data[class_name] = {
                'name': class_name,
                'students': [],
                'total_students': 0,
                'average_score': 0,
                'active_count': 0
            }
        
        analytics = StudentAnalytics.objects.filter(user=student).first()
        if analytics:
            classrooms_data[class_name]['students'].append({
                'student': student,
                'analytics': analytics
            })
            classrooms_data[class_name]['total_students'] += 1
            
            # Calculer les moyennes
            if analytics.average_score:
                classrooms_data[class_name]['average_score'] += analytics.average_score
            
            # Vérifier l'activité récente
            if analytics.last_activity and analytics.last_activity >= timezone.now() - timedelta(days=7):
                classrooms_data[class_name]['active_count'] += 1
    
    # Finaliser les calculs de moyenne
    for class_data in classrooms_data.values():
        if class_data['total_students'] > 0:
            class_data['average_score'] = class_data['average_score'] / class_data['total_students']
    
    context = {
        'classrooms': list(classrooms_data.values()),
        'page_title': 'Gestion des Classes',
        'total_classrooms': len(classrooms_data)
    }
    
    return render(request, 'analytics_dashboard/classrooms_list.html', context)

@login_required
def classroom_analytics(request, classroom_id):
    """Analytics détaillées d'une classe"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    if not request.user.is_staff:
        return redirect('analytics_dashboard:overview')
    
    # Simuler une classe basée sur l'ID
    class_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    if classroom_id <= len(class_letters):
        class_letter = class_letters[classroom_id - 1]
        class_name = f"Classe {class_letter}"
    else:
        class_name = "Classe Inconnue"
    
    # Récupérer les étudiants de cette "classe"
    students = User.objects.filter(
        is_staff=False,
        username__istartswith=class_letter.lower()
    ) if classroom_id <= len(class_letters) else User.objects.none()
    
    students_analytics = []
    total_score = 0
    active_students = 0
    
    for student in students:
        analytics = StudentAnalytics.objects.filter(user=student).first()
        if analytics:
            students_analytics.append({
                'student': student,
                'analytics': analytics,
                'recent_trends': PerformanceTrend.objects.filter(
                    student=student
                ).order_by('-date')[:5]
            })
            total_score += analytics.average_score or 0
            if analytics.last_activity and analytics.last_activity >= timezone.now() - timedelta(days=7):
                active_students += 1
    
    average_score = total_score / len(students_analytics) if students_analytics else 0
    
    context = {
        'classroom_name': class_name,
        'classroom_id': classroom_id,
        'students_analytics': students_analytics,
        'total_students': len(students_analytics),
        'average_score': average_score,
        'active_students': active_students,
        'page_title': f'Analytics - {class_name}'
    }
    
    return render(request, 'analytics_dashboard/classroom_analytics.html', context)

@login_required
def reports_list(request):
    """Liste des rapports analytics"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    reports = AnalyticsReport.objects.all().order_by('-generated_at')
    
    if not request.user.is_staff:
        reports = reports.filter(generated_by=request.user)
    
    paginator = Paginator(reports, 15)
    page = request.GET.get('page', 1)
    reports_page = paginator.get_page(page)
    
    context = {
        'reports': reports_page,
        'page_title': 'Rapports Analytics',
        'can_generate': True
    }
    
    return render(request, 'analytics_dashboard/reports_list.html', context)

@login_required
def report_detail(request, report_id):
    """Détail d'un rapport analytics"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    report = get_object_or_404(AnalyticsReport, pk=report_id)
    
    # Vérifier les permissions
    if not request.user.is_staff and report.generated_by != request.user:
        return redirect('analytics_dashboard:reports_list')
    
    # Parser les données du rapport si elles existent
    report_data = {}
    if report.report_data:
        try:
            report_data = json.loads(report.report_data)
        except:
            report_data = {'error': 'Données non valides'}
    
    context = {
        'report': report,
        'report_data': report_data,
        'page_title': f'Rapport - {report.report_type}'
    }
    
    return render(request, 'analytics_dashboard/report_detail.html', context)

@login_required
def predictions_view(request):
    """Vue des prédictions IA"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    context = {
        'page_title': 'Prédictions IA',
    }
    
    if request.user.is_staff:
        # Vue admin : prédictions pour tous
        predictions = PredictionModel.objects.all().order_by('-created_at')[:20]
        
        # Statistiques globales des prédictions
        total_predictions = PredictionModel.objects.count()
        recent_predictions = PredictionModel.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        context.update({
            'predictions': predictions,
            'total_predictions': total_predictions,
            'recent_predictions': recent_predictions,
            'is_admin': True
        })
    else:
        # Vue étudiant : ses prédictions
        predictions = PredictionModel.objects.filter(
            student=request.user
        ).order_by('-created_at')[:10]
        
        latest_prediction = predictions.first() if predictions.exists() else None
        prediction_data = {}
        
        if latest_prediction and latest_prediction.raw_data:
            try:
                prediction_data = latest_prediction.raw_data if isinstance(latest_prediction.raw_data, dict) else json.loads(latest_prediction.raw_data)
            except:
                prediction_data = {}
        
        context.update({
            'predictions': predictions,
            'latest_prediction': latest_prediction,
            'prediction_data': prediction_data,
            'is_admin': False
        })
    
    return render(request, 'analytics_dashboard/predictions.html', context)

# API Endpoints pour le tracking en temps réel
@login_required
def api_student_performance(request, student_id):
    """API pour récupérer les performances d'un étudiant"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    try:
        student = get_object_or_404(User, pk=student_id)
        
        # Vérifier les permissions
        if not request.user.is_staff and request.user != student:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        analytics = StudentAnalytics.objects.filter(user=student).first()
        trends = PerformanceTrend.objects.filter(
            student=student
        ).order_by('date')[:30]
        
        data = {
            'student_id': student.id,
            'student_name': f"{student.first_name} {student.last_name}".strip() or student.username,
            'analytics': {
                'success_rate': analytics.success_rate if analytics else 0,
                'average_score': analytics.average_score if analytics else 0,
                'risk_level': analytics.risk_level if analytics else 'LOW',
                'total_tests': analytics.total_tests_taken if analytics else 0,
                'last_activity': analytics.last_activity.isoformat() if analytics and analytics.last_activity else None
            },
            'performance_trends': [
                {
                    'date': trend.date.isoformat(),
                    'score': trend.score,
                    'subject': trend.subject
                } for trend in trends
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_class_trends(request, classroom_id):
    """API pour les tendances d'une classe"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        # Simuler les données de classe
        class_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        if classroom_id <= len(class_letters):
            class_letter = class_letters[classroom_id - 1]
            students = User.objects.filter(
                is_staff=False,
                username__istartswith=class_letter.lower()
            )
        else:
            students = User.objects.none()
        
        trends_data = []
        for student in students:
            recent_trends = PerformanceTrend.objects.filter(
                student=student
            ).order_by('-date')[:5]
            
            if recent_trends.exists():
                trends_data.extend([
                    {
                        'student_id': student.id,
                        'student_name': student.username,
                        'date': trend.date.isoformat(),
                        'score': trend.score,
                        'subject': trend.subject
                    } for trend in recent_trends
                ])
        
        return JsonResponse({
            'classroom_id': classroom_id,
            'trends': trends_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_risk_distribution(request):
    """API pour la distribution des risques"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        risk_data = _get_risk_statistics()
        return JsonResponse({
            'risk_distribution': risk_data,
            'total_students': sum(risk_data.values())
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_overview_stats(request):
    """API pour les statistiques générales"""
    # c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\views.py
    try:
        if request.user.is_staff:
            # Stats admin
            data = {
                'total_students': User.objects.filter(is_staff=False).count(),
                'active_students': StudentAnalytics.objects.filter(
                    last_activity__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'total_tests': PerformanceTrend.objects.count(),
                'total_predictions': PredictionModel.objects.count(),
                'average_success_rate': StudentAnalytics.objects.aggregate(
                    avg_success=Avg('success_rate')
                )['avg_success'] or 0
            }
        else:
            # Stats étudiant
            analytics = StudentAnalytics.objects.filter(user=request.user).first()
            data = {
                'my_tests': PerformanceTrend.objects.filter(student=request.user).count(),
                'my_success_rate': analytics.success_rate if analytics else 0,
                'my_average_score': analytics.average_score if analytics else 0,
                'my_risk_level': analytics.risk_level if analytics else 'LOW',
                'predictions_count': PredictionModel.objects.filter(student=request.user).count()
            }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)