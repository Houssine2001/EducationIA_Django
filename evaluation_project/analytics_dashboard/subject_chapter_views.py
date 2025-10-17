"""
Vues pour le système de matières et chapitres
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import time

from .subject_models import Subject, Chapter
from .subject_chapter_service import SubjectChapterService, PredictionReportService


@login_required
def subjects_list(request):
    """Liste de toutes les matières"""
    service = SubjectChapterService()
    
    if request.user.is_staff:
        # Vue admin: toutes les matières
        subjects = service.get_all_subjects()
        context = {
            'page_title': 'Gestion des Matières',
            'subjects': subjects,
            'is_admin': True
        }
    else:
        # Vue étudiant: avec progression
        overview = service.get_subject_overview_for_student(request.user)
        context = {
            'page_title': 'Mes Matières',
            'subjects_overview': overview,
            'is_admin': False
        }
    
    return render(request, 'analytics_dashboard/subjects_list.html', context)


@login_required
def subject_chapters(request, subject_id):
    """Liste des chapitres d'une matière avec statut de l'étudiant"""
    service = SubjectChapterService()
    
    subject, chapters = service.get_subject_with_chapters(subject_id)
    if not subject:
        return redirect('analytics_dashboard:subjects_list')
    
    # Récupérer le statut de chaque chapitre
    if not request.user.is_staff:
        chapter_status_list = service.get_student_chapter_status(request.user, subject)
        progress = service.get_student_progress(request.user, subject)
        
        # Reformater pour le template: chapter_data.chapter et chapter_data.status
        chapters_with_status = []
        for item in chapter_status_list:
            chapters_with_status.append({
                'chapter': item['chapter'],
                'status': {
                    'visited': item['is_visited'],
                    'completed': item['is_completed'],
                    'visit_count': item['visit_count'],
                    'total_time_minutes': item['total_time_minutes'],
                    'progress_percentage': item['progress_percentage']
                }
            })
        
        # Générer le rapport de prédiction
        report_service = PredictionReportService()
        prediction_report = report_service.generate_detailed_report(request.user, subject)
        
        # Calculer le taux de complétion
        completion_rate = progress.calculate_completion_rate()
    else:
        chapters_with_status = []
        for ch in chapters:
            chapters_with_status.append({
                'chapter': ch,
                'status': {
                    'visited': False,
                    'completed': False,
                    'visit_count': 0,
                    'total_time_minutes': 0,
                    'progress_percentage': 0
                }
            })
        progress = None
        prediction_report = None
        completion_rate = 0
    
    context = {
        'page_title': f'{subject.name} - Chapitres',
        'subject': subject,
        'chapters_with_status': chapters_with_status,
        'progress': progress,
        'prediction_report': prediction_report,
        'total_chapters': len(chapters),
        'completion_rate': completion_rate
    }
    
    return render(request, 'analytics_dashboard/subject_chapters.html', context)


@login_required
def chapter_view(request, chapter_id):
    """Vue d'un chapitre spécifique"""
    from bson import ObjectId
    service = SubjectChapterService()
    
    # Convertir l'ID en ObjectId si c'est une string
    if isinstance(chapter_id, str):
        chapter_id = ObjectId(chapter_id)
    
    chapter = get_object_or_404(Chapter, _id=chapter_id)
    
    # Enregistrer la visite au début
    start_time = time.time()
    
    # Récupérer le statut pour cet étudiant
    if not request.user.is_staff:
        from .subject_models import ChapterVisit
        previous_visits = list(ChapterVisit.objects.filter(
            student=request.user,
            chapter=chapter
        ).order_by('-visited_at'))
        
        # Compter manuellement (bug Djongo avec filter sur boolean)
        is_completed = any(v.completed for v in previous_visits)
        
        # Calculer les statistiques
        visit_count = len(previous_visits)
        total_time = sum(v.duration_seconds for v in previous_visits) / 60  # en minutes
        avg_time = total_time / visit_count if visit_count > 0 else 0
    else:
        previous_visits = []
        is_completed = False
        visit_count = 0
        total_time = 0
        avg_time = 0
    
    context = {
        'page_title': chapter.title,
        'chapter': chapter,
        'subject': chapter.subject,
        'previous_visits': previous_visits[:5],  # 5 dernières visites
        'is_completed': is_completed,
        'start_time': start_time,
        'visit_count': visit_count,
        'total_time': total_time,
        'avg_time': avg_time
    }
    
    return render(request, 'analytics_dashboard/chapter_view.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_chapter_complete(request, chapter_id):
    """Marque un chapitre comme terminé"""
    from bson import ObjectId
    try:
        # Convertir l'ID en ObjectId si c'est une string
        if isinstance(chapter_id, str):
            chapter_id = ObjectId(chapter_id)
        
        chapter = get_object_or_404(Chapter, _id=chapter_id)
        data = json.loads(request.body)
        duration_seconds = data.get('duration_seconds', 0)
        
        service = SubjectChapterService()
        visit = service.record_chapter_visit(
            student=request.user,
            chapter=chapter,
            duration_seconds=duration_seconds,
            completed=True
        )
        
        # Récupérer la progression mise à jour
        progress = service.get_student_progress(request.user, chapter.subject)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Chapitre terminé!',
            'progress': {
                'completion_rate': progress.calculate_completion_rate(),
                'chapters_completed': progress.chapters_completed,
                'predicted_success_rate': progress.predicted_success_rate
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def record_chapter_visit_api(request, chapter_id):
    """Enregistre une visite de chapitre (appelé automatiquement)"""
    from bson import ObjectId
    try:
        # Convertir l'ID en ObjectId si c'est une string
        if isinstance(chapter_id, str):
            chapter_id = ObjectId(chapter_id)
        
        chapter = get_object_or_404(Chapter, _id=chapter_id)
        data = json.loads(request.body)
        duration_seconds = data.get('duration_seconds', 0)
        
        service = SubjectChapterService()
        visit = service.record_chapter_visit(
            student=request.user,
            chapter=chapter,
            duration_seconds=duration_seconds,
            completed=False
        )
        
        return JsonResponse({
            'status': 'success',
            'visit_id': str(visit._id)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
def subject_prediction(request, subject_id):
    """Page de prédiction détaillée pour une matière"""
    from bson import ObjectId
    service = SubjectChapterService()
    report_service = PredictionReportService()
    
    # Convertir l'ID en ObjectId si c'est une string
    if isinstance(subject_id, str):
        subject_id = ObjectId(subject_id)
    
    subject = get_object_or_404(Subject, _id=subject_id)
    
    if request.user.is_staff:
        return redirect('analytics_dashboard:subjects_list')
    
    # Générer le rapport complet
    report = report_service.generate_detailed_report(request.user, subject)
    
    context = {
        'page_title': f'Prédiction - {subject.name}',
        'report': report,
        'subject': subject
    }
    
    return render(request, 'analytics_dashboard/subject_prediction.html', context)


@login_required
def my_progress_overview(request):
    """Vue d'ensemble de la progression de l'étudiant"""
    if request.user.is_staff:
        return redirect('analytics_dashboard:subjects_list')
    
    service = SubjectChapterService()
    overview = service.get_subject_overview_for_student(request.user)
    
    # Calculer les stats globales
    total_subjects = len(overview)
    total_chapters_all = sum(o['total_chapters'] for o in overview)
    total_visited = sum(o['progress'].chapters_visited for o in overview)
    total_completed = sum(o['progress'].chapters_completed for o in overview)
    
    avg_predicted_success = sum(o['progress'].predicted_success_rate for o in overview) / max(total_subjects, 1)
    
    # Identifier les matières à risque
    at_risk_subjects = [o for o in overview if o['progress'].risk_level in ['HIGH', 'CRITICAL']]
    
    context = {
        'page_title': 'Ma Progression Globale',
        'overview': overview,
        'global_stats': {
            'total_subjects': total_subjects,
            'total_chapters': total_chapters_all,
            'chapters_visited': total_visited,
            'chapters_completed': total_completed,
            'completion_rate': (total_completed / max(total_chapters_all, 1)) * 100,
            'avg_predicted_success': avg_predicted_success
        },
        'at_risk_subjects': at_risk_subjects
    }
    
    return render(request, 'analytics_dashboard/my_progress_overview.html', context)
