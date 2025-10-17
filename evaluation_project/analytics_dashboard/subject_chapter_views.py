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
        chapter_status = service.get_student_chapter_status(request.user, subject)
        progress = service.get_student_progress(request.user, subject)
        
        # Générer le rapport de prédiction
        report_service = PredictionReportService()
        prediction_report = report_service.generate_detailed_report(request.user, subject)
    else:
        chapter_status = [{'chapter': ch, 'is_visited': False, 'is_completed': False} for ch in chapters]
        progress = None
        prediction_report = None
    
    context = {
        'page_title': f'{subject.name} - Chapitres',
        'subject': subject,
        'chapter_status': chapter_status,
        'progress': progress,
        'prediction_report': prediction_report,
        'total_chapters': len(chapters)
    }
    
    return render(request, 'analytics_dashboard/subject_chapters.html', context)


@login_required
def chapter_view(request, chapter_id):
    """Vue d'un chapitre spécifique"""
    service = SubjectChapterService()
    
    chapter = get_object_or_404(Chapter, _id=chapter_id)
    
    # Enregistrer la visite au début
    start_time = time.time()
    
    # Récupérer le statut pour cet étudiant
    if not request.user.is_staff:
        from .subject_models import ChapterVisit
        previous_visits = ChapterVisit.objects.filter(
            student=request.user,
            chapter=chapter
        ).order_by('-visited_at')
        
        is_completed = previous_visits.filter(completed=True).exists()
    else:
        previous_visits = []
        is_completed = False
    
    context = {
        'page_title': chapter.title,
        'chapter': chapter,
        'subject': chapter.subject,
        'previous_visits': previous_visits[:5],  # 5 dernières visites
        'is_completed': is_completed,
        'start_time': start_time
    }
    
    return render(request, 'analytics_dashboard/chapter_view.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_chapter_complete(request, chapter_id):
    """Marque un chapitre comme terminé"""
    try:
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
    try:
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
    service = SubjectChapterService()
    report_service = PredictionReportService()
    
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
