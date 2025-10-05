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
from ai_modules.ai_services import get_ai_services


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
    
    # Récupérer les tests créés par l'enseignant
    tests = Test.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Statistiques globales
    stats = {
        'total_tests': tests.count(),
        'published_tests': tests.filter(status='published').count(),
        'total_submissions': Submission.objects.filter(test__created_by=request.user).count(),
    }
    
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
    test = get_object_or_404(Test, id=test_id, created_by=request.user)
    
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
        
        messages.success(request, f"Test mis à jour avec succès ! Statut: {test.get_status_display()}")
        return redirect('evaluation:teacher_dashboard')
    
    # Récupérer les questions du test
    questions = test.questions.all().order_by('order')
    
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
    test = get_object_or_404(Test, id=test_id, created_by=request.user)
    
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
        
        messages.success(request, "Question ajoutée avec succès !")
        return redirect('evaluation:edit_test', test_id=test.id)
    
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
    test = get_object_or_404(Test, id=test_id, created_by=request.user)
    
    # Récupérer les statistiques
    stats = TestService.get_test_statistics(test)
    
    # Récupérer les soumissions
    submissions = Submission.objects.filter(
        test=test, 
        status='graded'
    ).select_related('student').order_by('-submitted_at')
    
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
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'student'}
    )
    
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
        'strengths': analytics_data['strengths'],
        'weaknesses': analytics_data['weaknesses'],
        
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
        'in_progress_submissions': in_progress_submissions,
        'recent_results': recent_results,
        'pending_tests': len(available_tests),
        
        # Alertes
        'alerts': alerts,
        
        # Métadonnées
        'has_activity': analytics_data['metadata']['total_tests'] > 0,
        'is_new_student': created or analytics_data['metadata']['total_tests'] == 0,
    }
    
    return render(request, 'evaluation/student/dashboard.html', context)


@login_required
def test_detail(request, test_id):
    """
    Détails d'un test (avant de le commencer)
    """
    test = get_object_or_404(Test, id=test_id, status='published')
    
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
    test = get_object_or_404(Test, id=test_id, status='published')
    
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
    submission = get_object_or_404(
        Submission, 
        id=submission_id, 
        student=request.user,
        status='in_progress'
    )
    
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
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        student=request.user,
        status='in_progress'
    )
    
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
    result = get_object_or_404(Result, id=result_id, student=request.user)
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
    """
    from .analytics import StudentAnalytics
    from .gamification import GamificationService
    
    # Récupérer le profil
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # 1. GÉNÉRATION DES ANALYTICS COMPLÈTES
    analytics_service = StudentAnalytics(profile)
    analytics_data = analytics_service.get_complete_statistics()
    
    # 2. RÉCUPÉRER TOUS LES RÉSULTATS POUR GRAPHIQUES
    all_results = Result.objects.filter(
        student=request.user
    ).select_related('test').order_by('-created_at')
    
    # 3. PERFORMANCES PAR MATIÈRE (pour graphiques)
    performance_by_subject = {}
    for subject, data in analytics_data['subjects'].items():
        performance_by_subject[subject] = {
            'avg_score': data['average'],
            'count': data['count'],
            'trend': data['trend'],
            'last_score': data['last_score'],
            'tests': data['tests']
        }
    
    # 4. ANALYSER LES FAIBLESSES AVEC IA
    weaknesses_analysis = None
    if all_results.count() >= 2:
        try:
            ai_services = get_ai_services()
            # Prendre les 10 derniers APRÈS le tri
            recent_results = all_results.order_by('-created_at')[:10]
            weaknesses_analysis = ai_services['weakness_analyzer'].identify_weaknesses(
                profile, list(recent_results)  # Convertir en liste pour éviter les problèmes de slice
            )
        except Exception as e:
            print(f"Erreur analyse faiblesses IA: {e}")
            # Utiliser l'analyse locale si l'IA échoue
            weaknesses_analysis = {
                'weaknesses': analytics_data['weaknesses'],
                'strengths': analytics_data['strengths'],
                'recommendations': profile.ai_recommendations or []
            }
    
    # 5. GAMIFICATION
    gamification_service = GamificationService(profile)
    level_info = gamification_service.get_level_info()
    student_rank = gamification_service.get_student_rank(period='all_time')
    
    # 6. PRÉPARER LES DONNÉES POUR LES GRAPHIQUES
    # Données de progression temporelle (pour Chart.js)
    progression_chart_data = {
        'labels': [p['date'] for p in analytics_data['progression']['progression_data']],
        'scores': [p['score'] for p in analytics_data['progression']['progression_data']],
        'moving_average': [p['moving_average'] for p in analytics_data['progression']['progression_data']],
        'test_names': [p['test_name'] for p in analytics_data['progression']['progression_data']]
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
    study_sessions = analytics_data['study_time'].get('sessions', [])
    # Grouper par semaine
    from collections import defaultdict
    from datetime import timedelta
    
    weekly_study_time = defaultdict(float)
    for session in study_sessions:
        # Trouver le début de la semaine
        week_start = session['date'] - timedelta(days=session['date'].weekday())
        weekly_study_time[week_start.strftime('%Y-%m-%d')] += session['duration']
    
    study_time_chart_data = {
        'weeks': sorted(weekly_study_time.keys()),
        'hours': [round(weekly_study_time[week] / 60, 2) for week in sorted(weekly_study_time.keys())]
    }
    
    # 8. PRÉPARER DONNÉES STRUCTURÉES POUR FAIBLESSES/FORCES
    # Analyser les performances par compétence
    weak_areas = {}
    strong_areas = {}
    
    for result in all_results[:20]:  # Analyser les 20 derniers tests
        test = result.test
        # Calculer le score en %
        percentage = (result.total_score / test.total_points * 100) if test.total_points > 0 else 0
        
        # Clé: matière du test
        key = test.subject or "Général"
        
        if key not in weak_areas:
            weak_areas[key] = {'total': 0, 'correct': 0, 'score': 0}
            strong_areas[key] = {'total': 0, 'correct': 0, 'score': 0}
        
        # Compter les questions
        weak_areas[key]['total'] += 1
        strong_areas[key]['total'] += 1
        
        if percentage >= 70:
            strong_areas[key]['correct'] += 1
        else:
            weak_areas[key]['correct'] += 1
    
    # Calculer les scores
    for key in weak_areas:
        if weak_areas[key]['total'] > 0:
            weak_areas[key]['score'] = (weak_areas[key]['correct'] / weak_areas[key]['total']) * 100
        if strong_areas[key]['total'] > 0:
            strong_areas[key]['score'] = (strong_areas[key]['correct'] / strong_areas[key]['total']) * 100
    
    # Filtrer: faiblesses = score < 70%, forces = score >= 70%
    final_weak_areas = {k: v for k, v in weak_areas.items() if v['score'] < 70 and v['total'] > 0}
    final_strong_areas = {k: v for k, v in strong_areas.items() if v['score'] >= 70 and v['total'] > 0}
    
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
    
    # 10. CONSTRUCTION DU CONTEXTE
    context = {
        # Profil et analytics
        'profile': profile,
        'analytics': {
            'overview': {
                'average_score': analytics_data['scores'].get('average', 0),
                'total_tests': analytics_data['metadata']['total_tests'],
            },
            'study_time': {
                'total_hours': analytics_data['study_time']['total_hours'],
            },
            'progression': {
                'trend': analytics_data['progression']['trend'],
                'improvement': analytics_data['progression']['improvement'],
            },
            'weak_areas': final_weak_areas,
            'strong_areas': final_strong_areas,
        },
        'results': all_results,
        
        # Performances par matière
        'performance_by_subject': performance_by_subject,
        
        # Analyse IA des faiblesses
        'weaknesses_analysis': weaknesses_analysis,
        
        # Gamification
        'level_info': level_info,
        'student_rank': student_rank,
        'badges': profile.badges or [],
        
        # Données pour graphiques (Chart.js)
        'progression_chart_data': progression_chart_data,
        'subjects_chart_data': subjects_chart_data,
        'study_time_chart_data': study_time_chart_data,
        
        # Statistiques rapides
        'total_tests': analytics_data['metadata']['total_tests'],
        'average_score': analytics_data['scores'].get('average', 0),
        'total_study_hours': analytics_data['study_time']['total_hours'],
        'improvement_trend': analytics_data['progression']['trend'],
        'improvement_percentage': analytics_data['progression']['improvement'],
        
        # Flags
        'has_data': analytics_data['metadata']['total_tests'] > 0,
        'has_multiple_subjects': len(performance_by_subject) > 1,
    }
    
    return render(request, 'evaluation/student/progress_new.html', context)


@login_required
def view_result(request, result_id):
    """Afficher le résultat d'un test avec analyse IA"""
    result = get_object_or_404(Result, id=result_id, student=request.user)
    
    context = {
        'result': result,
        'test': result.test,
    }
    
    return render(request, 'evaluation/student/view_result_ultra.html', context)


@login_required
def test_history(request, test_id):
    """Afficher l'historique complet d'un test"""
    test = get_object_or_404(Test, id=test_id)
    
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
    test = get_object_or_404(Test, id=test_id)
    
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
    test = get_object_or_404(Test, id=test_id)
    
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
    
    return render(request, 'evaluation/student/test_history.html', context)

