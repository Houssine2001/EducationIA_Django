from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import logging
import secrets
import os

from .models import Resource, ResourceTag, ResourceTagging, SavedResource
from .forms import ResourceUploadForm, ResourceFilterForm, ResourceEditForm
from .ai_services import ai_service

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Tableau de bord principal : affiche les ressources de l'utilisateur"""
    resources = Resource.objects.filter(user=request.user)
    
    # Récupérer les valeurs des filtres
    search = request.GET.get('search', '')
    resource_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    # Appliquer les filtres
    filter_form = ResourceFilterForm(request.GET)
    
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search') or search
        resource_type = filter_form.cleaned_data.get('type') or resource_type
        status = filter_form.cleaned_data.get('status') or status
        order_by = filter_form.cleaned_data.get('order_by') or '-created_at'
        
        if search:
            resources = resources.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(summary__icontains=search)
            )
        
        if resource_type:
            resources = resources.filter(type=resource_type)
        
        if status:
            resources = resources.filter(processing_status=status)
        
        resources = resources.order_by(order_by)
    else:
        resources = resources.order_by('-created_at')
    
    # Statistiques
    stats = {
        'total': resources.count(),
        'pdf': resources.filter(type='pdf').count(),
        'video': resources.filter(type='video').count(),
        'text': resources.filter(type='text').count(),
        'processed': resources.filter(processing_status='completed').count(),
        'pending': resources.filter(processing_status='pending').count(),
        'processing': resources.filter(processing_status='processing').count(),
    }
    
    # Pagination
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'search': search,
        'resource_type': resource_type,
        'status': status,
    }
    
    return render(request, 'resources/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def upload_resource(request):
    """Upload une nouvelle ressource"""
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.processing_status = 'pending'
            resource.save()
            
            # Récupérer l'ID integer depuis MongoDB avec PyMongo (refresh_from_db ne fonctionne pas avec Djongo)
            try:
                import os
                from pymongo import MongoClient
                mongo_host = os.environ.get('MONGO_HOST', 'localhost')
                mongo_port = int(os.environ.get('MONGO_PORT', '27017'))
                mongo_db = os.environ.get('MONGO_DB_NAME', 'django_education')
                client = MongoClient(host=mongo_host, port=mongo_port)
                db = client[mongo_db]
                collection = db['resources_resource']
                # Chercher par share_token qui est unique
                doc = collection.find_one({'share_token': str(resource.share_token)})
                if not doc or 'id' not in doc:
                    logger.error(f"Impossible de récupérer l'ID de la ressource avec token {resource.share_token}")
                    messages.warning(request, 'Ressource uploadée, mais l\'ID n\'a pas été généré correctement.')
                    return redirect('resources:dashboard')
                resource_id_int = int(doc['id'])
                logger.info(f"ID integer récupéré depuis MongoDB: {resource_id_int}")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'ID: {e}", exc_info=True)
                messages.error(request, 'Erreur lors de la récupération de l\'ID de la ressource.')
                return redirect('resources:dashboard')
            # Lancer le traitement IA en arrière-plan (thread séparé)
            try:
                import threading
                thread = threading.Thread(target=process_resource_ai, args=(resource_id_int,))
                thread.daemon = True
                thread.start()
                logger.info(f"Thread de traitement IA lancé pour resource {resource_id_int}")
                messages.success(request, f'Ressource "{resource.title}" uploadée avec succès ! Le résumé IA est en cours de génération.')
            except Exception as e:
                logger.error(f"Erreur lors du lancement du thread IA: {e}", exc_info=True)
                messages.error(request, 'Erreur lors du lancement du traitement IA.')
            return redirect('resources:dashboard')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez corriger les erreurs.')
    else:
        form = ResourceUploadForm()
    
    return render(request, 'resources/upload.html', {'form': form})


def process_resource_ai(resource_id):
    """Traite une ressource avec l'IA"""
    try:
        resource = Resource.objects.get(id=resource_id)
        logger.info(f"Début du traitement de la ressource {resource_id} - Type: {resource.type}")
        
        resource.processing_status = 'processing'
        resource.save(update_fields=['processing_status'])
        
        result = ai_service.process_resource(resource)
        logger.info(f"Résultat du traitement pour {resource_id}: success={result['success']}")
        
        if result['success']:
            resource.summary = result['summary']
            resource.processing_status = 'completed'
            resource.error_message = ''
            logger.info(f"Résumé généré avec succès pour {resource_id}: {len(result['summary'])} caractères")
        else:
            resource.processing_status = 'failed'
            resource.error_message = result.get('error', 'Erreur inconnue')
            logger.error(f"Échec du traitement pour {resource_id}: {resource.error_message}")
        
        resource.save()
        logger.info(f"Ressource {resource_id} sauvegardée avec statut: {resource.processing_status}")
        
    except Resource.DoesNotExist:
        logger.error(f"Ressource {resource_id} introuvable")
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la ressource {resource_id} : {e}", exc_info=True)
        try:
            resource = Resource.objects.get(id=resource_id)
            resource.processing_status = 'failed'
            resource.error_message = f"Exception: {e}"
            resource.save(update_fields=['processing_status', 'error_message'])
        except Exception as e2:
            logger.error(f"Impossible de sauvegarder l'erreur sur la ressource {resource_id}: {e2}", exc_info=True)


@login_required
def resource_detail(request, resource_id):
    """Affiche les détails d'une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    resource.increment_views()
    
    context = {
        'resource': resource,
    }
    
    return render(request, 'resources/detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def resource_edit(request, resource_id):
    """Édite une ressource existante"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    
    if request.method == 'POST':
        form = ResourceEditForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ressource mise à jour avec succès !')
            return redirect('resources:detail', resource_id=resource.id)
    else:
        form = ResourceEditForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
    }
    
    return render(request, 'resources/edit.html', context)


@login_required
@require_http_methods(["POST"])
def resource_delete(request, resource_id):
    """Supprime une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    title = resource.title
    resource.delete()
    messages.success(request, f'Ressource "{title}" supprimée avec succès !')
    return redirect('resources:dashboard')


@login_required
def download_summary(request, resource_id):
    """Télécharge le résumé d'une ressource en format TXT"""
    # Vérifier si c'est une ressource publique ou la sienne
    try:
        resource = Resource.objects.get(id=resource_id)
        if resource.user != request.user and not resource.is_public:
            messages.error(request, 'Vous n\'avez pas accès à cette ressource.')
            return redirect('resources:dashboard')
    except Resource.DoesNotExist:
        messages.error(request, 'Ressource introuvable.')
        return redirect('resources:dashboard')
    
    if not resource.summary:
        messages.error(request, 'Aucun résumé disponible pour cette ressource.')
        if resource.user == request.user:
            return redirect('resources:detail', resource_id=resource.id)
        else:
            return redirect('resources:public_detail', resource_id=resource.id)
    
    resource.increment_downloads()
    
    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="resume_{resource.id}.txt"'
    
    content = f"""Résumé de : {resource.title}
Généré le : {timezone.now().strftime('%d/%m/%Y %H:%M')}
Type : {resource.get_type_display()}
{'='*60}

{resource.summary}

{'='*60}
Ressource créée le : {resource.created_at.strftime('%d/%m/%Y %H:%M')}
Par : {resource.user.get_full_name() or resource.user.username}
"""
    
    response.write(content)
    return response


@login_required
@require_http_methods(["POST"])
def regenerate_summary(request, resource_id):
    """Régénère le résumé d'une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    
    try:
        logger.info(f"=== DÉBUT RÉGÉNÉRATION pour resource {resource_id} ===")
        
        # Réinitialiser le statut et effacer l'ancien résumé
        resource.processing_status = 'pending'
        resource.summary = ''
        resource.error_message = ''
        resource.save(update_fields=['processing_status', 'summary', 'error_message'])
        logger.info(f"Statut réinitialisé à 'pending' pour resource {resource_id}")
        
        # Relancer le traitement IA en arrière-plan
        logger.info(f"Lancement thread de traitement IA pour resource {resource_id}")
        import threading
        # resource_id est déjà un integer venant de l'URL
        thread = threading.Thread(target=process_resource_ai, args=(resource_id,))
        thread.daemon = True
        thread.start()
        
        messages.success(request, 'Le résumé est en cours de régénération. Actualisez la page dans quelques instants.')
            
    except Exception as e:
        logger.error(f"Erreur lors de la régénération du résumé : {e}", exc_info=True)
        messages.error(request, f'Erreur lors de la régénération : {str(e)}')
    
    return redirect('resources:detail', resource_id=resource_id)


@login_required
@require_http_methods(["POST"])
def share_resource(request, resource_id):
    """Génère un lien de partage pour une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    
    if not resource.share_token:
        resource.share_token = secrets.token_urlsafe(32)
        resource.save(update_fields=['share_token'])
    
    share_url = request.build_absolute_uri(
        reverse('resources:shared', kwargs={'token': resource.share_token})
    )
    
    return JsonResponse({
        'success': True,
        'share_url': share_url
    })


def shared_resource(request, token):
    """Affiche une ressource partagée (accès public)"""
    # Requête simple pour éviter les problèmes Djongo
    resource = get_object_or_404(Resource, share_token=token)
    
    # Vérifier manuellement si publique
    if not resource.is_public:
        messages.error(request, 'Cette ressource n\'est pas publique.')
        return redirect('resources:public_resources')
    
    resource.increment_views()
    
    tags = ResourceTag.objects.filter(taggings__resource=resource)
    
    context = {
        'resource': resource,
        'tags': tags,
        'is_shared_view': True,
    }
    
    return render(request, 'resources/shared.html', context)


@login_required
def api_resource_status(request, resource_id):
    """API pour vérifier le statut de traitement d'une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    
    return JsonResponse({
        'id': resource.id,
        'status': resource.processing_status,
        'has_summary': resource.has_summary,
        'error': resource.error_message,
        'summary_length': len(resource.summary) if resource.summary else 0,
    })


@login_required
def debug_resource(request, resource_id):
    """Vue de diagnostic pour déboguer le traitement d'une ressource"""
    resource = get_object_or_404(Resource, id=resource_id, user=request.user)
    
    debug_info = {
        'resource_id': resource.id,
        'title': resource.title,
        'type': resource.type,
        'file_path': resource.file.path if resource.file else None,
        'file_exists': os.path.exists(resource.file.path) if resource.file else False,
        'processing_status': resource.processing_status,
        'has_summary': resource.has_summary,
        'summary_length': len(resource.summary) if resource.summary else 0,
        'error_message': resource.error_message,
    }
    
    # Tenter d'extraire le texte
    if resource.file and os.path.exists(resource.file.path):
        try:
            from .ai_services import ai_service
            file_path = resource.file.path
            
            if resource.type == 'text':
                if file_path.endswith('.docx'):
                    text = ai_service.extract_text_from_docx(file_path)
                else:
                    text = ai_service.extract_text_from_text_file(file_path)
                
                debug_info['extracted_text_length'] = len(text) if text else 0
                debug_info['extracted_text_preview'] = text[:500] if text else None
                debug_info['text_starts_with_error'] = text.startswith('Erreur') if text else False
        except Exception as e:
            debug_info['extraction_error'] = str(e)
    
    from django.http import JsonResponse
    return JsonResponse(debug_info, json_dumps_params={'indent': 2, 'ensure_ascii': False})


@login_required
def public_resources(request):
    """Affiche les ressources publiques des autres utilisateurs"""
    # Récupérer toutes les ressources publiques (compatible MongoDB)
    try:
        # Requête simple pour MongoDB
        all_resources = list(Resource.objects.filter(processing_status='completed').order_by('-created_at'))
        # Filtrer en Python pour éviter les problèmes Djongo
        resources_list = [r for r in all_resources if r.is_public and r.user.id != request.user.id]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des ressources publiques: {e}")
        resources_list = []
    
    # Appliquer les filtres
    search = request.GET.get('search', '')
    resource_type = request.GET.get('type', '')
    
    if search:
        search_lower = search.lower()
        resources_list = [
            r for r in resources_list 
            if (r.title and search_lower in r.title.lower()) or 
               (r.description and search_lower in r.description.lower()) or
               (r.summary and search_lower in r.summary.lower())
        ]
    
    if resource_type:
        resources_list = [r for r in resources_list if r.type == resource_type]
    
    # Récupérer les ressources déjà sauvegardées par l'utilisateur
    try:
        saved_resources = list(SavedResource.objects.filter(user_id=request.user.id))
        saved_resource_ids = [sr.resource_id for sr in saved_resources]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sauvegardes: {e}")
        saved_resource_ids = []
    
    # Pagination manuelle
    from django.core.paginator import Paginator
    paginator = Paginator(resources_list, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'resource_type': resource_type,
        'saved_resource_ids': saved_resource_ids,
    }
    
    return render(request, 'resources/public_resources.html', context)


@login_required
@require_http_methods(["POST"])
def save_resource(request, resource_id):
    """Sauvegarde une ressource publique pour l'utilisateur"""
    try:
        # Récupérer la ressource - SANS is_public dans get() (problème Djongo)
        resource = get_object_or_404(Resource, id=resource_id)
        
        # Vérifier manuellement si publique
        if not resource.is_public:
            return JsonResponse({
                'success': False,
                'error': 'Cette ressource n\'est pas publique.'
            }, status=404)
        
        # Vérifier que ce n'est pas la propre ressource de l'utilisateur
        if resource.user.id == request.user.id:
            return JsonResponse({
                'success': False,
                'error': 'Vous ne pouvez pas sauvegarder votre propre ressource.'
            }, status=400)
        
        # Vérifier si déjà sauvegardée (compatible MongoDB)
        existing = list(SavedResource.objects.filter(
            user_id=request.user.id,
            resource_id=resource_id
        ))
        
        if existing:
            return JsonResponse({
                'success': False,
                'error': 'Vous avez déjà sauvegardé cette ressource.'
            }, status=400)
        
        # Créer la sauvegarde avec les IDs
        saved_resource = SavedResource()
        saved_resource.user_id = request.user.id
        saved_resource.resource_id = resource.id
        saved_resource.notes = ''
        saved_resource.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Ressource "{resource.title}" sauvegardée avec succès !'
        })
        
    except Resource.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ressource non trouvée.'
        }, status=404)
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        logger.error(f"Erreur lors de la sauvegarde de la ressource {resource_id} : {error_msg}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {error_msg}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def unsave_resource(request, resource_id):
    """Retire une ressource des sauvegardes de l'utilisateur"""
    try:
        # Supprimer directement via PyMongo car Djongo ne gère pas bien les IDs None
        from pymongo import MongoClient
        import os
        
        mongo_host = os.environ.get('MONGO_HOST', 'localhost')
        mongo_port = int(os.environ.get('MONGO_PORT', '27017'))
        mongo_db = os.environ.get('MONGO_DB_NAME', 'django_education')
        
        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[mongo_db]
        collection = db['resources_savedresource']
        
        # Supprimer toutes les sauvegardes correspondantes
        result = collection.delete_many({
            'user_id': request.user.id,
            'resource_id': resource_id
        })
        
        if result.deleted_count == 0:
            return JsonResponse({
                'success': False,
                'error': 'Cette ressource n\'est pas dans vos sauvegardes.'
            }, status=404)
        
        logger.info(f"Supprimé {result.deleted_count} sauvegarde(s) pour user {request.user.id}, resource {resource_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Ressource retirée de vos sauvegardes.'
        })
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la sauvegarde {resource_id} : {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Une erreur est survenue : {str(e)}'
        }, status=500)


@login_required
def my_saved_resources(request):
    """Affiche les ressources sauvegardées par l'utilisateur"""
    # Récupérer les sauvegardes (compatible MongoDB avec IDs)
    all_saved = SavedResource.objects.filter(user_id=request.user.id).order_by('-saved_at')
    saved_list = list(all_saved)
    
    # Filtrer les sauvegardes avec des ressources valides (non supprimées)
    valid_saved_list = []
    for saved in saved_list:
        try:
            # Vérifier que la ressource existe et est accessible
            if saved.resource and saved.resource.id:
                # Vérifier que l'utilisateur de la ressource existe aussi
                if hasattr(saved.resource, 'user') and saved.resource.user:
                    valid_saved_list.append(saved)
                else:
                    logger.warning(f"Ressource {saved.resource_id} sans utilisateur valide")
            else:
                logger.warning(f"SavedResource {saved.id} pointe vers une ressource inexistante")
                # Optionnel: supprimer la sauvegarde orpheline
                # saved.delete()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la sauvegarde {saved.id}: {e}")
    
    saved_list = valid_saved_list
    
    # Filtres côté Python
    search = request.GET.get('search', '')
    resource_type = request.GET.get('type', '')
    
    if search:
        search_lower = search.lower()
        saved_list = [
            s for s in saved_list 
            if (s.resource.title and search_lower in s.resource.title.lower()) or 
               (s.resource.description and search_lower in s.resource.description.lower()) or
               (s.notes and search_lower in s.notes.lower())
        ]
    
    if resource_type:
        saved_list = [s for s in saved_list if s.resource.type == resource_type]
    
    # Pagination manuelle
    from django.core.paginator import Paginator
    paginator = Paginator(saved_list, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'resource_type': resource_type,
    }
    
    return render(request, 'resources/saved_resources.html', context)


@login_required
def public_resource_detail(request, resource_id):
    """Affiche les détails d'une ressource publique"""
    # Requête simple pour éviter les problèmes Djongo
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Vérifier manuellement si publique et complétée
    if not resource.is_public or resource.processing_status != 'completed':
        messages.error(request, 'Cette ressource n\'est pas disponible.')
        return redirect('resources:public_resources')
    
    resource.increment_views()
    
    # Vérifier si l'utilisateur a déjà sauvegardé cette ressource (avec IDs)
    try:
        saved_list = list(SavedResource.objects.filter(
            user_id=request.user.id,
            resource_id=resource_id
        ))
        is_saved = len(saved_list) > 0
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de sauvegarde: {e}")
        is_saved = False
    
    context = {
        'resource': resource,
        'is_saved': is_saved,
        'is_public_view': True,
    }
    
    return render(request, 'resources/public_detail.html', context)