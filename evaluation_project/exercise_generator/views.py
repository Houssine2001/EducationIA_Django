"""
Vues pour la génération automatique d'exercices par IA
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json

from .models import (
    CourseDocument,
    GeneratedExercise,
    GeneratedTest,
    ExerciseGenerationConfig
)
from .forms import (
    CourseDocumentForm,
    GenerationConfigForm,
    TestCreationForm,
    QuickGenerationForm
)
from .services import ExerciseGenerationService


# ============================================
# DASHBOARD
# ============================================

@login_required
def dashboard(request):
    """
    Tableau de bord principal pour la génération d'exercices
    """
    # Statistiques pour l'enseignant
    documents = CourseDocument.objects.filter(teacher=request.user)
    exercises = GeneratedExercise.objects.filter(source_document__teacher=request.user)
    tests = GeneratedTest.objects.filter(teacher=request.user)
    
    # Documents récents
    recent_documents = documents.order_by('-created_at')[:5]
    
    # Exercices récents
    recent_exercises = exercises.order_by('-created_at')[:10]
    
    # Statistiques
    stats = {
        'total_documents': documents.count(),
        'total_exercises': exercises.count(),
        'total_tests': tests.count(),
        'validated_exercises': exercises.filter(status='validated').count(),
        'pending_exercises': exercises.filter(status='draft').count(),
    }
    
    # Distribution par type d'exercice
    exercise_type_distribution = {
        'mcq': exercises.filter(exercise_type='mcq').count(),
        'true_false': exercises.filter(exercise_type='true_false').count(),
        'fill_blank': exercises.filter(exercise_type='fill_blank').count(),
    }
    
    context = {
        'stats': stats,
        'recent_documents': recent_documents,
        'recent_exercises': recent_exercises,
        'exercise_type_distribution': exercise_type_distribution,
    }
    
    return render(request, 'exercise_generator/dashboard.html', context)


# ============================================
# GESTION DES DOCUMENTS
# ============================================

@login_required
def document_list(request):
    """
    Liste des documents de cours
    """
    documents = CourseDocument.objects.filter(teacher=request.user).order_by('-created_at')
    
    # Filtres
    subject_filter = request.GET.get('subject', '')
    status_filter = request.GET.get('status', '')
    
    if subject_filter:
        documents = documents.filter(subject__icontains=subject_filter)
    
    if status_filter:
        documents = documents.filter(processing_status=status_filter)
    
    # Pagination
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'subject_filter': subject_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'exercise_generator/document_list.html', context)


@login_required
def document_create(request):
    """
    Créer un nouveau document de cours et lancer la génération
    """
    if request.method == 'POST':
        form = CourseDocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            document = form.save(commit=False)
            document.teacher = request.user
            document.processing_status = 'pending'
            document.save()
            
            # Lancement du traitement
            service = ExerciseGenerationService()
            result = service.process_document(document)
            
            if result['success']:
                messages.success(
                    request,
                    f"Document traité avec succès ! {len(result['exercises'])} exercices générés."
                )
                return redirect('exercise_generator:document_detail', pk=document.pk)
            else:
                messages.error(request, f"Erreur lors du traitement : {result['error']}")
                return redirect('exercise_generator:document_detail', pk=document.pk)
        
    else:
        form = CourseDocumentForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'exercise_generator/document_form.html', context)


@login_required
def document_detail(request, pk):
    """
    Détails d'un document avec les exercices générés
    """
    document = get_object_or_404(CourseDocument, pk=pk, teacher=request.user)
    exercises = document.generated_exercises.all().order_by('-quality_score', '-created_at')
    
    # Statistiques des exercices
    exercise_stats = {
        'total': exercises.count(),
        'validated': exercises.filter(status='validated').count(),
        'draft': exercises.filter(status='draft').count(),
        'rejected': exercises.filter(status='rejected').count(),
        'mcq': exercises.filter(exercise_type='mcq').count(),
        'true_false': exercises.filter(exercise_type='true_false').count(),
        'fill_blank': exercises.filter(exercise_type='fill_blank').count(),
    }
    
    # Pagination des exercices
    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'document': document,
        'exercise_stats': exercise_stats,
        'page_obj': page_obj,
    }
    
    return render(request, 'exercise_generator/document_detail.html', context)


@login_required
def document_reprocess(request, pk):
    """
    Re-traiter un document pour générer de nouveaux exercices
    """
    document = get_object_or_404(CourseDocument, pk=pk, teacher=request.user)
    
    # Lancement du retraitement
    service = ExerciseGenerationService()
    result = service.process_document(document)
    
    if result['success']:
        messages.success(
            request,
            f"Document retraité avec succès ! {len(result['exercises'])} nouveaux exercices générés."
        )
    else:
        messages.error(request, f"Erreur lors du retraitement : {result['error']}")
    
    return redirect('exercise_generator:document_detail', pk=pk)


# ============================================
# GESTION DES EXERCICES
# ============================================

@login_required
def exercise_list(request):
    """
    Liste de tous les exercices générés
    """
    # Récupérer TOUS les exercices de l'utilisateur (y compris ceux de quick generate)
    exercises = GeneratedExercise.objects.filter(
        source_document__teacher=request.user
    ).select_related('source_document').order_by('-created_at')
    
    # Filtres
    exercise_type = request.GET.get('type', '')
    difficulty = request.GET.get('difficulty', '')
    status = request.GET.get('status', '')
    concept = request.GET.get('concept', '')
    
    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)
    
    if difficulty:
        exercises = exercises.filter(difficulty=difficulty)
    
    if status:
        exercises = exercises.filter(status=status)
    
    if concept:
        exercises = exercises.filter(concept__icontains=concept)
    
    # Pagination
    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'exercises': page_obj,  # Pour compatibilité avec le template
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'exercise_type': exercise_type,
        'difficulty': difficulty,
        'status': status,
        'concept': concept,
    }
    
    return render(request, 'exercise_generator/exercise_list.html', context)


@login_required
def exercise_detail(request, pk):
    """
    Détails d'un exercice généré
    """
    exercise = get_object_or_404(
        GeneratedExercise,
        pk=pk,
        source_document__teacher=request.user
    )
    
    context = {
        'exercise': exercise,
    }
    
    return render(request, 'exercise_generator/exercise_detail.html', context)


@login_required
@require_http_methods(["POST"])
def exercise_validate(request, pk):
    """
    Valider un exercice
    """
    exercise = get_object_or_404(
        GeneratedExercise,
        pk=pk,
        source_document__teacher=request.user
    )
    
    action = request.POST.get('action', 'validate')
    notes = request.POST.get('notes', '')
    
    if action == 'validate':
        exercise.status = 'validated'
        message = "Exercice validé avec succès."
    elif action == 'publish':
        exercise.status = 'published'
        message = "Exercice publié avec succès."
    elif action == 'reject':
        exercise.status = 'rejected'
        message = "Exercice rejeté."
    else:
        messages.error(request, "Action non reconnue.")
        return redirect('exercise_generator:exercise_detail', pk=pk)
    
    exercise.validated_by = request.user
    exercise.validation_notes = notes
    exercise.save()
    
    messages.success(request, message)
    
    # Redirection
    next_url = request.POST.get('next', 'exercise_generator:exercise_detail')
    if next_url == 'exercise_generator:exercise_detail':
        return redirect('exercise_generator:exercise_detail', pk=pk)
    else:
        return redirect(next_url)


@login_required
@require_http_methods(["POST"])
def exercise_bulk_action(request):
    """
    Actions en masse sur les exercices
    """
    exercise_ids = request.POST.getlist('exercise_ids')
    action = request.POST.get('action')
    
    if not exercise_ids:
        messages.error(request, "Aucun exercice sélectionné.")
        return redirect('exercise_generator:exercise_list')
    
    exercises = GeneratedExercise.objects.filter(
        id__in=exercise_ids,
        source_document__teacher=request.user
    )
    
    if action == 'validate':
        exercises.update(status='validated', validated_by=request.user)
        messages.success(request, f"{exercises.count()} exercices validés.")
    
    elif action == 'publish':
        exercises.update(status='published', validated_by=request.user)
        messages.success(request, f"{exercises.count()} exercices publiés.")
    
    elif action == 'reject':
        exercises.update(status='rejected', validated_by=request.user)
        messages.success(request, f"{exercises.count()} exercices rejetés.")
    
    elif action == 'delete':
        count = exercises.count()
        exercises.delete()
        messages.success(request, f"{count} exercices supprimés.")
    
    else:
        messages.error(request, "Action non reconnue.")
    
    return redirect('exercise_generator:exercise_list')


# ============================================
# GESTION DES TESTS
# ============================================

@login_required
def test_create(request, document_pk):
    """
    Créer un test à partir d'exercices d'un document
    """
    document = get_object_or_404(CourseDocument, pk=document_pk, teacher=request.user)
    
    if request.method == 'POST':
        form = TestCreationForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            exercise_ids = form.cleaned_data['exercise_ids']
            
            # Création du test
            service = ExerciseGenerationService()
            test = service.create_test_from_exercises(
                document=document,
                teacher=request.user,
                exercise_ids=exercise_ids,
                title=title,
                description=description
            )
            
            messages.success(request, f"Test '{title}' créé avec succès !")
            return redirect('exercise_generator:test_detail', pk=test.pk)
    
    else:
        # Pré-sélection des exercices validés
        selected_exercises = document.generated_exercises.filter(
            status__in=['validated', 'published']
        ).order_by('-quality_score')[:10]
        
        form = TestCreationForm(initial={
            'title': f"Test - {document.title}",
            'description': document.description or "",
        })
        
        # Tous les exercices disponibles
        available_exercises = document.generated_exercises.all().order_by('-quality_score')
    
    context = {
        'form': form,
        'document': document,
        'available_exercises': available_exercises if request.method == 'GET' else [],
        'selected_exercises': selected_exercises if request.method == 'GET' else [],
    }
    
    return render(request, 'exercise_generator/test_form.html', context)


@login_required
def test_list(request):
    """
    Liste des tests générés
    """
    tests = GeneratedTest.objects.filter(teacher=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'exercise_generator/test_list.html', context)


@login_required
def test_detail(request, pk):
    """
    Détails d'un test généré
    """
    test = get_object_or_404(GeneratedTest, pk=pk, teacher=request.user)
    exercises = test.exercises.all().order_by('difficulty', 'exercise_type')
    
    context = {
        'test': test,
        'exercises': exercises,
    }
    
    return render(request, 'exercise_generator/test_detail.html', context)


@login_required
@require_http_methods(["POST"])
def test_export(request, pk):
    """
    Exporter un test vers l'application evaluation
    """
    test = get_object_or_404(GeneratedTest, pk=pk, teacher=request.user)
    
    service = ExerciseGenerationService()
    evaluation_test_id = service.export_to_evaluation_app(test)
    
    if evaluation_test_id:
        messages.success(
            request,
            f"Test exporté avec succès vers l'application d'évaluation ! (ID: {evaluation_test_id})"
        )
    else:
        messages.error(request, "Erreur lors de l'export du test.")
    
    return redirect('exercise_generator:test_detail', pk=pk)


# ============================================
# CONFIGURATION
# ============================================

@login_required
def config_view(request):
    """
    Configuration de la génération d'exercices
    """
    try:
        config = ExerciseGenerationConfig.objects.get(teacher=request.user)
    except ExerciseGenerationConfig.DoesNotExist:
        config = None
    
    if request.method == 'POST':
        form = GenerationConfigForm(request.POST, instance=config)
        
        if form.is_valid():
            config = form.save(commit=False)
            config.teacher = request.user
            config.save()
            
            messages.success(request, "Configuration enregistrée avec succès !")
            return redirect('exercise_generator:config')
    
    else:
        form = GenerationConfigForm(instance=config)
    
    context = {
        'form': form,
        'config': config,
    }
    
    return render(request, 'exercise_generator/config.html', context)


# ============================================
# GÉNÉRATION RAPIDE
# ============================================

@login_required
def quick_generate(request):
    """
    Génération rapide d'exercices à partir d'un texte
    """
    if request.method == 'POST':
        form = QuickGenerationForm(request.POST)
        
        if form.is_valid():
            text = form.cleaned_data['text']
            subject = form.cleaned_data['subject']
            num_exercises = form.cleaned_data['num_exercises']
            
            # Création d'un document temporaire
            document = CourseDocument.objects.create(
                title=f"Document rapide - {subject}",
                content=text,
                subject=subject,
                teacher=request.user,
                document_type='text',
                processing_status='pending'
            )
            
            # Configuration
            config = {
                'total_exercises': num_exercises,
                'mcq_percentage': 50,
                'true_false_percentage': 30,
                'fill_blank_percentage': 20,
                'easy_percentage': 30,
                'medium_percentage': 50,
                'hard_percentage': 20,
                'min_quality_score': 0.6
            }
            
            # Génération
            service = ExerciseGenerationService()
            result = service.process_document(document, config)
            
            if result['success']:
                messages.success(
                    request,
                    f"Génération réussie ! {len(result['exercises'])} exercices créés."
                )
                return redirect('exercise_generator:document_detail', pk=document.pk)
            else:
                messages.error(request, f"Erreur : {result['error']}")
    
    else:
        form = QuickGenerationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'exercise_generator/quick_generate.html', context)
