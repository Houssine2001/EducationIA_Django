"""
Vues pour l'application d'évaluation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Avg
import json

from .models import Test, Question, Submission, Result, UserProfile
from .services import TestService, AutoGrading, ResultService
from .ai_concept_analyzer import AIConceptAnalyzer
from backend.mongodb_utils import get_mongodb_client, get_mongodb_database
import re




# ============================================
# Fonctions Utilitaires
# ============================================

def _extract_concept_from_question(question_text, subject='Général'):
    """
    Extrait le concept principal d'une question en se basant sur des mots-clés
    """
    question_lower = question_text.lower()
    
    # Dictionnaire de mots-clés par domaine
    concept_keywords = {
        # Programmation
        'React': ['react', 'jsx', 'component', 'props', 'state', 'hook', 'usestate', 'useeffect', 'virtual dom'],
        'Components': ['component', 'composant', 'props', 'children'],
        'State Management': ['state', 'état', 'usestate', 'setstate', 'redux', 'context'],
        'Hooks': ['hook', 'usestate', 'useeffect', 'usememo', 'usecallback', 'useref', 'usecontext'],
        'Props': ['props', 'propriété', 'properties', 'propstype'],
        'Lifecycle': ['lifecycle', 'cycle de vie', 'componentdidmount', 'useeffect', 'cleanup'],
        'Events': ['event', 'événement', 'onclick', 'onchange', 'handler', 'gestionnaire'],
        'Routing': ['router', 'route', 'navigation', 'link', 'redirect'],
        'API Calls': ['axios', 'fetch', 'api', 'http', 'request', 'promise', 'async', 'await'],
        'Forms': ['form', 'formulaire', 'input', 'validation', 'submit'],
        
        # JavaScript
        'JavaScript': ['javascript', 'js', 'ecmascript'],
        'Arrays': ['array', 'tableau', 'map', 'filter', 'reduce', 'foreach'],
        'Functions': ['function', 'fonction', 'arrow', 'callback', 'closure'],
        'Promises': ['promise', 'async', 'await', 'then', 'catch'],
        'Objects': ['object', 'objet', 'class', 'constructor', 'prototype'],
        
        # Python
        'Python': ['python', 'py'],
        'Lists': ['list', 'liste', 'append', 'extend', 'pop'],
        'Dictionaries': ['dict', 'dictionnaire', 'key', 'value', 'items'],
        'Classes': ['class', 'classe', '__init__', 'self', 'method'],
        'Loops': ['loop', 'boucle', 'for', 'while', 'iteration'],
        
        # Mathématiques
        'Algèbre': ['algèbre', 'algebra', 'équation', 'equation', 'variable', 'polynôme'],
        'Géométrie': ['géométrie', 'geometry', 'triangle', 'cercle', 'angle', 'surface', 'périmètre'],
        'Analyse': ['analyse', 'calculus', 'dérivée', 'derivative', 'intégrale', 'integral', 'limite', 'limit'],
        'Probabilités': ['probabilité', 'probability', 'chance', 'aléatoire', 'random'],
        'Statistiques': ['statistique', 'statistic', 'moyenne', 'mean', 'médiane', 'median', 'écart-type'],
        'Trigonométrie': ['trigonométrie', 'trigonometry', 'sinus', 'cosinus', 'tangente', 'sin', 'cos', 'tan'],
        
        # Physique
        'Mécanique': ['mécanique', 'mechanics', 'force', 'masse', 'accélération', 'vitesse'],
        'Électricité': ['électricité', 'electricity', 'courant', 'voltage', 'résistance', 'circuit'],
        'Optique': ['optique', 'optics', 'lumière', 'light', 'réflexion', 'réfraction'],
        
        # Bases de données
        'SQL': ['sql', 'select', 'insert', 'update', 'delete', 'join', 'query'],
        'MongoDB': ['mongodb', 'nosql', 'document', 'collection', 'aggregate'],
        'Database Design': ['database', 'schema', 'table', 'relation', 'foreign key', 'primary key'],
    }
    
    # Chercher les mots-clés dans la question
    matched_concepts = []
    for concept, keywords in concept_keywords.items():
        for keyword in keywords:
            if keyword in question_lower:
                matched_concepts.append((concept, len(keyword)))  # Stocker avec la longueur du mot-clé
                break  # Un seul match par concept suffit
    
    # Retourner le concept avec le mot-clé le plus long (plus spécifique)
    if matched_concepts:
        matched_concepts.sort(key=lambda x: x[1], reverse=True)
        return matched_concepts[0][0]
    
    # Si aucun mot-clé trouvé, essayer d'extraire les noms propres ou termes techniques
    # Chercher les mots en majuscules ou entre guillemets
    technical_terms = re.findall(r'\b[A-Z][a-z]+\b|"([^"]+)"', question_text)
    if technical_terms:
        # Nettoyer et retourner le premier terme trouvé
        for term in technical_terms:
            if isinstance(term, tuple):
                term = term[0] if term[0] else term[1] if len(term) > 1 else ''
            if term and len(term) > 2:
                return term.strip()
    
    # Fallback sur le subject
    return subject


# ============================================
# Vues pour les Enseignants
# ============================================

@login_required
def teacher_dashboard(request):
    """
    Tableau de bord enseignant
    """
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux enseignants")
        return redirect('evaluation:student_dashboard')
    
    from pymongo import MongoClient
    from django.conf import settings
    
    # Connexion MongoDB
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    # Récupérer les tests créés par l'enseignant via PyMongo
    tests_data = list(db.tests.find({'created_by_id': request.user.id}).sort('created_at', -1))
    
    # Créer les instances Django manuellement
    tests = []
    for test_data in tests_data:
        test_id = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id
        test.id = test_id
        test._state.adding = False
        test._state.db = 'default'
        
        # Compter les questions pour ce test
        test.question_count = db.questions.count_documents({'test_id': test_id})
        
        # Compter les soumissions pour ce test
        test.submission_count = db.submissions.count_documents({'test_id': test_id})
        
        tests.append(test)
    
    # Statistiques globales
    stats = {
        'total_tests': len(tests),
        'published_tests': len([t for t in tests if t.status == 'published']),
        'total_submissions': db.submissions.count_documents({'test__created_by_id': request.user.id}),
    }
    
    client.close()
    
    context = {
        'tests': tests,
        'stats': stats
    }
    return render(request, 'evaluation/teacher/dashboard.html', context)


@login_required
def create_test(request):
    """
    Créer un nouveau test
    """
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux enseignants")
        return redirect('evaluation:student_dashboard')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        test_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description', ''),
            'subject': request.POST.get('subject'),
            'topic': request.POST.get('topic', ''),
            'difficulty': request.POST.get('difficulty', 'medium'),
            'duration': int(request.POST.get('duration', 60)),
            'passing_score': float(request.POST.get('passing_score', 50)),
            'total_points': float(request.POST.get('total_points', 100)),
            'is_timed': request.POST.get('is_timed') == 'on',
            'allow_review': request.POST.get('allow_review') == 'on',
            'shuffle_questions': request.POST.get('shuffle_questions') == 'on',
            'status': request.POST.get('status', 'draft'),
        }
        
        # Traiter les tags (séparés par virgules)
        tags_str = request.POST.get('tags', '')
        test_data['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Traiter les compétences
        skills_str = request.POST.get('skills_tested', '')
        test_data['skills_tested'] = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        
        # Créer le test
        test = TestService.create_test(request.user, test_data)
        
        messages.success(request, f"Test '{test.title}' créé avec succès !")
        return redirect('evaluation:edit_test', test_id=test.id)
    
    return render(request, 'evaluation/teacher/create_test.html')


@login_required
def edit_test(request, test_id):
    """
    Modifier un test existant
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo pour gérer ObjectId
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({
            '_id': ObjectId(test_id),
            'created_by_id': request.user.id
        })
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé")
            return redirect('evaluation:teacher_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:teacher_dashboard')
    
    if request.method == 'POST':
        # Mettre à jour le test
        test.title = request.POST.get('title')
        test.description = request.POST.get('description', '')
        test.subject = request.POST.get('subject')
        test.topic = request.POST.get('topic', '')
        test.difficulty = request.POST.get('difficulty', 'medium')
        
        # Gestion sécurisée des champs numériques
        duration_str = request.POST.get('duration', '60')
        test.duration = int(duration_str) if duration_str else 60
        
        passing_score_str = request.POST.get('passing_score', '50')
        test.passing_score = float(passing_score_str) if passing_score_str else 50.0
        
        # Gestion des booléens
        test.is_timed = request.POST.get('is_timed') == 'on'
        test.allow_review = request.POST.get('allow_review') == 'on'
        test.shuffle_questions = request.POST.get('shuffle_questions') == 'on'
        
        # Gestion du statut (IMPORTANT pour la visibilité des étudiants)
        test.status = request.POST.get('status', 'draft')
        
        # Si le test est publié, mettre à jour la date de publication
        if test.status == 'published' and not test.published_at:
            from django.utils import timezone
            test.published_at = timezone.now()
        
        tags_str = request.POST.get('tags', '')
        test.tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        skills_str = request.POST.get('skills_tested', '')
        test.skills_tested = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        
        test.save()
        
        client.close()
        messages.success(request, f"Test mis à jour avec succès ! Statut: {test.get_status_display()}")
        return redirect('evaluation:teacher_dashboard')
    
    # Récupérer les questions du test
    questions = test.questions.all().order_by('order')
    
    client.close()
    
    context = {
        'test': test,
        'questions': questions,
        'tags_str': ', '.join(test.tags) if test.tags else '',
        'skills_str': ', '.join(test.skills_tested) if test.skills_tested else '',
    }
    return render(request, 'evaluation/teacher/edit_test.html', context)


@login_required
def add_question(request, test_id):
    """
    Ajouter une question à un test
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({
            '_id': ObjectId(test_id),
            'created_by_id': request.user.id
        })
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé")
            return redirect('evaluation:teacher_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:teacher_dashboard')
    
    if request.method == 'POST':
        question_data = {
            'question_text': request.POST.get('question_text'),
            'question_type': request.POST.get('question_type'),
            'points': float(request.POST.get('points', 1.0)),
            'order': int(request.POST.get('order', 0)),
            'difficulty_level': request.POST.get('difficulty_level', 'medium'),
            'explanation': request.POST.get('explanation', ''),
            'hint': request.POST.get('hint', ''),
        }
        
        # Gérer les options pour QCM
        if question_data['question_type'] == 'mcq':
            options = []
            option_count = int(request.POST.get('option_count', 4))
            
            for i in range(option_count):
                option_text = request.POST.get(f'option_{i}_text')
                is_correct = request.POST.get(f'option_{i}_correct') == 'on'
                
                if option_text:
                    options.append({
                        'id': chr(65 + i),  # A, B, C, D...
                        'text': option_text,
                        'is_correct': is_correct
                    })
            
            question_data['options'] = options
        
        # Gérer la réponse correcte pour vrai/faux et réponse courte
        elif question_data['question_type'] in ['true_false', 'short_answer']:
            question_data['correct_answer'] = request.POST.get('correct_answer')
        
        # Gérer les compétences
        skills_str = request.POST.get('skills', '')
        question_data['skills'] = [s.strip() for s in skills_str.split(',') if s.strip()]
        
        # Créer la question
        question = TestService.add_question_to_test(test, question_data)
        
        client.close()
        messages.success(request, "Question ajoutée avec succès !")
        return redirect('evaluation:edit_test', test_id=test.id)
    
    client.close()
    
    context = {
        'test': test,
        'next_order': test.questions.count()
    }
    return render(request, 'evaluation/teacher/add_question.html', context)


@login_required
def test_statistics(request, test_id):
    """
    Voir les statistiques d'un test
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({
            '_id': ObjectId(test_id),
            'created_by_id': request.user.id
        })
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé")
            return redirect('evaluation:teacher_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:teacher_dashboard')
    
    # Récupérer les statistiques
    stats = TestService.get_test_statistics(test)
    
    # Récupérer les soumissions
    submissions = Submission.objects.filter(
        test=test, 
        status='graded'
    ).select_related('student').order_by('-submitted_at')
    
    client.close()
    
    context = {
        'test': test,
        'stats': stats,
        'submissions': submissions
    }
    return render(request, 'evaluation/teacher/test_statistics.html', context)


# ============================================
# Vues pour les Étudiants
# ============================================

@login_required
def student_dashboard(request):
    """
    Tableau de bord étudiant complet avec analytics et gamification.
    
    Affiche:
    - Scores obtenus et statistiques détaillées
    - Temps d'étude et progression
    - Matières faibles identifiées
    - Recommandations personnalisées par IA
    - Badges et classements (gamification)
    """
    from .analytics import StudentAnalytics, update_student_profile_with_recommendations
    from .gamification import GamificationService
    
    # 1. RÉCUPÉRER OU CRÉER LE PROFIL
    try:
        # Essayer de récupérer le profil existant
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if not profile:
            # Créer un nouveau profil s'il n'existe pas
            profile = UserProfile.objects.create(
                user=request.user,
                role='student'
            )
            created = True
            print(f"✅ Nouveau profil créé pour {request.user.username}")
        else:
            created = False
            print(f"✅ Profil existant trouvé pour {request.user.username}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération/création du profil: {e}")
        # Créer un profil de secours
        profile = UserProfile.objects.create(
            user=request.user,
            role='student'
        )
        created = True
    
    # 2. GÉNÉRATION DES ANALYTICS COMPLÈTES
    # Service d'analytics pour statistiques détaillées
    analytics_service = StudentAnalytics(profile)
    analytics_data = analytics_service.get_complete_statistics()
    
    # 3. GÉNÉRATION DES RECOMMANDATIONS IA
    # Mettre à jour le profil avec les dernières recommandations
    if analytics_data['metadata']['total_tests'] > 0:
        recommendations = update_student_profile_with_recommendations(profile)
    else:
        recommendations = []
    
    # 4. GAMIFICATION - Badges et Niveaux
    gamification_service = GamificationService(profile)
    
    # Vérifier et attribuer les nouveaux badges (désactivé temporairement pour djongo)
    new_badges = []  # gamification_service.check_and_award_badges()
    
    # Informations de niveau
    level_info = gamification_service.get_level_info()
    
    # Classements
    leaderboard_all_time = gamification_service.get_leaderboard(period='all_time', limit=10)
    leaderboard_weekly = gamification_service.get_leaderboard(period='weekly', limit=5)
    student_rank = gamification_service.get_student_rank(period='all_time')
    
    # 5. TESTS DISPONIBLES ET EN COURS
    available_tests = TestService.get_student_available_tests(request.user)
    
    # 5.1 RÉCUPÉRER AUSSI LES EXERCISESETS IA PUBLIÉS
    from pymongo import MongoClient
    from django.conf import settings
    
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        # Récupérer les ExerciseSets publiés (tests IA)
        ai_exercise_sets_data = list(db.exercise_sets.find({'status': 'published'}).sort('published_at', -1).limit(10))
        
        # Récupérer les IDs des sets déjà complétés par l'étudiant
        completed_submissions = db.student_exercise_submissions.find({
            'student_id': request.user.id,
            'status': 'completed'
        })
        completed_set_ids = [str(sub.get('exercise_set_id', '')) for sub in completed_submissions]
        
        # Créer une liste d'objets pour le template
        ai_exercise_sets = []
        for set_data in ai_exercise_sets_data:
            ai_exercise_sets.append({
                'id': str(set_data['_id']),
                'title': set_data.get('title', 'Sans titre'),
                'description': set_data.get('description', ''),
                'exercise_count': db.exercise_generator_exerciseset_exercises.count_documents({
                    'exerciseset_id': str(set_data['_id'])
                }),
                'is_completed': str(set_data['_id']) in completed_set_ids,
                'published_at': set_data.get('published_at'),
                'teacher_name': 'IA Generator'  # Vous pouvez récupérer le vrai nom du prof si nécessaire
            })
        
        client.close()
    except Exception as e:
        print(f"Erreur récupération ExerciseSets: {e}")
        ai_exercise_sets = []
    
    # Tests en cours (non terminés)
    in_progress_submissions = Submission.objects.filter(
        student=request.user,
        status='in_progress'
    ).select_related('test').order_by('-started_at')
    
    # Résultats récents (5 derniers)
    recent_results = Result.objects.filter(
        student=request.user
    ).select_related('test').order_by('-created_at')[:5]
    
    # 6. ALERTES ET NOTIFICATIONS
    alerts = []
    
    # Alerte si baisse de performances
    if analytics_data['progression']['trend'] == 'declining':
        alerts.append({
            'type': 'warning',
            'message': f"Vos scores ont baissé de {abs(analytics_data['progression']['improvement'])}% récemment.",
            'icon': 'exclamation-triangle'
        })
    
    # Alerte pour matières faibles
    if analytics_data['weaknesses']:
        weak_subjects = ', '.join([w['subject'] for w in analytics_data['weaknesses'][:2]])
        alerts.append({
            'type': 'info',
            'message': f"Matières à travailler : {weak_subjects}",
            'icon': 'book'
        })
    
    # Notification pour nouveaux badges
    if new_badges:
        for badge in new_badges:
            alerts.append({
                'type': 'success',
                'message': f"Nouveau badge obtenu : {badge['icon']} {badge['name']} !",
                'icon': 'trophy'
            })
    
    # 7. CONSTRUCTION DU CONTEXTE
    context = {
        # Profil étudiant
        'profile': profile,
        
        # Analytics détaillées
        'analytics': analytics_data,
        'scores_stats': analytics_data['scores'],
        'study_time': analytics_data['study_time'],
        'progression': analytics_data['progression'],
        'subjects_performance': analytics_data['subjects'],
        
        # Points forts/lacunes depuis UserProfile (mis à jour par analyze_student_strengths)
        'strengths': profile.strengths or [],  # Utiliser les données du profil au lieu d'analytics
        'weaknesses': profile.weaknesses or [],  # Utiliser les données du profil au lieu d'analytics
        
        # Recommandations IA
        'recommendations': recommendations[:6],  # Top 6 recommandations
        'has_recommendations': len(recommendations) > 0,
        
        # Gamification
        'level_info': level_info,
        'badges': profile.badges or [],
        'new_badges': new_badges,
        'total_badges': len(profile.badges or []),
        'leaderboard_all_time': leaderboard_all_time,
        'leaderboard_weekly': leaderboard_weekly,
        'student_rank': student_rank,
        
        # Tests et résultats
        'available_tests': available_tests[:6],  # Top 6 tests disponibles
        'ai_exercise_sets': ai_exercise_sets,  # Tests IA (ExerciseSets)
        'in_progress_submissions': in_progress_submissions,
        'recent_results': recent_results,
        'pending_tests': len(available_tests) + len(ai_exercise_sets),  # Total tests + exerciseSets
        
        # Alertes
        'alerts': alerts,
        
        # Métadonnées
        'has_activity': analytics_data['metadata']['total_tests'] > 0,
        'is_new_student': created or analytics_data['metadata']['total_tests'] == 0,
    }
    
    # AJOUTER LES STATISTIQUES DES TESTS IA
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        # Récupérer toutes les soumissions IA de l'étudiant
        ai_submissions = list(db.student_exercise_submissions.find({
            'student_id': request.user.id,
            'status': 'completed'
        }))
        
        if len(ai_submissions) > 0:
            # Calculer les stats IA
            ai_total_tests = len(ai_submissions)
            ai_scores = [s.get('score', 0) for s in ai_submissions]
            ai_average_score = sum(ai_scores) / len(ai_scores) if ai_scores else 0
            ai_tests_passed = sum(1 for s in ai_submissions if s.get('score', 0) >= 60)
            
            # Combiner avec les stats manuelles
            manual_total_tests = analytics_data['metadata']['total_tests']
            manual_average_score = analytics_data['scores'].get('average', 0)
            
            combined_total_tests = manual_total_tests + ai_total_tests
            combined_average_score = ((manual_average_score * manual_total_tests) + (ai_average_score * ai_total_tests)) / combined_total_tests if combined_total_tests > 0 else 0
            combined_tests_passed = analytics_data['metadata'].get('tests_passed', 0) + ai_tests_passed
            
            # Ajouter au contexte
            context['combined_stats'] = {
                'total_tests': combined_total_tests,
                'average_score': combined_average_score,
                'tests_passed': combined_tests_passed,
                'manual_tests': manual_total_tests,
                'ai_tests': ai_total_tests,
                'has_ai_tests': ai_total_tests > 0
            }
            
            # NOUVELLE PARTIE: Ajouter les tests IA aux performances par matière
            from bson.objectid import ObjectId
            from collections import defaultdict
            
            # Grouper les submissions IA par matière
            ai_performance_by_subject = defaultdict(list)
            
            for submission in ai_submissions:
                set_id = submission.get('exercise_set_id')
                if set_id:
                    set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
                    if set_data:
                        # Récupérer le sujet depuis le CourseDocument
                        subject = 'Général'
                        source_doc_id = set_data.get('source_document_id')
                        if source_doc_id:
                            try:
                                doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                                if doc_data and doc_data.get('subject'):
                                    subject = doc_data.get('subject').capitalize()
                            except:
                                pass
                        
                        ai_performance_by_subject[subject].append(submission.get('score', 0))
            
            # Fusionner avec les performances manuelles
            combined_subjects = dict(analytics_data['subjects'])  # Copier les données manuelles
            
            for subject, scores in ai_performance_by_subject.items():
                if subject in combined_subjects:
                    # Fusionner avec les scores existants
                    existing_avg = combined_subjects[subject]['average']
                    existing_count = combined_subjects[subject]['count']
                    
                    ai_avg = sum(scores) / len(scores)
                    ai_count = len(scores)
                    
                    # Recalculer la moyenne combinée
                    combined_avg = ((existing_avg * existing_count) + (ai_avg * ai_count)) / (existing_count + ai_count)
                    
                    combined_subjects[subject]['average'] = combined_avg
                    combined_subjects[subject]['count'] += ai_count
                    combined_subjects[subject]['last_score'] = scores[-1]  # Dernier score IA
                else:
                    # Nouvelle matière (seulement des tests IA)
                    combined_subjects[subject] = {
                        'average': sum(scores) / len(scores),
                        'count': len(scores),
                        'last_score': scores[-1],
                        'trend': 'stable',
                        'tests': []
                    }
            
            # Remplacer les performances par matière dans le contexte
            context['analytics']['subjects'] = combined_subjects
            context['subjects_performance'] = combined_subjects
            
        else:
            # Pas de tests IA
            context['combined_stats'] = {
                'total_tests': analytics_data['metadata'].get('total_tests', 0),
                'average_score': analytics_data['scores'].get('average', 0),
                'tests_passed': analytics_data['metadata'].get('tests_passed', 0),
                'manual_tests': analytics_data['metadata'].get('total_tests', 0),
                'ai_tests': 0,
                'has_ai_tests': False
            }
        
        client.close()
    except Exception as e:
        print(f"Erreur calcul stats IA: {e}")
        # Fallback aux stats manuelles uniquement
        context['combined_stats'] = {
            'total_tests': analytics_data['metadata'].get('total_tests', 0),
            'average_score': analytics_data['scores'].get('average', 0),
            'tests_passed': analytics_data['metadata'].get('tests_passed', 0),
            'manual_tests': analytics_data['metadata'].get('total_tests', 0),
            'ai_tests': 0,
            'has_ai_tests': False
        }
    
    return render(request, 'evaluation/student/dashboard.html', context)


@login_required
def test_detail(request, test_id):
    """
    Détails d'un test (avant de le commencer)
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({
            '_id': ObjectId(test_id),
            'status': 'published'
        })
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé ou non publié")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    # Vérifier si l'étudiant a déjà une soumission en cours
    existing_submission = Submission.objects.filter(
        student=request.user,
        test=test,
        status='in_progress'
    ).first()
    
    # Récupérer les tentatives précédentes et leurs résultats
    user_results = Result.objects.filter(
        submission__student=request.user,
        submission__test=test,
        submission__status='graded'
    ).order_by('-created_at')
    
    # Compter le nombre de tentatives
    user_attempts = user_results.count()
    
    # Compter les types de questions
    from collections import Counter
    question_types = Counter()
    for question in test.questions.all():
        question_types[question.get_question_type_display()] += 1
    
    client.close()
    
    context = {
        'test': test,
        'existing_submission': existing_submission,
        'user_results': user_results,
        'user_attempts': user_attempts,
        'question_types': dict(question_types),
        'can_start': True
    }
    return render(request, 'evaluation/student/test_detail_modern.html', context)


@login_required
def start_test(request, test_id):
    """
    Démarrer un test
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({
            '_id': ObjectId(test_id),
            'status': 'published'
        })
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé ou non publié")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    # Vérifier s'il y a déjà une soumission en cours
    existing_submission = Submission.objects.filter(
        student=request.user,
        test=test,
        status='in_progress'
    ).first()
    
    if existing_submission:
        return redirect('evaluation:take_test', submission_id=existing_submission.id)
    
    # Créer une nouvelle soumission
    submission = TestService.start_test(request.user, test)
    
    messages.success(request, f"Test '{test.title}' démarré. Bonne chance !")
    return redirect('evaluation:take_test', submission_id=submission.id)


@login_required
def take_test(request, submission_id):
    """
    Interface de passage du test
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer la soumission via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        submission_data = db.submissions.find_one({
            '_id': ObjectId(submission_id),
            'student_id': request.user.id,
            'status': 'in_progress'
        })
        
        if not submission_data:
            client.close()
            messages.error(request, "Soumission non trouvée")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django de la soumission
        submission_id_obj = submission_data.pop('_id', None)
        submission = Submission(**{k: v for k, v in submission_data.items() if k != '_id'})
        submission.pk = submission_id_obj
        submission.id = submission_id_obj
        submission._state.adding = False
        submission._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    test = submission.test
    questions = test.questions.all().order_by('order')
    
    # Calculer le temps restant
    elapsed_time = (timezone.now() - submission.started_at).total_seconds()
    time_limit = test.duration * 60  # Convertir en secondes
    time_remaining = max(0, time_limit - elapsed_time) if test.is_timed else None
    
    context = {
        'submission': submission,
        'test': test,
        'questions': questions,
        'time_remaining': time_remaining,
        'current_answers': submission.answers or {}
    }
    return render(request, 'evaluation/student/take_test.html', context)


@login_required
@require_http_methods(["POST"])
def submit_test(request, submission_id):
    """
    Soumettre un test complété
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer la soumission via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        submission_data = db.submissions.find_one({
            '_id': ObjectId(submission_id),
            'student_id': request.user.id,
            'status': 'in_progress'
        })
        
        if not submission_data:
            client.close()
            messages.error(request, "Soumission non trouvée")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django de la soumission
        submission_id_obj = submission_data.pop('_id', None)
        submission = Submission(**{k: v for k, v in submission_data.items() if k != '_id'})
        submission.pk = submission_id_obj
        submission.id = submission_id_obj
        submission._state.adding = False
        submission._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    # Récupérer les réponses depuis le POST
    answers = {}
    test = submission.test
    
    for question in test.questions.all():
        answer_key = f'question_{question.id}'
        answer_value = request.POST.get(answer_key)
        
        if answer_value:
            answers[str(question.id)] = {
                'answer': answer_value,
                'time_spent': 0  # À améliorer avec tracking JS
            }
    
    # Soumettre le test et obtenir les résultats
    grading_results = TestService.submit_test(submission, answers)
    
    # Créer un résultat détaillé
    result = ResultService.create_detailed_result(submission, grading_results)
    
    # Mettre à jour le profil de l'étudiant
    ResultService.update_user_profile_stats(request.user, result)
    
    # Générer un feedback IA complet
    try:
        from .ai_feedback import AIFeedbackGenerator
        
        ai_feedback = AIFeedbackGenerator.generate_comprehensive_feedback(result, submission)
        
        # Mettre à jour le résultat avec le feedback IA
        result.ai_analysis = ai_feedback
        result.recommendations = ai_feedback.get('recommendations', [])
        result.learning_gaps = ai_feedback.get('weaknesses', [])
        result.save()
        
        print(f"✓ Feedback IA généré: {len(ai_feedback.get('recommendations', []))} recommandations")
    except Exception as e:
        print(f"Erreur génération feedback IA: {e}")
        import traceback
        traceback.print_exc()
    
    messages.success(request, "Test soumis avec succès ! Découvrez vos résultats.")
    return redirect('evaluation:view_result', result_id=result.id)


@login_required
def view_result(request, result_id):
    """
    Voir les résultats d'un test
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le résultat via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        result_data = db.results.find_one({
            '_id': ObjectId(result_id),
            'student_id': request.user.id
        })
        
        if not result_data:
            client.close()
            messages.error(request, "Résultat non trouvé")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du résultat
        result_id_obj = result_data.pop('_id', None)
        result = Result(**{k: v for k, v in result_data.items() if k != '_id'})
        result.pk = result_id_obj
        result.id = result_id_obj
        result._state.adding = False
        result._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    submission = result.submission
    test = result.test
    
    # Récupérer les questions avec les réponses
    questions_with_answers = []
    for question in test.questions.all().order_by('order'):
        answer_data = submission.answers.get(str(question.id), {})
        # Gérer le cas où answer_data est une string au lieu d'un dict
        if isinstance(answer_data, str):
            answer_data = {'answer': answer_data}
        elif not isinstance(answer_data, dict):
            answer_data = {}
        
        questions_with_answers.append({
            'question': question,
            'student_answer': answer_data.get('answer'),
            'is_correct': answer_data.get('is_correct'),
            'feedback': answer_data.get('feedback'),
            'points_earned': answer_data.get('points_earned', 0)
        })
    
    context = {
        'result': result,
        'submission': submission,
        'test': test,
        'questions_with_answers': questions_with_answers,
    }
    return render(request, 'evaluation/student/view_result.html', context)


@login_required
def student_progress(request):
    """
    Page de progression détaillée de l'étudiant.
    
    Affiche:
    - Graphiques de progression dans le temps
    - Performances par matière avec tendances
    - Analyse détaillée des points faibles par IA
    - Recommandations d'apprentissage
    - Historique complet des résultats
    INCLUT LES TESTS MANUELS ET LES TESTS IA
    """
    from .analytics import StudentAnalytics
    from .gamification import GamificationService
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    from collections import defaultdict
    from datetime import timedelta
    from .utils import get_or_create_user_profile_safe
    
    # Récupérer le profil de manière sécurisée (gère les duplicatas)
    profile = get_or_create_user_profile_safe(request.user)
    
    # 1. GÉNÉRATION DES ANALYTICS COMPLÈTES (TESTS MANUELS)
    analytics_service = StudentAnalytics(profile)
    analytics_data = analytics_service.get_complete_statistics()
    
    # 2. RÉCUPÉRER LES RÉSULTATS MANUELS (LIMITÉS POUR ÉCONOMISER LA MÉMOIRE)
    # ⚠️ Sur Render free tier (512MB RAM), on limite à 50 résultats max
    all_manual_results = Result.objects.filter(
        student=request.user
    ).select_related('test').order_by('-created_at')[:50]  # 🔥 LIMITE AJOUTÉE
    
    # 2.1 RÉCUPÉRER LES RÉSULTATS IA (LIMITÉS)
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    # 🔥 LIMITER à 30 soumissions les plus récentes pour économiser la RAM
    ai_submissions = list(db.student_exercise_submissions.find({
        'student_id': request.user.id,
        'status': 'completed'
    }).sort('submitted_at', -1).limit(30))  # 🔥 LIMITE AJOUTÉE
    
    # Récupérer les infos des ExerciseSets pour les soumissions IA
    ai_results_with_details = []
    for submission in ai_submissions:
        set_id = submission.get('exercise_set_id')
        if set_id:
            set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
            if set_data:
                # Récupérer le vrai subject depuis le CourseDocument
                subject = 'Général'  # Fallback par défaut
                source_doc_id = set_data.get('source_document_id')
                if source_doc_id:
                    try:
                        doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                        if doc_data and doc_data.get('subject'):
                            subject = doc_data.get('subject').capitalize()
                    except:
                        pass
                
                # 🔥 NOUVEAU : Récupérer les détails des questions pour l'analyse
                # ⚠️ OPTIMISÉ : Ne charger que si moins de 20 questions pour économiser RAM
                questions_details = []
                try:
                    # Récupérer les IDs des exercices du set
                    exercise_ids = list(db.exercise_generator_exerciseset_exercises.find({
                        'exerciseset_id': str(set_id)
                    }).limit(20))  # 🔥 LIMITE: Max 20 exercices par set
                    
                    exercise_id_list = [ex['generatedexercise_id'] for ex in exercise_ids]
                    
                    # Ne charger que si pas trop d'exercices
                    if len(exercise_id_list) <= 20:
                        # Récupérer les exercices complets (projection pour réduire la taille)
                        exercises_data = list(db.generated_exercises.find(
                            {
                                '_id': {'$in': [ObjectId(eid) if isinstance(eid, str) else eid for eid in exercise_id_list]}
                            },
                            {
                                '_id': 1, 'concept': 1, 'topic': 1, 'difficulty': 1, 
                                'exercise_type': 1, 'question_text': 1, 'options_data': 1
                            }  # 🔥 PROJECTION: Ne charger que les champs nécessaires
                        ))
                        
                        # Récupérer les réponses de l'étudiant
                        answers = submission.get('answers', {})
                        
                        # Créer les détails pour chaque question
                        for ex_data in exercises_data:
                            exercise_id = str(ex_data['_id'])
                            
                            # Extraire le concept/topic
                            concept = ex_data.get('concept') or ex_data.get('topic') or subject or 'Général'
                            
                            # Si le concept est trop générique, essayer d'extraire du texte de la question
                            if concept in ['Général', 'General', '']:
                                question_text = ex_data.get('question_text', '')
                                # 🔥 OPTIMISÉ: Ne pas appeler la fonction si pas nécessaire
                                concept = question_text[:30] if question_text else subject
                            
                            # Vérifier si la réponse est correcte
                            student_answer = answers.get(exercise_id)
                            options_data = ex_data.get('options_data', {})
                            correct_answer = options_data.get('correct')
                            exercise_type = ex_data.get('exercise_type')
                            
                            is_correct = False
                            if exercise_type == 'true_false':
                                student_bool = (student_answer == 'True' or student_answer == 'true')
                                is_correct = (correct_answer == student_bool)
                            else:
                                is_correct = (str(student_answer) == str(correct_answer)) if correct_answer else False
                            
                            # Ajouter les détails de la question
                            questions_details.append({
                                'topic': concept,
                                'difficulty': ex_data.get('difficulty', 'medium'),
                                'is_correct': is_correct,
                                'question_type': exercise_type or 'multiple_choice'
                            })
                except Exception as e:
                    print(f"⚠️ Erreur récupération questions_details pour set {set_id}: {e}")
                
                ai_results_with_details.append({
                    'submission': submission,
                    'set_data': set_data,
                    'score': submission.get('score', 0),
                    'submitted_at': submission.get('submitted_at'),
                    'subject': subject,
                    'questions_details': questions_details,  # ⭐ AJOUTÉ
                    'exercise_set_name': set_data.get('title', 'Test IA')  # ⭐ AJOUTÉ
                })
    
    # NE PAS FERMER LE CLIENT ICI - il sera utilisé plus tard pour l'analyse par concepts
    # client.close() sera appelé à la fin de la fonction
    
    # 3. COMBINER LES RÉSULTATS MANUELS ET IA POUR L'HISTORIQUE
    # Créer une liste unifiée pour le tableau
    all_combined_results = []
    
    # Ajouter les résultats manuels
    for result in all_manual_results:
        all_combined_results.append({
            'type': 'manual',
            'date': result.created_at,
            'title': result.test.title,
            'subject': result.test.subject or 'Général',
            'score': result.percentage_score,
            'result_obj': result,
            'test_id': result.test.id
        })
    
    # Ajouter les résultats IA
    for ai_result in ai_results_with_details:
        # Assurer que la date est timezone-aware
        submitted_at = ai_result['submitted_at']
        if submitted_at and timezone.is_naive(submitted_at):
            submitted_at = timezone.make_aware(submitted_at)
        elif not submitted_at:
            submitted_at = timezone.now()
        
        # Calculer le score en points (comme les tests manuels)
        submission = ai_result['submission']
        total_count = submission.get('total_count', 0)
        correct_count = submission.get('correct_count', 0)
        score_percentage = ai_result['score']
        
        # Score sur 100 points
        total_score = (score_percentage / 100) * total_count if total_count > 0 else 0
        
        # Calculer la note (grade) comme dans TestResult.assign_grade()
        if score_percentage >= 90:
            grade = 'A+'
        elif score_percentage >= 85:
            grade = 'A'
        elif score_percentage >= 80:
            grade = 'B+'
        elif score_percentage >= 75:
            grade = 'B'
        elif score_percentage >= 70:
            grade = 'C+'
        elif score_percentage >= 65:
            grade = 'C'
        elif score_percentage >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        all_combined_results.append({
            'type': 'ai',
            'date': submitted_at,
            'title': ai_result['set_data'].get('title', 'Test IA'),
            'subject': ai_result['subject'],
            'score': score_percentage,
            'total_score': round(total_score, 1),  # Score obtenu en points
            'total_points': total_count,  # Total de questions
            'correct_count': correct_count,
            'grade': grade,  # Note lettre
            'set_id': str(ai_result['set_data']['_id']),
            'submission': ai_result['submission']
        })
    
    # Trier par date décroissante
    all_combined_results.sort(key=lambda x: x['date'], reverse=True)
    
    # 4. PERFORMANCES PAR MATIÈRE (COMBINÉES)
    performance_by_subject = {}
    
    # Ajouter performances manuelles
    for subject, data in analytics_data['subjects'].items():
        performance_by_subject[subject] = {
            'avg_score': data['average'],
            'count': data['count'],
            'trend': data['trend'],
            'last_score': data['last_score'],
            'tests': data['tests'],
            'scores': []  # Pour recalculer
        }
        # Récupérer les scores individuels
        for test_data in data['tests']:
            performance_by_subject[subject]['scores'].append(test_data['score'])
    
    # Ajouter performances IA
    for ai_result in ai_results_with_details:
        subject = ai_result['subject']
        if subject not in performance_by_subject:
            performance_by_subject[subject] = {
                'avg_score': 0,
                'count': 0,
                'trend': 'stable',
                'last_score': 0,
                'tests': [],
                'scores': []
            }
        
        performance_by_subject[subject]['scores'].append(ai_result['score'])
        performance_by_subject[subject]['count'] += 1
    
    # Recalculer les moyennes
    for subject in performance_by_subject:
        scores = performance_by_subject[subject]['scores']
        if scores:
            performance_by_subject[subject]['avg_score'] = sum(scores) / len(scores)
            performance_by_subject[subject]['last_score'] = scores[-1] if scores else 0
    
    # 5. ANALYSER LES FAIBLESSES AVEC IA (OLD - kept for compatibility)
    # ⚠️ DÉSACTIVÉ temporairement pour économiser RAM sur Render free tier
    weaknesses_analysis = None
    if False and all_manual_results.count() >= 2:  # 🔥 DÉSACTIVÉ avec False
        try:
            ai_services = get_ai_services()
            # Prendre les 10 derniers APRÈS le tri
            recent_results = all_manual_results[:10]  # Déjà trié par -created_at
            weaknesses_analysis = ai_services['weakness_analyzer'].identify_weaknesses(
                profile, list(recent_results)
            )
        except Exception as e:
            print(f"⚠️ Erreur analyse faiblesses IA: {e}")
    
    # Utiliser l'analyse locale (moins gourmande)
    if not weaknesses_analysis:
        weaknesses_analysis = {
            'weaknesses': analytics_data['weaknesses'],
            'strengths': analytics_data['strengths'],
            'recommendations': profile.ai_recommendations or []
        }
    
    # 5.1 NOUVELLE ANALYSE PAR CONCEPTS (DÉTAILLÉE) - OPTIMISÉE
    from .concept_analysis import ConceptAnalysisService
    
    concept_analyzer = ConceptAnalysisService(request.user, db_connection=db)
    
    # Analyser séparément les tests manuels et IA
    print(f"🔍 DEBUG: all_manual_results count = {len(all_manual_results)}")
    manual_concept_insights = concept_analyzer.analyze_test_results(all_manual_results)
    print(f"🔍 DEBUG: manual_concept_insights = {manual_concept_insights}")
    print(f"🔍 DEBUG: manual_concept_insights keys = {manual_concept_insights.keys() if manual_concept_insights else 'EMPTY'}")
    
    ai_concept_insights = concept_analyzer.analyze_ai_test_results(ai_submissions)
    print(f"🔍 DEBUG: ai_concept_insights = {ai_concept_insights}")
    
    # Également garder l'analyse combinée
    concept_insights = concept_analyzer.get_combined_analysis(
        all_manual_results,  # Tests manuels
        ai_submissions  # Tests IA
    )
    
    # 5.2 ANALYSE IA AVANCÉE AVEC MODÈLE PUISSANT (Mistral-7B-Instruct-v0.2)
    # ⚠️ DÉSACTIVÉ temporairement pour économiser RAM sur Render free tier
    manual_tests_for_ai = []
    ai_tests_for_ai = []
    
    # Le code d'analyse IA avancée est désactivé pour économiser la RAM
    # Sur Render free tier (512MB), ces analyses consomment trop de mémoire
    
    # Effectuer l'analyse IA par batch (plus efficace)
    # ⚠️ DÉSACTIVÉ temporairement pour économiser RAM sur Render free tier
    manual_ai_analysis = {}
    ai_tests_ai_analysis = {}
    # Les analyses IA avancées sont désactivées pour le tier gratuit de Render
    
    # 6. GAMIFICATION
    gamification_service = GamificationService(profile)
    
    # ✅ VÉRIFIER ET ATTRIBUER LES BADGES
    try:
        new_badges = gamification_service.check_and_award_badges()
        if new_badges:
            print(f"🎉 Nouveaux badges obtenus: {[b['name'] for b in new_badges]}")
    except Exception as e:
        print(f"❌ Erreur attribution badges: {e}")
        new_badges = []
    
    # ✅ OBTENIR LA PROGRESSION DE TOUS LES BADGES
    try:
        badge_progress_data = gamification_service.get_badge_progress()
    except Exception as e:
        print(f"❌ Erreur progression badges: {e}")
        badge_progress_data = {
            'earned_badges': [],
            'available_badges': []
        }
    
    level_info = gamification_service.get_level_info()
    student_rank = gamification_service.get_student_rank(period='all_time')
    
    # 7. PRÉPARER LES DONNÉES POUR LES GRAPHIQUES (COMBINÉS)
    # Données de progression temporelle (pour Chart.js)
    progression_data_combined = []
    
    # Ajouter tests manuels - avec protection contre KeyError
    progression_data = analytics_data.get('progression', {}).get('progression_data', [])
    for p in progression_data:
        progression_data_combined.append({
            'date': p.get('date', ''),
            'score': p.get('score', 0),
            'test_name': p.get('test_name', 'Test'),
            'type': 'manual'
        })
    
    # Ajouter tests IA
    for ai_result in ai_results_with_details:
        progression_data_combined.append({
            'date': ai_result['submitted_at'].strftime('%d/%m') if ai_result['submitted_at'] else '',
            'score': ai_result['score'],
            'test_name': ai_result['set_data'].get('title', 'Test IA'),
            'type': 'ai'
        })
    
    # Trier par date
    progression_data_combined.sort(key=lambda x: x['date'])
    
    # Calculer moyenne mobile
    for i, item in enumerate(progression_data_combined):
        window = progression_data_combined[max(0, i-2):i+1]
        item['moving_average'] = sum(d['score'] for d in window) / len(window)
    
    progression_chart_data = {
        'labels': [p['date'] for p in progression_data_combined],
        'scores': [p['score'] for p in progression_data_combined],
        'moving_average': [p['moving_average'] for p in progression_data_combined],
        'test_names': [p['test_name'] for p in progression_data_combined]
    }
    
    # Données par matière (pour Chart.js)
    subjects_chart_data = {
        'subjects': list(performance_by_subject.keys()),
        'averages': [data['avg_score'] for data in performance_by_subject.values()],
        'colors': [
            '#27ae60' if avg >= 75 else '#f39c12' if avg >= 60 else '#e74c3c'
            for avg in [data['avg_score'] for data in performance_by_subject.values()]
        ]
    }
    
    # 7. TEMPS D'ÉTUDE PAR SEMAINE (pour graphique)
    study_sessions = analytics_data.get('study_time', {}).get('sessions', [])
    # Grouper par semaine
    from collections import defaultdict
    from datetime import timedelta
    
    weekly_study_time = defaultdict(float)
    for session in study_sessions:
        # Trouver le début de la semaine
        session_date = session.get('date')
        session_duration = session.get('duration', 0)
        if session_date:
            week_start = session_date - timedelta(days=session_date.weekday())
            weekly_study_time[week_start.strftime('%Y-%m-%d')] += session_duration
    
    study_time_chart_data = {
        'weeks': sorted(weekly_study_time.keys()),
        'hours': [round(weekly_study_time[week] / 60, 2) for week in sorted(weekly_study_time.keys())]
    }
    
    # 8. PRÉPARER DONNÉES STRUCTURÉES POUR FAIBLESSES/FORCES (COMBINÉS)
    # Analyser les performances combinées (manuels + IA)
    
    strong_areas = {}
    weak_areas = {}
    
    # Analyser par matière en utilisant performance_by_subject (déjà combiné)
    for subject, data in performance_by_subject.items():
        if data['avg_score'] >= 70:
            # Point fort
            strong_areas[subject] = {
                'total': data['count'],
                'correct': data['count'],
                'score': data['avg_score'],
                'description': f"Excellente performance en {subject} (moyenne {data['avg_score']:.1f}%)"
            }
        else:
            # Point faible
            weak_areas[subject] = {
                'total': data['count'],
                'correct': 0,
                'score': data['avg_score'],
                'description': f"À améliorer en {subject} (moyenne {data['avg_score']:.1f}%)"
            }
    
    # Si toujours vide, utiliser profile.strengths/weaknesses
    if not strong_areas and not weak_areas:
        if profile.strengths:
            for i, strength in enumerate(profile.strengths, 1):
                strong_areas[f"Force {i}"] = {
                    'total': 1,
                    'correct': 1,
                    'score': 100,
                    'description': strength
                }
        
        if profile.weaknesses:
            for i, weakness in enumerate(profile.weaknesses, 1):
                weak_areas[f"Lacune {i}"] = {
                    'total': 1,
                    'correct': 0,
                    'score': 40,
                    'description': weakness
                }
    
    # 9. GÉNÉRER RECOMMANDATIONS SI VIDES
    if not profile.ai_recommendations or len(profile.ai_recommendations) == 0:
        recommendations = [
            {
                'title': 'Pratiquez régulièrement',
                'message': 'Effectuez au moins 3 tests par semaine pour maintenir vos compétences et progresser régulièrement.'
            },
            {
                'title': 'Revoyez vos erreurs',
                'message': 'Après chaque test, prenez le temps d\'analyser vos erreurs pour éviter de les répéter.'
            },
            {
                'title': 'Concentrez-vous sur vos points faibles',
                'message': 'Identifiez vos lacunes et travaillez spécifiquement sur ces sujets pour équilibrer vos compétences.'
            },
            {
                'title': 'Variez les matières',
                'message': 'Testez-vous sur différentes matières pour développer une expertise complète et polyvalente.'
            },
            {
                'title': 'Fixez-vous des objectifs',
                'message': 'Définissez des objectifs de score précis (ex: atteindre 80% en React) pour rester motivé.'
            },
            {
                'title': 'Utilisez les ressources complémentaires',
                'message': 'Consultez la documentation officielle et les tutoriels pour approfondir vos connaissances.'
            }
        ]
        profile.ai_recommendations = recommendations
        profile.save()
    
    # 10. CONSTRUCTION DU CONTEXTE AVEC DONNÉES COMBINÉES
    
    # Calculer les statistiques combinées
    total_tests_combined = all_manual_results.count() + len(ai_submissions)
    
    # Calculer score moyen combiné
    manual_total = all_manual_results.count()
    manual_avg = analytics_data['scores'].get('average', 0)
    ai_total = len(ai_submissions)
    ai_avg = sum(s.get('score', 0) for s in ai_submissions) / ai_total if ai_total > 0 else 0
    
    if total_tests_combined > 0:
        combined_average_score = ((manual_avg * manual_total) + (ai_avg * ai_total)) / total_tests_combined
    else:
        combined_average_score = 0
    
    # Calculer tendance combinée
    if len(progression_data_combined) >= 3:
        recent_scores = [p['score'] for p in progression_data_combined[-3:]]
        old_scores = [p['score'] for p in progression_data_combined[:3]]
        if old_scores and recent_scores:
            improvement = (sum(recent_scores) / len(recent_scores)) - (sum(old_scores) / len(old_scores))
        else:
            improvement = analytics_data.get('progression', {}).get('improvement', 0)
    else:
        improvement = analytics_data.get('progression', {}).get('improvement', 0)
    
    context = {
        # Profil et analytics
        'profile': profile,
        'analytics': {
            'overview': {
                'average_score': combined_average_score,  # Score combiné
                'total_tests': total_tests_combined,      # Tests combinés
            },
            'study_time': {
                'total_hours': analytics_data.get('study_time', {}).get('total_hours', 0),
            },
            'progression': {
                'trend': 'improving' if improvement > 0 else 'declining' if improvement < 0 else 'stable',
                'improvement': improvement,
            },
            'weak_areas': weak_areas,
            'strong_areas': strong_areas,
        },
        'results': all_combined_results,  # Liste combinée pour le tableau
        
        # Performances par matière (déjà combinées)
        'performance_by_subject': performance_by_subject,
        
        # NOUVELLE ANALYSE PAR CONCEPTS (SÉPARÉE)
        'manual_concept_insights': manual_concept_insights,  # Tests manuels seulement
        'ai_concept_insights': ai_concept_insights,  # Tests IA seulement
        'concept_insights': concept_insights,  # Analysis combinée (pour compatibilité)
        
        # ANALYSE IA AVANCÉE (Mistral-7B-Instruct-v0.2)
        'manual_ai_analysis': manual_ai_analysis,  # Analyse IA détaillée des tests manuels
        'ai_tests_ai_analysis': ai_tests_ai_analysis,  # Analyse IA détaillée des tests IA
        'manual_tests_count': len(manual_tests_for_ai),
        'ai_tests_count': len(ai_tests_for_ai),
        
        # Analyse IA des faiblesses
        'weaknesses_analysis': weaknesses_analysis,
        
        # Gamification
        'level_info': level_info,
        'student_rank': student_rank,
        'badges': profile.badges or [],
        'new_badges': new_badges,  # Nouveaux badges obtenus
        'badge_progress': badge_progress_data,  # ✅ Progression de tous les badges
        
        # Données pour graphiques (Chart.js) - COMBINÉES
        'progression_chart_data': progression_chart_data,
        'subjects_chart_data': subjects_chart_data,
        'study_time_chart_data': study_time_chart_data,
        
        # Statistiques rapides - COMBINÉES
        'total_tests': total_tests_combined,
        'average_score': combined_average_score,
        'total_study_hours': analytics_data.get('study_time', {}).get('total_hours', 0),
        'improvement_trend': 'improving' if improvement > 0 else 'declining' if improvement < 0 else 'stable',
        'improvement_percentage': improvement,
        'manual_tests_count': manual_total,
        'ai_tests_count': ai_total,
        
        # Flags
        'has_data': total_tests_combined > 0,
        'has_multiple_subjects': len(performance_by_subject) > 1,
    }
    
    # Fermer la connexion MongoDB maintenant que tout est terminé
    client.close()
    
    return render(request, 'evaluation/student/progress_new.html', context)


@login_required
def view_result(request, result_id):
    """Afficher le résultat d'un test avec analyse IA"""
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le résultat via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        result_data = db.results.find_one({
            '_id': ObjectId(result_id),
            'student_id': request.user.id
        })
        
        if not result_data:
            client.close()
            messages.error(request, "Résultat non trouvé")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du résultat
        result_id_obj = result_data.pop('_id', None)
        result = Result(**{k: v for k, v in result_data.items() if k != '_id'})
        result.pk = result_id_obj
        result.id = result_id_obj
        result._state.adding = False
        result._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    context = {
        'result': result,
        'test': result.test,
    }
    
    return render(request, 'evaluation/student/view_result_ultra.html', context)


@login_required
def test_history(request, test_id):
    """Afficher l'historique complet d'un test"""
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({'_id': ObjectId(test_id)})
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    # Récupérer tous les résultats pour ce test
    results = Result.objects.filter(
        student=request.user,
        test=test
    ).order_by('created_at')
    
    total_attempts = results.count()
    
    # Calculer les statistiques
    evolution_data = {
        'labels': [f"Tentative {i+1}" for i in range(total_attempts)],
        'scores': [r.percentage_score for r in results],
        'best_score': max([r.percentage_score for r in results]) if results else 0,
        'average_score': sum([r.percentage_score for r in results]) / total_attempts if total_attempts > 0 else 0,
    }
    
    # Vérifier si passé
    passed = any(r.percentage_score >= test.passing_score for r in results)
    
    # Analyser les forces et faiblesses récurrentes
    persistent_strengths = []
    persistent_weaknesses = []
    learning_path = []
    
    if results.count() >= 2:
        # Analyser les 3 derniers résultats
        recent_results = list(results.order_by('-created_at')[:3])
        
        # Si amélioration constante
        if len(recent_results) >= 2:
            scores = [r.percentage_score for r in reversed(recent_results)]
            if all(scores[i] < scores[i+1] for i in range(len(scores)-1)):
                persistent_strengths.append("Progression constante")
                learning_path.append("Continuez à ce rythme!")
            elif scores[-1] < scores[0]:
                persistent_weaknesses.append("Baisse de performance")
                learning_path.append("Réviser les concepts de base")
        
        # Analyser les sujets
        if test.subject:
            avg_score = evolution_data['average_score']
            if avg_score >= 80:
                persistent_strengths.append(f"Excellente maîtrise de {test.subject}")
            elif avg_score < 60:
                persistent_weaknesses.append(f"Difficultés en {test.subject}")
                learning_path.append(f"Approfondir les fondamentaux de {test.subject}")
    
    context = {
        'test': test,
        'results': results,
        'total_attempts': total_attempts,
        'evolution_data': evolution_data,
        'passed': passed,
        'persistent_strengths': persistent_strengths,
        'persistent_weaknesses': persistent_weaknesses,
        'learning_path': learning_path,
    }
    
    return render(request, 'evaluation/student/test_history_ultra.html', context)


# ============================================
# API Endpoints (JSON)
# ============================================

@login_required
@require_http_methods(["POST"])
def save_answer_ajax(request):
    """
    Sauvegarder une réponse en AJAX (auto-sauvegarde)
    """
    try:
        data = json.loads(request.body)
        submission_id = data.get('submission_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        submission = Submission.objects.get(
            id=submission_id,
            student=request.user,
            status='in_progress'
        )
        
        # Mettre à jour les réponses
        if not submission.answers:
            submission.answers = {}
        
        submission.answers[str(question_id)] = {
            'answer': answer,
            'saved_at': timezone.now().isoformat()
        }
        submission.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_test_stats_ajax(request, test_id):
    """
    Récupérer les statistiques d'un test en JSON
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({'_id': ObjectId(test_id)})
        
        if not test_data:
            client.close()
            return JsonResponse({'error': 'Test non trouvé'}, status=404)
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        return JsonResponse({'error': str(e)}, status=400)
    
    # Vérifier les permissions
    if not request.user.is_staff and test.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    stats = TestService.get_test_statistics(test)
    
    return JsonResponse(stats)


@login_required
def test_history(request, test_id):
    """
    Affiche l'historique complet de toutes les tentatives d'un test
    avec analyse détaillée de l'évolution
    """
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer le test via PyMongo
    try:
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        test_data = db.tests.find_one({'_id': ObjectId(test_id)})
        
        if not test_data:
            client.close()
            messages.error(request, "Test non trouvé")
            return redirect('evaluation:student_dashboard')
        
        # Créer instance Django du test
        test_id_obj = test_data.pop('_id', None)
        test = Test(**{k: v for k, v in test_data.items() if k != '_id'})
        test.pk = test_id_obj
        test.id = test_id_obj
        test._state.adding = False
        test._state.db = 'default'
        
        client.close()
        
    except Exception as e:
        if 'client' in locals():
            client.close()
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('evaluation:student_dashboard')
    
    # Récupérer toutes les soumissions de l'étudiant pour ce test
    submissions = Submission.objects.filter(
        test=test,
        student=request.user,
        status='submitted'
    ).order_by('submitted_at')
    
    # Récupérer tous les résultats associés
    results = Result.objects.filter(
        test=test,
        student=request.user
    ).order_by('created_at')
    
    if not results.exists():
        messages.info(request, "Vous n'avez pas encore passé ce test.")
        return redirect('evaluation:test_detail', test_id=test_id)
    
    # Analyser l'évolution
    evolution_data = {
        'scores': [r.percentage_score for r in results],
        'dates': [r.created_at.strftime('%d/%m/%Y %H:%M') for r in results],
        'attempts': list(range(1, len(results) + 1)),
        'best_score': max(r.percentage_score for r in results),
        'worst_score': min(r.percentage_score for r in results),
        'average_score': sum(r.percentage_score for r in results) / len(results),
        'progression': 'improving' if len(results) >= 2 and results.last().percentage_score > results.first().percentage_score else 'stable'
    }
    
    # Analyser les compétences sur toutes les tentatives
    all_strengths = []
    all_weaknesses = []
    all_recommendations = []
    
    for result in results:
        if result.ai_analysis:
            strengths = result.ai_analysis.get('strengths', [])
            weaknesses = result.ai_analysis.get('weaknesses', [])
            
            # Extraire les skills/descriptions
            for s in strengths:
                if isinstance(s, dict):
                    all_strengths.append(s.get('skill', s.get('description', str(s))))
                else:
                    all_strengths.append(str(s))
            
            for w in weaknesses:
                if isinstance(w, dict):
                    all_weaknesses.append(w.get('skill', w.get('description', str(w))))
                else:
                    all_weaknesses.append(str(w))
    
    # Compter les occurrences pour identifier les patterns
    from collections import Counter
    strengths_counter = Counter(all_strengths)
    weaknesses_counter = Counter(all_weaknesses)
    
    persistent_strengths = [s for s, count in strengths_counter.most_common(3) if s]
    persistent_weaknesses = [w for w, count in weaknesses_counter.most_common(3) if w]
    
    # Générer un parcours d'apprentissage personnalisé
    from .ai_feedback import AIFeedbackGenerator
    learning_path = AIFeedbackGenerator.generate_learning_path(
        request.user,
        test.subject
    )
    
    context = {
        'test': test,
        'submissions': submissions,
        'results': results,
        'evolution_data': evolution_data,
        'persistent_strengths': persistent_strengths,
        'persistent_weaknesses': persistent_weaknesses,
        'all_recommendations': list(all_recommendations),
        'learning_path': learning_path,
        'total_attempts': len(results),
        'passed': any(r.percentage_score >= test.passing_score for r in results)
    }
    
    return render(request, 'evaluation/student/test_history_ultra.html', context)


# ============================================
# Nouvelles Vues pour Interfaces Modernes
# ============================================

@login_required
def my_tests(request):
    """
    Interface moderne pour afficher tous les tests de l'étudiant.
    Affiche un tableau avec statistiques et graphiques.
    Inclut les tests manuels ET les tests générés par IA.
    """
    from .models import Test, Result, Submission
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from collections import defaultdict
    import json
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    
    # Récupérer tous les tests manuels publiés
    all_manual_tests = Test.objects.filter(status='published').order_by('-created_at')
    
    # Récupérer les tests IA via PyMongo
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    ai_exercise_sets = list(db.exercise_sets.find({'status': 'published'}).sort('created_at', -1))
    
    # Préparer les données pour chaque test
    tests_data = []
    all_scores_evolution = []
    subject_scores = defaultdict(list)
    
    # 1. TRAITER LES TESTS MANUELS
    for test in all_manual_tests:
        # Récupérer les résultats de l'étudiant pour ce test
        results = Result.objects.filter(
            submission__student=request.user,
            submission__test=test,
            submission__status='graded'
        ).order_by('-created_at')
        
        attempts = results.count()
        best_score = None
        last_score = None
        last_result_id = None
        
        if attempts > 0:
            best_score = max(r.percentage_score for r in results)
            last_result = results.first()
            last_score = last_result.percentage_score
            last_result_id = last_result.id
            
            # Ajouter aux données d'évolution
            for result in results:
                all_scores_evolution.append({
                    'date': result.created_at.strftime('%d/%m'),
                    'score': result.percentage_score
                })
            
            # Ajouter aux scores par matière
            subject_scores[test.subject or 'Général'].append(best_score)
        
        tests_data.append({
            'test_obj': test,
            'attempts': attempts,
            'best_score': best_score,
            'last_score': last_score,
            'last_result_id': last_result_id,
            'source': 'manual',  # Identifier comme test manuel
            'test_type': 'Manual'
        })
    
    # 2. TRAITER LES TESTS IA
    for set_data in ai_exercise_sets:
        set_id = str(set_data['_id'])
        
        # Récupérer le vrai subject depuis le CourseDocument
        subject_key = 'Général'  # Fallback par défaut
        source_doc_id = set_data.get('source_document_id')
        if source_doc_id:
            try:
                doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                if doc_data and doc_data.get('subject'):
                    subject_key = doc_data.get('subject').capitalize()
            except:
                pass
        
        # Récupérer les soumissions de l'étudiant pour ce set
        submissions = list(db.student_exercise_submissions.find({
            'student_id': request.user.id,
            'exercise_set_id': set_id,
            'status': 'completed'
        }).sort('submitted_at', -1))
        
        attempts = len(submissions)
        best_score = None
        last_score = None
        
        if attempts > 0:
            best_score = max(s.get('score', 0) for s in submissions)
            last_submission = submissions[0]
            last_score = last_submission.get('score', 0)
            
            # Ajouter aux données d'évolution
            for submission in submissions:
                submitted_at = submission.get('submitted_at')
                if submitted_at:
                    all_scores_evolution.append({
                        'date': submitted_at.strftime('%d/%m'),
                        'score': submission.get('score', 0)
                    })
            
            # Ajouter aux scores par matière (utiliser le vrai subject du CourseDocument)
            subject_scores[subject_key].append(best_score)
        
        # Créer un objet compatible pour le template
        tests_data.append({
            'ai_set_data': set_data,  # Données brutes MongoDB
            'ai_set_id': set_id,
            'attempts': attempts,
            'best_score': best_score,
            'last_score': last_score,
            'source': 'ai',  # Identifier comme test IA
            'test_type': 'IA'
        })
    
    client.close()
    
    client.close()
    
    # Pagination (10 tests par page)
    paginator = Paginator(tests_data, 10)
    page_number = request.GET.get('page', 1)
    
    try:
        tests_page = paginator.page(page_number)
    except PageNotAnInteger:
        tests_page = paginator.page(1)
    except EmptyPage:
        tests_page = paginator.page(paginator.num_pages)
    
    # Calculer les statistiques globales (tests manuels + IA)
    # Tests manuels
    manual_results = Result.objects.filter(
        submission__student=request.user,
        submission__status='graded'
    )
    
    manual_tests_count = manual_results.count()
    manual_average = manual_results.aggregate(Avg('percentage_score'))['percentage_score__avg'] or 0
    manual_passed = sum(1 for r in manual_results if r.percentage_score >= r.submission.test.passing_score)
    manual_time = sum(r.submission.test.duration for r in manual_results) / 60  # En heures
    
    # Tests IA
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    ai_submissions = list(db.student_exercise_submissions.find({
        'student_id': request.user.id,
        'status': 'completed'
    }))
    
    ai_tests_count = len(ai_submissions)
    ai_average = sum(s.get('score', 0) for s in ai_submissions) / ai_tests_count if ai_tests_count > 0 else 0
    ai_passed = sum(1 for s in ai_submissions if s.get('score', 0) >= 60)  # Seuil 60%
    
    client.close()
    
    # Statistiques combinées
    total_tests = manual_tests_count + ai_tests_count
    average_score = ((manual_average * manual_tests_count) + (ai_average * ai_tests_count)) / total_tests if total_tests > 0 else 0
    tests_passed = manual_passed + ai_passed
    total_time = manual_time  # On ne compte que le temps des tests manuels (duration définie)
    
    stats = {
        'total_tests': total_tests,
        'average_score': average_score,
        'tests_passed': tests_passed,
        'total_time': total_time,
        'manual_tests': manual_tests_count,
        'ai_tests': ai_tests_count
    }
    
    # Préparer les données pour les graphiques
    # Évolution des scores (derniers 10)
    evolution_sorted = sorted(all_scores_evolution, key=lambda x: x['date'])[-10:]
    score_evolution_data = {
        'labels': [item['date'] for item in evolution_sorted],
        'scores': [item['score'] for item in evolution_sorted]
    }
    
    # Performance par matière
    subject_performance_data = {
        'labels': list(subject_scores.keys()),
        'scores': [sum(scores)/len(scores) for scores in subject_scores.values()]
    }
    
    context = {
        'tests': tests_page,
        'stats': stats,
        'score_evolution_data': json.dumps(score_evolution_data),
        'subject_performance_data': json.dumps(subject_performance_data)
    }
    
    return render(request, 'evaluation/student/my_tests.html', context)


@login_required
def my_badges(request):
    """
    Interface moderne pour afficher les badges de l'étudiant.
    Affiche les badges obtenus, les badges disponibles, et des statistiques.
    """
    from .gamification import GamificationService
    from .models import UserProfile
    import json
    from collections import Counter
    
    # Récupérer ou créer le profil (robuste si des doublons existent dans la base)
    created = False
    try:
        profiles_qs = UserProfile.objects.filter(user=request.user).order_by('-created_at')
        profile = profiles_qs.first() if profiles_qs.exists() else None
        if profile is None:
            # Aucun profil trouvé → créer un nouveau via ORM
            profile = UserProfile.objects.create(user=request.user)
            created = True
    except Exception:
        # Certains backends (ex: djongo) peuvent échouer avec des erreurs SQL/recursion.
        # En fallback, lire directement depuis MongoDB via PyMongo si possible.
        import traceback
        traceback.print_exc()
        profile = None
        try:
            from pymongo import MongoClient
            from django.conf import settings

            client = get_mongodb_client()
            db = client[settings.MONGO_DB_NAME]

            found = db['evaluation_userprofile'].find_one({'user_id': request.user.id}, sort=[('created_at', -1)])
            if found:
                # Construire une instance non sauvegardée de UserProfile à partir du document
                profile = UserProfile()
                profile.user = request.user
                mapping_fields = [
                    'role', 'student_id', 'date_of_birth', 'phone_number', 'class_level', 'specialization',
                    'total_tests_taken', 'average_score', 'total_study_time', 'level', 'total_xp', 'badges',
                    'strengths', 'weaknesses', 'ai_recommendations', 'learning_style', 'performance_history',
                    'skill_progress', 'created_at', 'updated_at', 'is_active'
                ]
                for field in mapping_fields:
                    if field in found:
                        try:
                            setattr(profile, field, found[field])
                        except Exception:
                            pass
                # Coerce numeric/list fields to safe defaults to avoid None arithmetic in views
                try:
                    lvl = getattr(profile, 'level', None)
                    profile.level = int(lvl) if (lvl is not None and str(lvl).isdigit()) else 1
                except Exception:
                    profile.level = 1
                try:
                    txp = getattr(profile, 'total_xp', None)
                    profile.total_xp = int(txp) if txp is not None else 0
                except Exception:
                    profile.total_xp = 0
                try:
                    coins = getattr(profile, 'coins', None)
                    profile.coins = int(coins) if coins is not None else 0
                except Exception:
                    profile.coins = 0
                try:
                    streak = getattr(profile, 'current_streak', None)
                    profile.current_streak = int(streak) if streak is not None else 0
                except Exception:
                    profile.current_streak = 0
                try:
                    if getattr(profile, 'badges', None) is None:
                        profile.badges = []
                except Exception:
                    profile.badges = []
                try:
                    profile._state.adding = False
                except Exception:
                    pass
                created = False
            else:
                # Si rien trouvé, essayer de créer via ORM (dernier recours)
                try:
                    profile = UserProfile.objects.create(user=request.user)
                    created = True
                except Exception:
                    profile = None
            try:
                client.close()
            except Exception:
                pass
        except Exception:
            # Aucun fallback possible — la vue doit gérer profile == None
            profile = None
    
    # Service de gamification
    gamification_service = GamificationService(profile)
    
    # ✅ VÉRIFIER ET ATTRIBUER LES NOUVEAUX BADGES
    try:
        new_badges = gamification_service.check_and_award_badges()
        if new_badges:
            print(f"🎉 Nouveaux badges obtenus dans my_badges: {[b['name'] for b in new_badges]}")
    except Exception as e:
        print(f"❌ Erreur attribution badges: {e}")
        import traceback
        traceback.print_exc()
    
    # ✅ OBTENIR LA PROGRESSION RÉELLE DE TOUS LES BADGES
    try:
        badge_progress_data = gamification_service.get_badge_progress()
        earned_badges_data = badge_progress_data['earned_badges']
        available_badges_data = badge_progress_data['available_badges']
    except Exception as e:
        print(f"❌ Erreur get_badge_progress: {e}")
        import traceback
        traceback.print_exc()
        earned_badges_data = []
        available_badges_data = []
    
    # Préparer les données des badges pour le template
    badges = []
    category_counts = Counter()
    
    # Ajouter les badges obtenus
    for badge_data in earned_badges_data:
        badge_info = {
            'id': badge_data['badge_id'],
            'name': badge_data['name'],
            'description': badge_data['description'],
            'category': 'achievement',  # Catégorie par défaut
            'icon': badge_data['icon'],
            'color': badge_data.get('color', '#667eea'),
            'xp_reward': badge_data['points'],
            'earned': True,
            'earned_date': badge_data.get('earned_at', profile.created_at),
            'progress': 100,
            'requirement': 'Complété !'
        }
        badges.append(badge_info)
        category_counts['achievement'] += 1
    
    # Ajouter les badges disponibles (non obtenus)
    for badge_data in available_badges_data:
        progress = badge_data.get('progress_percentage', 0)
        current = badge_data.get('progress', 0)
        target = badge_data.get('target', 1)
        
        badge_info = {
            'id': badge_data['badge_id'],
            'name': badge_data['name'],
            'description': badge_data['description'],
            'category': 'progress' if progress > 0 else 'locked',
            'icon': badge_data['icon'],
            'color': badge_data.get('color', '#667eea'),
            'xp_reward': badge_data['points'],
            'earned': False,
            'earned_date': None,
            'progress': progress,
            'requirement': f"Progression {current}/{target} - Complétez les objectifs"
        }
        badges.append(badge_info)
        category_counts['progress' if progress > 0 else 'locked'] += 1
    
    # Statistiques
    total_earned = len(earned_badges_data)
    total_available = len(badges)
    completion_rate = (total_earned / total_available * 100) if total_available > 0 else 0
    
    # Compter les badges rares (ceux avec un XP élevé)
    rarest_owned = sum(1 for b in badges if b['earned'] and b['xp_reward'] >= 80)
    
    stats = {
        'total_earned': total_earned,
        'total_available': total_available,
        'completion_rate': completion_rate,
        'rarest_owned': rarest_owned
    }
    
    # Données pour les graphiques
    category_data = {
        'labels': list(category_counts.keys()),
        'values': list(category_counts.values())
    }
    
    # Progression dans le temps (simplifiée)
    progress_data = {
        'labels': ['Mois 1', 'Mois 2', 'Mois 3', 'Actuel'],
        'values': [0, max(0, total_earned - 3), max(0, total_earned - 1), total_earned]
    }
    
    context = {
        'badges': badges,
        'stats': stats,
        'category_data': json.dumps(category_data),
        'progress_data': json.dumps(progress_data)
    }
    
    return render(request, 'evaluation/student/my_badges.html', context)


@login_required
def students_list(request):
    """
    Vue pour les enseignants: liste des étudiants avec prédictions IA.
    Affiche pour chaque étudiant: niveau actuel, badges, scores, prédiction future.
    """
    from .models import UserProfile, Result, Submission
    from .ai_prediction import StudentLevelPredictor, get_student_level_class, get_student_level_name
    from .gamification import GamificationService
    from django.contrib.auth import get_user_model
    import json
    
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux enseignants")
        return redirect('evaluation:student_dashboard')
    
    User = get_user_model()
    
    # Récupérer tous les étudiants (non-staff users avec profil)
    # FIX: Éviter user__is_staff=False car Djongo ne gère pas bien WHERE NOT
    # On filtre côté Python après récupération
    students_profiles = UserProfile.objects.filter(
        role='student'  # Utiliser le champ role au lieu de user__is_staff
    ).select_related('user')
    
    students_data = []
    total_students = 0
    pro_count = 0
    moyen_count = 0
    faible_count = 0
    total_score_sum = 0
    total_tests_all = 0
    total_badges_all = 0
    
    for profile in students_profiles:
        # Récupérer les résultats de l'étudiant
        results = Result.objects.filter(
            submission__student=profile.user,
            submission__status='graded'
        ).order_by('created_at')
        
        if results.count() == 0:
            continue  # Ignorer les étudiants sans résultats
        
        total_students += 1
        
        # Calculer les statistiques
        scores = [r.percentage_score for r in results]
        average_score = sum(scores) / len(scores)
        tests_completed = results.count()
        tests_passed = sum(1 for r in results if r.percentage_score >= r.submission.test.passing_score)
        
        # Niveau actuel
        current_level = get_student_level_name(average_score)
        current_level_class = get_student_level_class(average_score)
        
        # Compter par niveau
        if current_level == 'Pro':
            pro_count += 1
        elif current_level == 'Moyen':
            moyen_count += 1
        else:
            faible_count += 1
        
        total_score_sum += average_score
        total_tests_all += tests_completed
        
        # Prédiction IA
        predictor = StudentLevelPredictor(profile)
        ai_prediction = predictor.predict_future_level()
        
        # Tendance
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:3]) / 3
            if recent_avg > older_avg + 5:
                trend = 'improving'
            elif recent_avg < older_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Badges
        student_badges = profile.badges if isinstance(profile.badges, list) else []
        badges_count = len(student_badges)
        total_badges_all += badges_count
        
        # Récupérer quelques badges pour affichage
        all_badge_defs = [
            {'id': key, **value}
            for key, value in GamificationService.BADGES.items()
        ]
        recent_badges = []
        for badge_def in all_badge_defs[:5]:
            if badge_def['id'] in student_badges:
                recent_badges.append({
                    'name': badge_def['name'],
                    'icon': badge_def['icon'],
                    'color': badge_def.get('color', '#667eea')
                })
        
        # Forces et faiblesses
        strengths = []
        weaknesses = []
        
        for result in results:
            if result.ai_analysis:
                for s in result.ai_analysis.get('strengths', [])[:2]:
                    if isinstance(s, dict):
                        strength_text = s.get('skill', s.get('description', ''))
                    else:
                        strength_text = str(s)
                    if strength_text and strength_text not in strengths:
                        strengths.append(strength_text)
                
                for w in result.ai_analysis.get('weaknesses', [])[:2]:
                    if isinstance(w, dict):
                        weakness_text = w.get('skill', w.get('description', ''))
                    else:
                        weakness_text = str(w)
                    if weakness_text and weakness_text not in weaknesses:
                        weaknesses.append(weakness_text)
        
        # Historique des scores pour mini graphique
        score_history = {
            'labels': [f"T{i+1}" for i in range(min(10, len(scores)))],
            'scores': scores[-10:] if len(scores) > 10 else scores
        }
        
        students_data.append({
            'id': profile.user.id,
            'full_name': profile.user.get_full_name() or profile.user.username,
            'email': profile.user.email,
            'initials': ''.join([n[0].upper() for n in profile.user.get_full_name().split()[:2]]) if profile.user.get_full_name() else profile.user.username[0].upper(),
            'current_level': current_level,
            'current_level_class': current_level_class,
            'average_score': average_score,
            'tests_completed': tests_completed,
            'tests_passed': tests_passed,
            'total_xp': profile.total_xp,
            'badges_count': badges_count,
            'recent_badges': recent_badges,
            'strengths': strengths[:3],
            'weaknesses': weaknesses[:3],
            'trend': trend,
            'ai_prediction': ai_prediction,
            'score_history': score_history
        })
    
    # Statistiques globales
    stats = {
        'total_students': total_students,
        'pro_students': pro_count,
        'moyen_students': moyen_count,
        'faible_students': faible_count,
        'average_score': total_score_sum / total_students if total_students > 0 else 0,
        'total_tests': total_tests_all,
        'total_badges': total_badges_all
    }
    
    # Trier par score moyen décroissant
    students_data.sort(key=lambda x: x['average_score'], reverse=True)
    
    context = {
        'students': students_data,
        'stats': stats
    }



    
    return render(request, 'evaluation/teacher/students_list.html', context)

    
# ============================================
# Vue d'inscription (Sign Up)
# ============================================

def signup(request):
    """
    Vue d'inscription pour les nouveaux utilisateurs
    Professeur si is_staff=True, Étudiant sinon
    """
    if request.user.is_authenticated:
        return redirect('evaluation:student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'student')  # 'student' ou 'teacher'
        
        # Validation
        from django.contrib.auth.models import User
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'registration/signup.html')
        
        if len(password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
            return render(request, 'registration/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return render(request, 'registration/signup.html')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email est déjà utilisée.")
            return render(request, 'registration/signup.html')
        
        try:
            from pymongo import MongoClient
            from django.conf import settings
            from bson import ObjectId
            from django.utils import timezone as django_timezone
            
            # Connexion MongoDB
            client = get_mongodb_client()
            db = client[settings.MONGO_DB_NAME]
            
            # Obtenir le prochain ID pour auth_user
            last_user = db.auth_user.find_one(sort=[('id', -1)])
            next_id = (last_user['id'] + 1) if last_user else 1
            
            # Hasher le mot de passe
            from django.contrib.auth.hashers import make_password
            hashed_password = make_password(password)
            
            # Créer l'utilisateur directement dans MongoDB
            user_data = {
                '_id': ObjectId(),
                'id': next_id,
                'username': username,
                'email': email,
                'password': hashed_password,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': (user_type == 'teacher'),
                'is_active': True,
                'is_superuser': False,
                'date_joined': django_timezone.now(),
                'last_login': None
            }
            
            db.auth_user.insert_one(user_data)
            
            # Créer le profil utilisateur seulement s'il n'existe pas
            existing_profile = db.evaluation_userprofile.find_one({'user_id': next_id})
            if not existing_profile:
                profile_data = {
                    '_id': ObjectId(),
                    'user_id': next_id,
                    'role': 'teacher' if user_type == 'teacher' else 'student'
                }
                db.evaluation_userprofile.insert_one(profile_data)
            
            messages.success(request, f"Compte créé avec succès ! Vous pouvez maintenant vous connecter avec vos identifiants.")
            
            # Redirection vers la page de connexion
            return redirect('login')
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erreur d'inscription: {error_detail}")
            messages.error(request, f"Erreur lors de la création du compte : {str(e)}")
            return render(request, 'registration/signup.html')
    
    return render(request, 'registration/signup.html')
