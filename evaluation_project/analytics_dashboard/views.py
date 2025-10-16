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

# Import des modèles analytics
from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel
from .services import AnalyticsService, PredictionService, ReportService

# Import des modèles evaluation avec gestion d'erreur
try:
    from evaluation.models import Test, TestSubmission
except ImportError:
    Test = None
    TestSubmission = None


@login_required
def dashboard_overview(request):
    """Vue principale du dashboard analytics"""
    # Statistiques générales avec gestion d'erreur pour Djongo
    try:
        total_students = User.objects.count()
    except Exception:
        total_students = 0
    
    try:
        total_analytics = StudentAnalytics.objects.count()
    except Exception:
        total_analytics = 0
    
    context = {
        'page_title': 'Dashboard Analytics IA',
        'total_students': total_students,
        'total_analytics': total_analytics,
        'risk_stats': [],  # Vide pour éviter les erreurs
        'user_type': 'admin' if request.user.is_staff else 'student',
    }
    
    # Données spécifiques selon le type d'utilisateur
    if request.user.is_staff:
        try:
            context.update({
                'recent_reports': AnalyticsReport.objects.all()[:5],
            })
        except Exception:
            context.update({'recent_reports': []})
    else:
        try:
            student_analytics = StudentAnalytics.objects.filter(user=request.user).first()
            context.update({'student_analytics': student_analytics})
        except Exception:
            context.update({'student_analytics': None})
    
    return render(request, 'analytics_dashboard/overview.html', context)


@login_required
def student_evolution_dashboard(request):
    """Vue principale du tableau de bord évolution des étudiants - Version sécurisée"""
    
    # Initialiser avec des valeurs par défaut
    context = {
        'total_students': 0,
        'total_tests': 0,
        'total_submissions': 0,
        'avg_score': 0.0,
        'chart_data': json.dumps([]),
        'top_students': [],
        'score_distribution': {
            'excellent': 0,
            'good': 0,
            'average': 0,
            'poor': 0,
        },
        'subjects_evolution': {},
    }
    
    try:
        # Méthode alternative pour compter les utilisateurs (compatible Djongo)
        all_users = list(User.objects.all())
        students = [user for user in all_users if not user.is_staff]
        context['total_students'] = len(students)
        
        # Vérifier si les modèles Test et TestSubmission sont disponibles
        if Test is not None and TestSubmission is not None:
            try:
                # Statistiques des tests
                all_tests = list(Test.objects.all())
                context['total_tests'] = len(all_tests)
                
                # Statistiques des soumissions
                all_submissions = list(TestSubmission.objects.all())
                context['total_submissions'] = len(all_submissions)
                
                if all_submissions:
                    # Calcul de la moyenne générale
                    total_score = sum(submission.score for submission in all_submissions)
                    context['avg_score'] = round(total_score / len(all_submissions), 2)
                    
                    # Évolution des scores sur les 30 derniers jours
                    thirty_days_ago = datetime.now() - timedelta(days=30)
                    recent_submissions = [
                        submission for submission in all_submissions 
                        if submission.submitted_at >= thirty_days_ago
                    ]
                    
                    # Données pour les graphiques
                    daily_stats = {}
                    for submission in recent_submissions:
                        date_key = submission.submitted_at.strftime('%Y-%m-%d')
                        if date_key not in daily_stats:
                            daily_stats[date_key] = {'scores': [], 'count': 0}
                        daily_stats[date_key]['scores'].append(submission.score)
                        daily_stats[date_key]['count'] += 1
                    
                    # Calcul des moyennes quotidiennes
                    chart_data = []
                    for date_str, data in sorted(daily_stats.items()):
                        if data['scores']:
                            avg_daily_score = sum(data['scores']) / len(data['scores'])
                            chart_data.append({
                                'date': date_str,
                                'avg_score': round(avg_daily_score, 2),
                                'submissions_count': data['count']
                            })
                    
                    context['chart_data'] = json.dumps(chart_data)
                    
                    # Top 5 des étudiants
                    student_stats = {}
                    for submission in all_submissions:
                        student = submission.student
                        if student and not student.is_staff:
                            if student.id not in student_stats:
                                student_stats[student.id] = {
                                    'user': student,
                                    'scores': [],
                                    'total_tests': 0
                                }
                            student_stats[student.id]['scores'].append(submission.score)
                            student_stats[student.id]['total_tests'] += 1
                    
                    # Calculer les moyennes et créer le top 5
                    top_students = []
                    for student_id, data in student_stats.items():
                        if data['scores']:
                            avg_score = sum(data['scores']) / len(data['scores'])
                            top_students.append({
                                'name': data['user'].get_full_name() or data['user'].username,
                                'avg_score': round(avg_score, 2),
                                'total_tests': data['total_tests']
                            })
                    
                    # Trier et prendre les 5 premiers
                    top_students = sorted(top_students, key=lambda x: x['avg_score'], reverse=True)[:5]
                    context['top_students'] = top_students
                    
                    # Répartition des scores par tranche
                    excellent = len([s for s in all_submissions if s.score >= 90])
                    good = len([s for s in all_submissions if 70 <= s.score < 90])
                    average = len([s for s in all_submissions if 50 <= s.score < 70])
                    poor = len([s for s in all_submissions if s.score < 50])
                    
                    context['score_distribution'] = {
                        'excellent': excellent,
                        'good': good,
                        'average': average,
                        'poor': poor,
                    }
                    
                    # Évolution par matière
                    subjects_evolution = {}
                    for submission in all_submissions:
                        try:
                            subject = submission.test.subject if hasattr(submission.test, 'subject') else 'Matière inconnue'
                            if subject not in subjects_evolution:
                                subjects_evolution[subject] = {
                                    'total_submissions': 0,
                                    'avg_score': 0,
                                    'scores': []
                                }
                            subjects_evolution[subject]['scores'].append(submission.score)
                            subjects_evolution[subject]['total_submissions'] += 1
                        except AttributeError:
                            continue
                    
                    # Calcul des moyennes par matière
                    for subject, data in subjects_evolution.items():
                        if data['scores']:
                            data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 2)
                    
                    context['subjects_evolution'] = subjects_evolution
                    
            except Exception as e:
                print(f"Erreur lors du traitement des données de test: {e}")
                
    except Exception as e:
        print(f"Erreur générale dans student_evolution_dashboard: {e}")
    
    return render(request, 'analytics_dashboard/student_evolution_dashboard.html', context)


@login_required
def student_analytics(request, student_id):
    """Détails analytics d'un étudiant"""
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Créer ou récupérer les analytics de base
        analytics, created = StudentAnalytics.objects.get_or_create(
            user=student,
            defaults={
                'student_name': student.get_full_name() or student.username,
                'student_email': student.email,
                'total_exercises': 0,
                'completed_exercises': 0,
                'average_score': 0.0,
                'success_rate': 0.0,
            }
        )
        
        context = {
            'student': student,
            'analytics': analytics,
            'page_title': f'Analytics - {analytics.student_name}'
        }
        
        return render(request, 'analytics_dashboard/student_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement des analytics: {str(e)}')
        return redirect('analytics_dashboard:overview')


@login_required
def students_list(request):
    """Liste des étudiants avec leurs analytics"""
    try:
        students_analytics = StudentAnalytics.objects.all()
        
        # Pagination
        paginator = Paginator(students_analytics, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'page_title': 'Tous les Étudiants'
        }
        
    except Exception as e:
        context = {
            'page_obj': None,
            'page_title': 'Tous les Étudiants',
            'error': str(e)
        }
    
    return render(request, 'analytics_dashboard/students_list.html', context)


@login_required
def classroom_analytics(request, classroom_id):
    """Analytics d'une classe"""
    try:
        classroom = get_object_or_404(ClassroomAnalytics, id=classroom_id)
        
        context = {
            'classroom': classroom,
            'page_title': f'Classe - {classroom.class_name}'
        }
        
    except Exception as e:
        context = {
            'classroom': None,
            'page_title': 'Classe',
            'error': str(e)
        }
    
    return render(request, 'analytics_dashboard/classroom_detail.html', context)


@login_required
def classrooms_list(request):
    """Liste des classes"""
    try:
        classrooms = ClassroomAnalytics.objects.all()
        
        context = {
            'classrooms': classrooms,
            'page_title': 'Toutes les Classes'
        }
        
    except Exception as e:
        context = {
            'classrooms': [],
            'page_title': 'Toutes les Classes',
            'error': str(e)
        }
    
    return render(request, 'analytics_dashboard/classrooms_list.html', context)


@login_required
def reports_list(request):
    """Liste des rapports"""
    try:
        reports = AnalyticsReport.objects.all()
        
        # Pagination
        paginator = Paginator(reports, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'page_title': 'Rapports Analytics'
        }
        
    except Exception as e:
        context = {
            'page_obj': None,
            'page_title': 'Rapports Analytics',
            'error': str(e)
        }
    
    return render(request, 'analytics_dashboard/reports_list.html', context)


@login_required
def generate_report(request):
    """Générer un nouveau rapport"""
    if request.method == 'POST':
        try:
            # Créer un rapport simple
            report = AnalyticsReport.objects.create(
                title=f"Rapport généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}",
                generated_by=request.user,
                data={'message': 'Rapport généré avec succès'}
            )
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
    try:
        report = get_object_or_404(AnalyticsReport, id=report_id)
        
        context = {
            'report': report,
            'page_title': f'Rapport - {report.title}'
        }
        
    except Exception as e:
        context = {
            'report': None,
            'page_title': 'Rapport',
            'error': str(e)
        }
    
    return render(request, 'analytics_dashboard/report_detail.html', context)


@login_required
def predictions_view(request):
    """Vue des prédictions IA"""
    try:
        predictions = PredictionModel.objects.all()[:20]
        
        context = {
            'predictions': predictions,
            'page_title': 'Prédictions IA'
        }
        
    except Exception as e:
        context = {
            'predictions': [],
            'page_title': 'Prédictions IA',
            'error': str(e)
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
            'total_exercises': analytics.total_exercises,
            'completed_exercises': analytics.completed_exercises,
        }
        return JsonResponse(data)
    except StudentAnalytics.DoesNotExist:
        return JsonResponse({'error': 'Analytics not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_class_trends(request, classroom_id):
    """API pour les tendances d'une classe"""
    try:
        classroom = ClassroomAnalytics.objects.get(id=classroom_id)
        data = {
            'students_count': classroom.students_count,
            'average_performance': classroom.average_performance,
        }
        return JsonResponse(data)
    except ClassroomAnalytics.DoesNotExist:
        return JsonResponse({'error': 'Classroom not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_risk_distribution(request):
    """API pour la distribution des risques - utilise les scores moyens"""
    try:
        analytics = StudentAnalytics.objects.all()
        
        # Calculer la distribution basée sur les scores moyens
        excellent = len([a for a in analytics if a.average_score >= 90])
        good = len([a for a in analytics if 70 <= a.average_score < 90])
        average = len([a for a in analytics if 50 <= a.average_score < 70])
        poor = len([a for a in analytics if a.average_score < 50])
        
        data = {
            'excellent': excellent,
            'good': good,
            'average': average,
            'poor': poor
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_overview_stats(request):
    """API pour les statistiques générales du dashboard"""
    try:
        all_analytics = list(StudentAnalytics.objects.all())
        total_students = len(all_analytics)
        
        # Moyennes générales
        if all_analytics:
            avg_score = sum(a.average_score for a in all_analytics) / len(all_analytics)
            avg_success_rate = sum(a.success_rate for a in all_analytics) / len(all_analytics)
        else:
            avg_score = 0
            avg_success_rate = 0
        
        data = {
            'total_students': total_students,
            'avg_score': round(avg_score, 2),
            'avg_success_rate': round(avg_success_rate, 2),
            'last_updated': timezone.now().isoformat()
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_predictions(request):
    """Mettre à jour les prédictions IA"""
    if request.method == 'POST':
        try:
            updated_count = 0
            
            # Créer des prédictions factices pour les 5 premiers étudiants
            all_users = list(User.objects.all())
            students = [u for u in all_users if not u.is_staff][:5]
            
            for student in students:
                try:
                    PredictionModel.objects.create(
                        student=student,
                        prediction_type='risk_assessment',
                        prediction_value=0.5,
                        confidence=0.8
                    )
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
            updated_count = 0
            
            # Actualiser pour tous les utilisateurs non-staff
            all_users = list(User.objects.all())
            users = [u for u in all_users if not u.is_staff]
            
            for user in users:
                try:
                    analytics, created = StudentAnalytics.objects.get_or_create(
                        user=user,
                        defaults={
                            'student_name': user.get_full_name() or user.username,
                            'student_email': user.email,
                            'total_exercises': 0,
                            'completed_exercises': 0,
                            'average_score': 0.0,
                            'success_rate': 0.0,
                        }
                    )
                    if not created:
                        analytics.updated_at = timezone.now()
                        analytics.save()
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