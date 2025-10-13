"""
Vues pour la génération automatique d'exercices par IA
"""
from bson.objectid import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import models
from django.conf import settings
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
# HELPER FUNCTIONS
# ============================================

def convert_to_objectid(pk):
    """
    Convertit un pk (string ou ObjectId) en ObjectId MongoDB
    """
    if isinstance(pk, ObjectId):
        return pk
    try:
        return ObjectId(pk)
    except:
        return pk


def get_mongo_document_simple(model_class, pk):
    """
    Récupère un document MongoDB via PyMongo direct (version simplifiée sans filtre teacher)
    Retourne une instance Django du modèle
    """
    from django.http import Http404
    from pymongo import MongoClient
    
    try:
        object_id = ObjectId(pk)
    except:
        raise Http404(f"{model_class.__name__} non trouvé")
    
    # Connexion MongoDB directe
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Nom de la collection
    collection_name = model_class._meta.db_table
    collection = db[collection_name]
    
    # Requête PyMongo simple
    doc_data = collection.find_one({'_id': object_id})
    
    if not doc_data:
        client.close()
        raise Http404(f"{model_class.__name__} non trouvé")
    
    # Créer une instance Django
    doc_id = doc_data.pop('_id', None)
    obj = model_class(**{k: v for k, v in doc_data.items() if k != '_id'})
    obj.pk = doc_id
    obj.id = doc_id
    obj._state.adding = False
    obj._state.db = 'default'
    
    client.close()
    return obj


def get_mongo_object(model_class, pk, **kwargs):
    """
    Récupère un objet MongoDB via PyMongo direct (contourne tous les bugs Djongo)
    """
    from django.http import Http404
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    
    try:
        object_id = convert_to_objectid(pk)
    except:
        raise Http404(f"{model_class.__name__} non trouvé")
    
    # Connexion MongoDB directe
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Nom de la collection
    collection_name = model_class._meta.db_table
    collection = db[collection_name]
    
    # Construire le filtre MongoDB
    mongo_filter = {'_id': object_id}
    
    # Ajouter les filtres additionnels
    for key, value in kwargs.items():
        if hasattr(value, 'id'):
            mongo_filter[f'{key}_id'] = value.id
        else:
            mongo_filter[key] = value
    
    # Requête PyMongo
    doc_data = collection.find_one(mongo_filter)
    
    if not doc_data:
        raise Http404(f"{model_class.__name__} non trouvé")
    
    # Créer une instance Django à partir des données brutes
    # Retirer _id car Django attend 'id' ou 'pk'
    doc_id = doc_data.pop('_id', None)
    
    # Préparer les données pour l'initialisation
    # Séparer les champs normaux des ForeignKey
    init_data = {}
    for field in model_class._meta.fields:
        if field.name == 'id':
            continue
        
        # Pour les ForeignKey, utiliser l'attribut _id
        if isinstance(field, models.ForeignKey):
            fk_field_name = f'{field.name}_id'
            if fk_field_name in doc_data:
                # Stocker directement l'ID sans charger l'objet
                init_data[fk_field_name] = doc_data[fk_field_name]
        elif field.name in doc_data:
            init_data[field.name] = doc_data[field.name]
    
    # Créer l'instance sans déclencher de requêtes
    obj = model_class()
    
    # Assigner les valeurs directement sans passer par __init__
    for key, value in init_data.items():
        setattr(obj, key, value)
    
    # Assigner le pk manuellement (évite save())
    obj.pk = doc_id
    obj.id = doc_id
    
    # Marquer comme "venant de la DB" pour que Django ne tente pas de l'insérer
    obj._state.adding = False
    obj._state.db = 'default'
    
    return obj


# ============================================
# DASHBOARD
# ============================================

@login_required
def dashboard(request):
    """
    Tableau de bord principal pour la génération d'exercices
    """
    from pymongo import MongoClient
    from django.conf import settings
    
    # Connexion MongoDB directe pour éviter les bugs Djongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Documents récents via PyMongo
    # Note: created_at est souvent None, utiliser updated_at comme fallback
    recent_documents_data = list(db.course_documents.find({
        'teacher_id': request.user.id
    }).sort([('updated_at', -1), ('_id', -1)]).limit(5))
    
    # Convertir en objets Django
    recent_documents = []
    for doc_data in recent_documents_data:
        doc_id = doc_data.pop('_id', None)
        document = CourseDocument(**{k: v for k, v in doc_data.items() if k != '_id'})
        document.pk = doc_id
        document.id = doc_id
        document._state.adding = False
        document._state.db = 'default'
        recent_documents.append(document)
    
    # 🔧 NORMALISATION AUTOMATIQUE DES TEACHER_ID
    # Importer le système de normalisation
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    try:
        from teacher_id_normalizer import TeacherIdNormalizer
        normalizer = TeacherIdNormalizer()
        normalizer.check_and_fix_if_needed()  # Auto-fix si nécessaire
        normalizer.close()
    except Exception as e:
        print(f"⚠️ Normalisation automatique échouée: {e}")
    
    # Récupérer les IDs des documents de l'enseignant pour filtrer les exercices
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': request.user.id})]
    
    # Exercices récents via PyMongo
    recent_exercises_data = list(db.generated_exercises.find({
        'source_document_id': {'$in': teacher_document_ids}
    }).sort('created_at', -1).limit(10))
    
    # DEBUG: Afficher les exercices trouvés
    print(f"🔍 Exercices trouvés: {len(recent_exercises_data)}")
    if recent_exercises_data:
        print(f"🔍 Premier exercice source_doc_id: {recent_exercises_data[0].get('source_document_id')}")
    
    # Convertir en objets Django
    recent_exercises = []
    for ex_data in recent_exercises_data:
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**{k: v for k, v in ex_data.items() if k != '_id'})
        exercise.pk = ex_id
        exercise.id = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        recent_exercises.append(exercise)
    
    # Statistiques via PyMongo
    total_documents = db.course_documents.count_documents({'teacher_id': request.user.id})
    total_exercises = db.generated_exercises.count_documents({'source_document_id': {'$in': teacher_document_ids}})
    
    # 🔧 CORRECTION: Tests = Exercices publiés + Exercise Sets publiés
    published_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'published'
    })
    published_exercise_sets = db.exercise_sets.count_documents({
        'teacher_id': {'$in': [request.user.id, str(request.user.id)]},
        'status': 'published'
    })
    total_tests = published_exercises + published_exercise_sets
    
    # 🔧 CORRECTION: Exercices validés (seulement ceux avec status='validated')
    validated_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'validated'
    })
    
    pending_exercises = db.generated_exercises.count_documents({
        'source_document_id': {'$in': teacher_document_ids},
        'status': 'draft'
    })
    
    stats = {
        'total_documents': total_documents,
        'total_exercises': total_exercises,
        'total_tests': total_tests,
        'validated_exercises': validated_exercises,
        'pending_exercises': pending_exercises,
    }
    
    # Distribution par type d'exercice via PyMongo
    exercise_type_distribution = {
        'mcq': db.generated_exercises.count_documents({
            'source_document_id': {'$in': teacher_document_ids},
            'exercise_type': 'mcq'
        }),
        'true_false': db.generated_exercises.count_documents({
            'source_document_id': {'$in': teacher_document_ids},
            'exercise_type': 'true_false'
        }),
        'fill_blank': db.generated_exercises.count_documents({
            'source_document_id': {'$in': teacher_document_ids},
            'exercise_type': 'fill_blank'
        }),
    }
    
    client.close()
    
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
    from pymongo import MongoClient
    
    # Récupérer le document (sans filtre teacher pour permettre accès aux étudiants)
    document = get_mongo_document_simple(CourseDocument, pk)
    
    # Récupérer les exercices via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    exercises_data = list(db.generated_exercises.find(
        {'source_document_id': document.pk}
    ).sort([('quality_score', -1), ('created_at', -1)]))
    
    # Créer des instances Django manuellement
    exercises = []
    for ex_data in exercises_data:
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**ex_data)
        exercise.pk = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        exercises.append(exercise)
    
    # Statistiques des exercices
    exercise_stats = {
        'total': len(exercises),
        'validated': len([e for e in exercises if e.status == 'validated']),
        'draft': len([e for e in exercises if e.status == 'draft']),
        'rejected': len([e for e in exercises if e.status == 'rejected']),
        'mcq': len([e for e in exercises if e.exercise_type == 'mcq']),
        'true_false': len([e for e in exercises if e.exercise_type == 'true_false']),
        'fill_blank': len([e for e in exercises if e.exercise_type == 'fill_blank']),
    }
    
    # Pagination des exercices
    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Fermer la connexion MongoDB
    client.close()
    
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
    # Récupérer le document (utilise la fonction helper simplifiée)
    document = get_mongo_document_simple(CourseDocument, pk)
    
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
    from pymongo import MongoClient
    from django.conf import settings
    from django.core.paginator import Paginator
    
    # Filtres
    exercise_type = request.GET.get('type', '')
    difficulty = request.GET.get('difficulty', '')
    status = request.GET.get('status', '')
    concept = request.GET.get('concept', '')
    
    # Connexion MongoDB directe
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Récupérer les IDs des documents de l'enseignant
    teacher_document_ids = [doc['_id'] for doc in db.course_documents.find({'teacher_id': request.user.id})]
    
    # Construire le filtre MongoDB
    mongo_filter = {'source_document_id': {'$in': teacher_document_ids}}
    
    if exercise_type:
        mongo_filter['exercise_type'] = exercise_type
    if difficulty:
        mongo_filter['difficulty'] = difficulty
    if status:
        mongo_filter['status'] = status
    if concept:
        mongo_filter['concept'] = {'$regex': concept, '$options': 'i'}
    
    # Récupérer les exercices
    exercises_data = list(db.generated_exercises.find(mongo_filter).sort('created_at', -1))
    
    # Convertir en objets Django
    exercises = []
    for ex_data in exercises_data:
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**{k: v for k, v in ex_data.items() if k != '_id'})
        exercise.pk = ex_id
        exercise.id = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        
        # Charger le document source
        source_doc_id = ex_data.get('source_document_id')
        if source_doc_id:
            doc_data = db.course_documents.find_one({'_id': source_doc_id})
            if doc_data:
                doc_data_clean = {k: v for k, v in doc_data.items() if k != '_id'}
                source_document = CourseDocument(**doc_data_clean)
                source_document.pk = doc_data['_id']
                source_document.id = doc_data['_id']
                source_document._state.adding = False
                source_document._state.db = 'default'
                exercise.source_document = source_document
        
        exercises.append(exercise)
    
    client.close()
    
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
    from pymongo import MongoClient
    
    # Récupérer l'exercice (sans filtre teacher pour permettre accès universel)
    exercise = get_mongo_document_simple(GeneratedExercise, pk)
    
    # Récupérer le document source via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    source_doc_data = None
    if exercise.source_document_id:  # Vérifier que source_document_id n'est pas None/vide
        source_doc_data = db.course_documents.find_one({
            '_id': exercise.source_document_id
        })
    
    if source_doc_data:
        # Créer instance Django du document source pour le template
        doc_id = source_doc_data.pop('_id', None)
        source_document = CourseDocument(**{k: v for k, v in source_doc_data.items() if k != '_id'})
        source_document.pk = doc_id
        source_document.id = doc_id
        source_document._state.adding = False
        source_document._state.db = 'default'
    else:
        source_document = None
    
    client.close()
    
    context = {
        'exercise': exercise,
        'source_document': source_document,  # Pour le template
    }
    
    return render(request, 'exercise_generator/exercise_detail.html', context)


@login_required
@require_http_methods(["POST"])
def exercise_validate(request, pk):
    """
    Valider un exercice
    """
    from pymongo import MongoClient
    from django.conf import settings
    from django.http import Http404
    from datetime import datetime
    
    # Récupérer l'exercice
    exercise = get_mongo_object(GeneratedExercise, pk)
    
    # Vérifier que le document source appartient au professeur connecté
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    source_doc = db.course_documents.find_one({
        '_id': exercise.source_document_id,
        'teacher_id': request.user.id
    })
    
    if not source_doc:
        raise Http404("Exercice non trouvé ou accès non autorisé")
    
    action = request.POST.get('action', 'validate')
    notes = request.POST.get('notes', '')
    
    if action == 'validate':
        # Utiliser PyMongo pour la mise à jour directe
        update_result = db.generated_exercises.update_one(
            {'_id': exercise.pk},
            {
                '$set': {
                    'status': 'validated',
                    'validated_by_id': request.user.id,
                    'validation_notes': notes,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if update_result.modified_count > 0:
            message = "Exercice validé avec succès."
        else:
            message = "Erreur lors de la validation."
        
        messages.success(request, message)
        client.close()
        # Redirection vers la liste des exercices après validation
        return redirect('exercise_generator:exercise_list')
            
    elif action == 'reject':
        # Supprimer l'exercice au lieu de le marquer comme rejeté
        # Utiliser PyMongo pour s'assurer de la suppression
        exercise_doc = db.generated_exercises.find_one({'_id': exercise.pk})
        if exercise_doc:
            # Supprimer de MongoDB
            db.generated_exercises.delete_one({'_id': exercise.pk})
            
            # Supprimer aussi les relations ManyToMany si elles existent
            db.exercise_generator_exerciseset_exercises.delete_many({
                'generatedexercise_id': str(exercise.pk)
            })
            
            message = "Exercice supprimé avec succès."
        else:
            message = "Exercice déjà supprimé."
        
        messages.success(request, message)
        client.close()
        # Redirection vers la liste des exercices car l'exercice n'existe plus
        return redirect('exercise_generator:exercise_list')
        
    else:
        messages.error(request, "Action non reconnue.")
        client.close()
        return redirect('exercise_generator:exercise_detail', pk=pk)
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
    # Récupérer le document sans restriction teacher
    document = get_mongo_document_simple(CourseDocument, document_pk)
    
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
        # Récupérer les exercices manuellement (contourne bug ObjectId)
        from pymongo import MongoClient
        from django.conf import settings
        
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]
        
        # Tous les exercices du document
        all_ex_data = list(db.generated_exercises.find(
            {'source_document_id': document.pk}
        ).sort('quality_score', -1))
        
        available_exercises = []
        selected_exercises = []
        
        for ex_data in all_ex_data:
            ex_id = ex_data.pop('_id', None)
            exercise = GeneratedExercise(**ex_data)
            exercise.pk = ex_id
            exercise._state.adding = False
            exercise._state.db = 'default'
            
            available_exercises.append(exercise)
            
            # Pré-sélectionner les exercices validés (10 premiers)
            if exercise.status in ['validated', 'published'] and len(selected_exercises) < 10:
                selected_exercises.append(exercise)
        
        form = TestCreationForm(initial={
            'title': f"Test - {document.title}",
            'description': document.description or "",
        })
    
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
    # Récupérer le test sans restriction teacher
    test = get_mongo_document_simple(GeneratedTest, pk)
    
    # Récupérer les exercices manuellement (contourne bug ObjectId)
    from pymongo import MongoClient
    from django.conf import settings
    
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Les IDs des exercices sont stockés dans test.exercise_ids (ArrayField)
    exercises_data = list(db.generated_exercises.find(
        {'_id': {'$in': test.exercise_ids}}
    ).sort([('difficulty', 1), ('exercise_type', 1)]))
    
    exercises = []
    for ex_data in exercises_data:
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**ex_data)
        exercise.pk = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        exercises.append(exercise)
    
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
    # Récupérer le test sans restriction teacher
    test = get_mongo_document_simple(GeneratedTest, pk)
    
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
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    
    # Récupérer directement via PyMongo pour éviter les problèmes avec Django ORM
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # 🔧 NORMALISATION AUTOMATIQUE DES TEACHER_ID
    # Importer le système de normalisation
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    try:
        from teacher_id_normalizer import TeacherIdNormalizer
        normalizer = TeacherIdNormalizer()
        normalizer.check_and_fix_if_needed()  # Auto-fix si nécessaire
        normalizer.close()
    except Exception as e:
        print(f"⚠️ Normalisation automatique échouée: {e}")
    
    # Récupérer les ExerciseSets de cet enseignant (recherche avec int ET string)
    sets_data = list(db.exercise_sets.find({
        'teacher_id': {'$in': [request.user.id, str(request.user.id)]}
    }).sort('created_at', -1))
    
    # Convertir en objets Django
    sets = []
    for data in sets_data:
        exercise_set = ExerciseSet()
        exercise_set.pk = data['_id']
        exercise_set.id = data['_id']
        exercise_set.title = data.get('title', '')
        exercise_set.description = data.get('description', '')
        exercise_set.status = data.get('status', 'draft')
        exercise_set.published_at = data.get('published_at')
        exercise_set.created_at = data.get('created_at')
        exercise_set.teacher_id = data.get('teacher_id')
        exercise_set.source_document_id = data.get('source_document_id')
        
        # Marquer l'objet comme déjà sauvegardé
        exercise_set._state.adding = False
        exercise_set._state.db = 'default'
        
        # Compter les exercices via MongoDB au lieu de Django ORM
        exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': str(data['_id'])
        })
        exercise_set._exercise_count = exercise_count  # Stocker pour usage dans le template
        
        sets.append(exercise_set)
    
    client.close()
    
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
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le document sans restriction teacher
    document = get_mongo_document_simple(CourseDocument, document_id)
    
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
        
        # Récupérer les exercices via PyMongo (contourne bug ObjectId)
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]
        
        # Convertir exercise_ids en ObjectId
        from bson import ObjectId as BsonObjectId
        object_ids = [convert_to_objectid(eid) for eid in exercise_ids]
        
        exercises_data = list(db.generated_exercises.find({
            '_id': {'$in': object_ids},
            'source_document_id': document.pk
        }))
        
        # ✅ FIX: Insérer directement dans la table ManyToMany via PyMongo
        # La table through s'appelle: exercise_generator_exerciseset_exercises
        # Colonnes: id, exerciseset_id, generatedexercise_id
        # IMPORTANT: Stocker les IDs comme strings pour cohérence
        
        # D'abord, vider les relations existantes pour ce set
        db['exercise_generator_exerciseset_exercises'].delete_many({
            'exerciseset_id': str(exercise_set.pk)  # ← String
        })
        
        # Créer les nouvelles relations
        relations = []
        for ex_data in exercises_data:
            ex_id = ex_data['_id']
            relations.append({
                'exerciseset_id': str(exercise_set.pk),  # ← String
                'generatedexercise_id': str(ex_id)  # ← String
            })
        
        if relations:
            db['exercise_generator_exerciseset_exercises'].insert_many(relations)
        
        messages.success(
            request,
            f"Set '{title}' créé avec {len(exercises_data)} exercices ! Vous pouvez maintenant le publier."
        )
        
        client.close()
        return redirect('exercise_generator:exercise_set_detail', set_id=exercise_set.id)
    
    # GET : afficher le formulaire - Récupérer exercices via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    exercises_data = list(db.generated_exercises.find({'source_document_id': document.pk}))
    
    exercises = []
    for ex_data in exercises_data:
        ex_id = ex_data.pop('_id', None)
        ex = GeneratedExercise(**ex_data)
        ex.pk = ex_id
        ex._state.adding = False
        ex._state.db = 'default'
        exercises.append(ex)
    
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
    from .models import ExerciseSet, CourseDocument, GeneratedExercise
    from pymongo import MongoClient
    
    # Récupérer le set sans restriction teacher
    exercise_set = get_mongo_document_simple(ExerciseSet, set_id)
    
    # ✅ Récupérer le document source via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    source_doc_data = db.course_documents.find_one({'_id': exercise_set.source_document_id})
    if source_doc_data:
        doc_id = source_doc_data.pop('_id', None)
        source_document = CourseDocument(**source_doc_data)
        source_document.pk = doc_id
        source_document._state.adding = False
        source_document._state.db = 'default'
    else:
        source_document = None
    
    # ✅ Récupérer les exercices via PyMongo (from ManyToMany through table)
    # La table through: exercise_generator_exerciseset_exercises
    # IMPORTANT: Les IDs sont stockés comme strings dans cette table
    relations = list(db['exercise_generator_exerciseset_exercises'].find({
        'exerciseset_id': str(exercise_set.pk)  # ← Convertir en string
    }))
    
    # Récupérer les exercices par leurs IDs
    exercise_ids = [rel['generatedexercise_id'] for rel in relations]
    exercises_data = list(db.generated_exercises.find({
        '_id': {'$in': exercise_ids}
    }))
    
    # Créer instances Django
    exercises = []
    for ex_data in exercises_data:
        ex_id = ex_data.pop('_id', None)
        ex = GeneratedExercise(**ex_data)
        ex.pk = ex_id
        ex._state.adding = False
        ex._state.db = 'default'
        exercises.append(ex)
    
    # ✅ Récupérer statistiques de soumissions via PyMongo
    submissions_count = db.student_exercise_submissions.count_documents({
        'exercise_set_id': exercise_set.pk
    })
    
    # Calculer score moyen si des soumissions existent
    avg_score = 0.0
    if submissions_count > 0:
        submissions_data = list(db.student_exercise_submissions.find({
            'exercise_set_id': exercise_set.pk,
            'is_completed': True
        }))
        if submissions_data:
            total_score = sum(sub.get('score', 0) for sub in submissions_data)
            avg_score = total_score / len(submissions_data)
    
    client.close()
    
    context = {
        'exercise_set': exercise_set,
        'source_document': source_document,  # ✅ Passer explicitement
        'exercises': exercises,
        'submissions_count': submissions_count,  # ✅ Nombre de soumissions
        'avg_score': avg_score,  # ✅ Score moyen
    }
    return render(request, 'exercise_generator/exercise_set_detail.html', context)


@login_required
def publish_exercise_set(request, set_id):
    """
    Publier un set pour les étudiants
    """
    from .models import ExerciseSet
    from pymongo import MongoClient
    
    # Récupérer le set sans restriction teacher
    exercise_set = get_mongo_document_simple(ExerciseSet, set_id)
    
    # ✅ Compter les exercices via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # IMPORTANT: Les IDs sont stockés comme strings dans la table ManyToMany
    exercise_count = db['exercise_generator_exerciseset_exercises'].count_documents({
        'exerciseset_id': str(exercise_set.pk)  # ← Convertir en string
    })
    
    client.close()
    
    if exercise_count == 0:
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
    
    # Récupérer le set sans restriction teacher
    exercise_set = get_mongo_document_simple(ExerciseSet, set_id)
    exercise_set.unpublish()
    
    messages.success(request, f"Set '{exercise_set.title}' retiré de la publication")
    return redirect('exercise_generator:exercise_set_detail', set_id=set_id)


@login_required
def delete_exercise_set(request, set_id):
    """
    Supprimer un set d'exercices
    """
    from .models import ExerciseSet
    
    # Récupérer le set sans restriction teacher
    exercise_set = get_mongo_document_simple(ExerciseSet, set_id)
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
    from pymongo import MongoClient
    from django.conf import settings
    
    # Vérifier que c'est un étudiant
    try:
        profile = request.user.profile
        if profile.role != 'student':
            messages.error(request, "Accès réservé aux étudiants")
            return redirect('evaluation:teacher_dashboard')
    except:
        messages.error(request, "Profil utilisateur non trouvé")
        return redirect('evaluation:student_dashboard')
    
    # Récupérer via PyMongo pour éviter les erreurs ManyToMany
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Sets publiés
    sets_data = list(db.exercise_sets.find({'status': 'published'}).sort('published_at', -1))
    
    # Vérifier les soumissions existantes
    submissions = db.student_exercise_submissions.find({'student_id': request.user.id})
    completed_set_ids = set([str(sub.get('exercise_set_id', '')) for sub in submissions])
    
    # Convertir en objets Django
    exercise_sets = []
    for data in sets_data:
        exercise_set = ExerciseSet()
        exercise_set.pk = data['_id']
        exercise_set.id = data['_id']
        exercise_set._state.adding = False
        exercise_set._state.db = 'default'
        
        # Remplir tous les champs
        exercise_set.title = data.get('title', '')
        exercise_set.description = data.get('description', '')
        exercise_set.status = data.get('status', 'draft')
        exercise_set.teacher_id = data.get('teacher_id')
        exercise_set.source_document_id = data.get('source_document_id')
        exercise_set.created_at = data.get('created_at')
        exercise_set.published_at = data.get('published_at')
        exercise_set.updated_at = data.get('updated_at')
        
        # Pré-calculer le count des exercices
        exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': str(data['_id'])
        })
        exercise_set._exercise_count = exercise_count
        
        # Récupérer le nom du teacher pour éviter la requête ForeignKey
        teacher_id = data.get('teacher_id')
        if teacher_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                teacher = User.objects.get(id=teacher_id)
                exercise_set._teacher_name = teacher.get_full_name() or teacher.username
            except:
                exercise_set._teacher_name = 'Professeur'
        else:
            exercise_set._teacher_name = 'Professeur'
        
        exercise_sets.append(exercise_set)
    
    client.close()
    
    context = {
        'exercise_sets': exercise_sets,
        'completed_set_ids': completed_set_ids,
    }
    return render(request, 'exercise_generator/student_exercise_sets.html', context)


@login_required
def student_take_exercise_set(request, set_id):
    """
    Étudiant prend un set d'exercices (SANS voir les corrections)
    """
    from .models import ExerciseSet, StudentExerciseSubmission, GeneratedExercise
    from evaluation.models import UserProfile
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    from django.utils import timezone
    
    # Vérifier que c'est un étudiant
    try:
        profile = request.user.profile
        if profile.role != 'student':
            messages.error(request, "Accès réservé aux étudiants")
            return redirect('evaluation:teacher_dashboard')
    except:
        messages.error(request, "Profil utilisateur non trouvé")
        return redirect('evaluation:student_dashboard')
    
    # Connexion MongoDB
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Récupérer le set via PyMongo
    try:
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id), 'status': 'published'})
        if not set_data:
            client.close()
            messages.error(request, "Set d'exercices non trouvé ou non publié")
            return redirect('exercise_generator:student_exercise_sets')
    except Exception as e:
        client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('exercise_generator:student_exercise_sets')
    
    # Récupérer les exercices du set
    # IMPORTANT: Dans la table ManyToMany, les IDs sont stockés comme strings
    exercise_ids = db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': str(set_id)  # ← Convertir en string
    })
    exercise_id_list = [ex['generatedexercise_id'] for ex in exercise_ids]
    
    # Récupérer les exercices
    exercises_data = list(db.generated_exercises.find({
        '_id': {'$in': [ObjectId(eid) if isinstance(eid, str) else eid for eid in exercise_id_list]}
    }))
    
    # Vérifier si déjà soumis
    existing_submission = db.student_exercise_submissions.find_one({
        'student_id': request.user.id,
        'exercise_set_id': set_id
    })
    
    if existing_submission and existing_submission.get('status') == 'completed':
        client.close()
        messages.info(request, "Vous avez déjà complété ce set")
        return redirect('exercise_generator:student_exercise_result', set_id=set_id)
    
    if request.method == 'POST':
        # Traiter les réponses
        answers = {}
        correct_count = 0
        total_count = len(exercises_data)
        
        for exercise_data in exercises_data:
            exercise_id = str(exercise_data['_id'])
            answer_key = f'exercise_{exercise_id}'
            student_answer = request.POST.get(answer_key)
            
            if student_answer:
                answers[exercise_id] = student_answer
                
                # Vérifier la réponse
                options_data = exercise_data.get('options_data', {})
                correct_answer = options_data.get('correct')
                exercise_type = exercise_data.get('exercise_type')
                
                # Normaliser les réponses True/False
                if exercise_type == 'true_false':
                    # La réponse correcte est un booléen, convertir la réponse étudiant
                    student_bool = (student_answer == 'True' or student_answer == 'true')
                    if correct_answer == student_bool:
                        correct_count += 1
                else:
                    # Pour MCQ et autres types, comparaison directe
                    if correct_answer and str(student_answer) == str(correct_answer):
                        correct_count += 1
        
        # Calculer le score
        score = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # Créer ou mettre à jour la soumission
        submission_data = {
            'student_id': request.user.id,
            'exercise_set_id': set_id,
            'answers': answers,
            'correct_count': correct_count,
            'total_count': total_count,
            'score': round(score, 2),
            'status': 'completed',
            'submitted_at': timezone.now(),
            'updated_at': timezone.now()
        }
        
        if existing_submission:
            db.student_exercise_submissions.update_one(
                {'_id': existing_submission['_id']},
                {'$set': submission_data}
            )
        else:
            submission_data['created_at'] = timezone.now()
            db.student_exercise_submissions.insert_one(submission_data)
        
        client.close()
        messages.success(request, f"Exercices soumis! Score: {score:.1f}%")
        return redirect('exercise_generator:student_exercise_result', set_id=set_id)
    
    # Construire les objets exercices pour le template
    exercises = []
    for ex_data in exercises_data:
        # Créer instance complète avec tous les champs
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**{k: v for k, v in ex_data.items() if k != '_id'})
        exercise.pk = ex_id
        exercise.id = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        exercises.append(exercise)
    
    # Construire l'objet set pour le template
    set_id_obj = set_data.pop('_id', None)
    exercise_set = ExerciseSet(**{k: v for k, v in set_data.items() if k != '_id'})
    exercise_set.pk = set_id_obj
    exercise_set.id = set_id_obj
    exercise_set._state.adding = False
    exercise_set._state.db = 'default'
    
    client.close()
    
    context = {
        'exercise_set': exercise_set,
        'exercises': exercises,
        'exercise_count': len(exercises),
    }
    return render(request, 'exercise_generator/student_take_exercise_set.html', context)



@login_required
def student_exercise_result(request, set_id):
    """
    Résultats d'un étudiant pour un set (avec corrections)
    """
    from .models import ExerciseSet, GeneratedExercise
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    
    # Connexion MongoDB
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Récupérer le set
    try:
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id), 'status': 'published'})
        if not set_data:
            client.close()
            messages.error(request, "Set d'exercices non trouvé")
            return redirect('exercise_generator:student_exercise_sets')
    except Exception as e:
        client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('exercise_generator:student_exercise_sets')
    
    # Récupérer la soumission
    submission_data = db.student_exercise_submissions.find_one({
        'student_id': request.user.id,
        'exercise_set_id': set_id,
        'status': 'completed'
    })
    
    if not submission_data:
        client.close()
        messages.error(request, "Aucune soumission trouvée pour ce set")
        return redirect('exercise_generator:student_take_exercise_set', set_id=set_id)
    
    # Récupérer les exercices du set
    # IMPORTANT: Dans la table ManyToMany, les IDs sont stockés comme strings
    exercise_ids = db.exercise_generator_exerciseset_exercises.find({
        'exerciseset_id': str(set_id)  # ← Convertir en string
    })
    exercise_id_list = [ex['generatedexercise_id'] for ex in exercise_ids]
    
    # Récupérer les exercices
    exercises_data = list(db.generated_exercises.find({
        '_id': {'$in': [ObjectId(eid) if isinstance(eid, str) else eid for eid in exercise_id_list]}
    }))
    
    # Préparer les résultats
    exercise_results = []
    answers = submission_data.get('answers', {})
    
    for ex_data in exercises_data:
        exercise_id = str(ex_data['_id'])
        student_answer = answers.get(exercise_id)
        options_data = ex_data.get('options_data', {})
        exercise_type = ex_data.get('exercise_type', 'mcq')
        
        # Trouver la bonne réponse
        correct_answer = options_data.get('correct')
        
        # Vérifier si la réponse est correcte (gérer True/False)
        if exercise_type == 'true_false':
            student_bool = (student_answer == 'True' or student_answer == 'true')
            is_correct = (correct_answer == student_bool)
        else:
            is_correct = (str(student_answer) == str(correct_answer)) if correct_answer else False
        
        # Créer l'objet exercice complet
        ex_id = ex_data.pop('_id', None)
        exercise = GeneratedExercise(**{k: v for k, v in ex_data.items() if k != '_id'})
        exercise.pk = ex_id
        exercise.id = ex_id
        exercise._state.adding = False
        exercise._state.db = 'default'
        
        exercise_results.append({
            'exercise': exercise,
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
        })
    
    # Créer l'objet set
    exercise_set = ExerciseSet(
        id=set_id,
        title=set_data.get('title', ''),
        description=set_data.get('description', '')
    )
    exercise_set.pk = set_id
    
    client.close()
    
    context = {
        'exercise_set': exercise_set,
        'submission': submission_data,
        'exercise_results': exercise_results,
    }
    return render(request, 'exercise_generator/student_exercise_result.html', context)

