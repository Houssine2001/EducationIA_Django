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
        'exercises': exercises,  # Ajouté pour la condition du bouton
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


# ============================================
# EXERCISE SETS - COLLECTE ET PUBLICATION
# ============================================

@login_required
def exercise_sets_list(request):
    """
    Liste des ensembles d'exercices créés par le prof
    """
    from .models import ExerciseSet
    
    sets = ExerciseSet.objects.filter(teacher=request.user).prefetch_related('exercises', 'source_document')
    
    context = {
        'exercise_sets': sets,
    }
    return render(request, 'exercise_generator/exercise_sets_list.html', context)


@login_required
def create_exercise_set(request, document_id):
    """
    Créer un nouveau set d'exercices à partir d'exercices générés
    """
    from .models import ExerciseSet
    
    document = get_object_or_404(CourseDocument, pk=document_id, teacher=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        exercise_ids = request.POST.getlist('exercises')  # Liste des IDs d'exercices cochés
        
        if not title:
            messages.error(request, "Le titre est obligatoire")
            return redirect('exercise_generator:document_detail', pk=document_id)
        
        if not exercise_ids or len(exercise_ids) == 0:
            messages.error(request, "Veuillez sélectionner au moins 1 exercice")
            return redirect('exercise_generator:document_detail', pk=document_id)
        
        if len(exercise_ids) > 6:
            messages.error(request, "Maximum 6 exercices par set")
            return redirect('exercise_generator:document_detail', pk=document_id)
        
        # Créer le set
        exercise_set = ExerciseSet.objects.create(
            title=title,
            description=description,
            teacher=request.user,
            source_document=document,
            status='draft'
        )
        
        # Ajouter les exercices sélectionnés
        exercises = GeneratedExercise.objects.filter(
            id__in=exercise_ids,
            source_document=document
        )
        exercise_set.exercises.set(exercises)
        
        messages.success(
            request,
            f"Set '{title}' créé avec {exercises.count()} exercices ! Vous pouvez maintenant le publier."
        )
        return redirect('exercise_generator:exercise_set_detail', set_id=exercise_set.id)
    
    # GET : afficher le formulaire
    exercises = GeneratedExercise.objects.filter(source_document=document)
    
    context = {
        'document': document,
        'exercises': exercises,
    }
    return render(request, 'exercise_generator/create_exercise_set.html', context)


@login_required
def exercise_set_detail(request, set_id):
    """
    Détails d'un set d'exercices
    """
    from .models import ExerciseSet
    
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, teacher=request.user)
    exercises = exercise_set.exercises.all()
    
    context = {
        'exercise_set': exercise_set,
        'exercises': exercises,
    }
    return render(request, 'exercise_generator/exercise_set_detail.html', context)


@login_required
def publish_exercise_set(request, set_id):
    """
    Publier un set pour les étudiants
    """
    from .models import ExerciseSet
    
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, teacher=request.user)
    
    if exercise_set.exercises.count() == 0:
        messages.error(request, "Impossible de publier un set vide")
        return redirect('exercise_generator:exercise_set_detail', set_id=set_id)
    
    exercise_set.publish()
    messages.success(request, f"Set '{exercise_set.title}' publié ! Les étudiants peuvent maintenant y accéder.")
    
    return redirect('exercise_generator:exercise_set_detail', set_id=set_id)


@login_required
def unpublish_exercise_set(request, set_id):
    """
    Retirer un set de la publication
    """
    from .models import ExerciseSet
    
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, teacher=request.user)
    exercise_set.unpublish()
    
    messages.success(request, f"Set '{exercise_set.title}' retiré de la publication")
    return redirect('exercise_generator:exercise_set_detail', set_id=set_id)


@login_required
def delete_exercise_set(request, set_id):
    """
    Supprimer un set d'exercices
    """
    from .models import ExerciseSet
    
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, teacher=request.user)
    title = exercise_set.title
    exercise_set.delete()
    
    messages.success(request, f"Set '{title}' supprimé")
    return redirect('exercise_generator:exercise_sets_list')


# ============================================
# VUES ÉTUDIANTS - ACCÈS AUX SETS PUBLIÉS
# ============================================

@login_required
def student_exercise_sets(request):
    """
    Dashboard étudiant : liste des sets publiés disponibles
    """
    from .models import ExerciseSet, StudentExerciseSubmission
    from evaluation.models import UserProfile
    
    # Vérifier que c'est un étudiant
    try:
        profile = request.user.profile
        if profile.role != 'student':
            messages.error(request, "Accès réservé aux étudiants")
            return redirect('evaluation:teacher_dashboard')
    except:
        messages.error(request, "Profil utilisateur non trouvé")
        return redirect('evaluation:student_dashboard')
    
    # Sets publiés
    published_sets = ExerciseSet.objects.filter(status='published').prefetch_related('exercises', 'teacher')
    
    # Vérifier les soumissions existantes
    submissions = StudentExerciseSubmission.objects.filter(student=request.user)
    completed_set_ids = set(submissions.values_list('exercise_set_id', flat=True))
    
    context = {
        'exercise_sets': published_sets,
        'completed_set_ids': completed_set_ids,
    }
    return render(request, 'exercise_generator/student_exercise_sets.html', context)


@login_required
def student_take_exercise_set(request, set_id):
    """
    Étudiant prend un set d'exercices (SANS voir les corrections)
    """
    from .models import ExerciseSet, StudentExerciseSubmission
    from evaluation.models import UserProfile
    
    # Vérifier que c'est un étudiant
    try:
        profile = request.user.profile
        if profile.role != 'student':
            messages.error(request, "Accès réservé aux étudiants")
            return redirect('evaluation:teacher_dashboard')
    except:
        messages.error(request, "Profil utilisateur non trouvé")
        return redirect('evaluation:student_dashboard')
    
    # Récupérer le set
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, status='published')
    exercises = exercise_set.exercises.all()
    
    # Vérifier si déjà soumis
    try:
        submission = StudentExerciseSubmission.objects.get(
            student=request.user,
            exercise_set=exercise_set
        )
        if submission.is_completed:
            messages.info(request, "Vous avez déjà complété ce set")
            return redirect('exercise_generator:student_exercise_result', set_id=set_id)
    except StudentExerciseSubmission.DoesNotExist:
        # Créer une nouvelle soumission
        submission = StudentExerciseSubmission.objects.create(
            student=request.user,
            exercise_set=exercise_set,
            total_count=exercises.count()
        )
    
    if request.method == 'POST':
        # Traiter les réponses
        answers = {}
        correct_count = 0
        
        for exercise in exercises:
            answer_key = f'exercise_{exercise.id}'
            student_answer = request.POST.get(answer_key)
            
            if student_answer:
                answers[str(exercise.id)] = student_answer
                
                # Vérifier la réponse
                options_data = exercise.options_data
                
                if exercise.exercise_type == 'mcq':
                    correct_answer = options_data.get('correct')
                    if student_answer == correct_answer:
                        correct_count += 1
                
                elif exercise.exercise_type == 'true_false':
                    correct_answer = str(options_data.get('correct')).lower()
                    if student_answer.lower() == correct_answer:
                        correct_count += 1
                
                elif exercise.exercise_type == 'fill_blank':
                    correct_answer = options_data.get('correct', '').lower().strip()
                    if student_answer.lower().strip() == correct_answer:
                        correct_count += 1
        
        # Calculer le score
        total = exercises.count()
        score = (correct_count / total * 100) if total > 0 else 0
        
        # Mettre à jour la soumission
        from django.utils import timezone
        submission.answers = answers
        submission.correct_count = correct_count
        submission.score = score
        submission.is_completed = True
        submission.completed_at = timezone.now()
        submission.save()
        
        messages.success(request, f"Exercices soumis ! Score : {score:.1f}%")
        return redirect('exercise_generator:student_exercise_result', set_id=set_id)
    
    context = {
        'exercise_set': exercise_set,
        'exercises': exercises,
        'submission': submission,
    }
    return render(request, 'exercise_generator/student_take_exercise_set.html', context)


@login_required
def student_exercise_result(request, set_id):
    """
    Résultats d'un étudiant pour un set (avec corrections)
    """
    from .models import ExerciseSet, StudentExerciseSubmission
    
    exercise_set = get_object_or_404(ExerciseSet, pk=set_id, status='published')
    submission = get_object_or_404(
        StudentExerciseSubmission,
        student=request.user,
        exercise_set=exercise_set,
        is_completed=True
    )
    
    # Récupérer les exercices avec les réponses de l'étudiant
    exercises = exercise_set.exercises.all()
    exercise_results = []
    
    for exercise in exercises:
        student_answer = submission.answers.get(str(exercise.id))
        options_data = exercise.options_data
        
        # Déterminer la réponse correcte
        if exercise.exercise_type == 'mcq':
            correct_answer = options_data.get('correct')
            is_correct = (student_answer == correct_answer)
        elif exercise.exercise_type == 'true_false':
            correct_answer = str(options_data.get('correct'))
            is_correct = (student_answer == str(correct_answer))
        elif exercise.exercise_type == 'fill_blank':
            correct_answer = options_data.get('correct')
            is_correct = (student_answer and student_answer.lower().strip() == correct_answer.lower().strip())
        else:
            correct_answer = None
            is_correct = False
        
        exercise_results.append({
            'exercise': exercise,
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
        })
    
    context = {
        'exercise_set': exercise_set,
        'submission': submission,
        'exercise_results': exercise_results,
    }
    return render(request, 'exercise_generator/student_exercise_result.html', context)
