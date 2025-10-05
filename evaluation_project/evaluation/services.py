"""
Services pour la correction automatique et la gestion des tests
"""
from django.utils import timezone
from .models import Test, Question, Submission, Result, UserProfile
from django.db.models import Avg, Count


class AutoGrading:
    """
    Service de correction automatique des tests
    """
    
    @staticmethod
    def grade_mcq_question(question, student_answer):
        """
        Corrige une question QCM
        
        Args:
            question: Instance de Question
            student_answer: Réponse de l'étudiant (ex: "A", "B", etc.)
            
        Returns:
            dict: {is_correct, points_earned, feedback}
        """
        if not question.options:
            return {
                'is_correct': False,
                'points_earned': 0,
                'feedback': 'Question mal configurée'
            }
        
        # Trouver la bonne réponse
        correct_options = [opt for opt in question.options if opt.get('is_correct', False)]
        
        if not correct_options:
            return {
                'is_correct': False,
                'points_earned': 0,
                'feedback': 'Pas de bonne réponse définie'
            }
        
        correct_answer = correct_options[0].get('id')
        is_correct = student_answer == correct_answer
        
        return {
            'is_correct': is_correct,
            'points_earned': question.points if is_correct else 0,
            'feedback': question.explanation if question.explanation else (
                'Correct !' if is_correct else f'Incorrect. La bonne réponse est {correct_answer}.'
            )
        }
    
    @staticmethod
    def grade_true_false_question(question, student_answer):
        """
        Corrige une question Vrai/Faux
        
        Args:
            question: Instance de Question
            student_answer: "True" ou "False"
            
        Returns:
            dict: {is_correct, points_earned, feedback}
        """
        correct_answer = question.correct_answer
        is_correct = str(student_answer).lower() == str(correct_answer).lower()
        
        return {
            'is_correct': is_correct,
            'points_earned': question.points if is_correct else 0,
            'feedback': question.explanation if question.explanation else (
                'Correct !' if is_correct else f'Incorrect. La bonne réponse est {correct_answer}.'
            )
        }
    
    @staticmethod
    def grade_short_answer_question(question, student_answer):
        """
        Corrige une réponse courte (comparaison exacte)
        
        Args:
            question: Instance de Question
            student_answer: Réponse de l'étudiant
            
        Returns:
            dict: {is_correct, points_earned, feedback}
        """
        correct_answer = question.correct_answer.strip().lower()
        student_ans = str(student_answer).strip().lower()
        
        is_correct = student_ans == correct_answer
        
        return {
            'is_correct': is_correct,
            'points_earned': question.points if is_correct else 0,
            'feedback': question.explanation if question.explanation else (
                'Correct !' if is_correct else f'Incorrect. La bonne réponse est {question.correct_answer}.'
            ),
            'requires_manual_review': False
        }
    
    @staticmethod
    def grade_submission(submission):
        """
        Corrige une soumission complète
        
        Args:
            submission: Instance de Submission
            
        Returns:
            dict: Résultats de la correction
        """
        test = submission.test
        questions = test.questions.all()
        
        total_points = 0
        earned_points = 0
        correct_count = 0
        total_count = 0
        
        detailed_results = {}
        questions_by_type = {
            'mcq': {'earned': 0, 'total': 0},
            'true_false': {'earned': 0, 'total': 0},
            'short_answer': {'earned': 0, 'total': 0},
            'essay': {'earned': 0, 'total': 0}
        }
        
        skills_performance = {}
        
        for question in questions:
            total_points += question.points
            total_count += 1
            
            # Récupérer la réponse de l'étudiant
            answer_data = submission.answers.get(str(question.id), {})
            student_answer = answer_data.get('answer')
            
            if not student_answer:
                detailed_results[str(question.id)] = {
                    'is_correct': False,
                    'points_earned': 0,
                    'feedback': 'Pas de réponse fournie'
                }
                continue
            
            # Correction selon le type de question
            if question.question_type == 'mcq':
                result = AutoGrading.grade_mcq_question(question, student_answer)
                questions_by_type['mcq']['total'] += question.points
                questions_by_type['mcq']['earned'] += result['points_earned']
                
            elif question.question_type == 'true_false':
                result = AutoGrading.grade_true_false_question(question, student_answer)
                questions_by_type['true_false']['total'] += question.points
                questions_by_type['true_false']['earned'] += result['points_earned']
                
            elif question.question_type == 'short_answer':
                result = AutoGrading.grade_short_answer_question(question, student_answer)
                questions_by_type['short_answer']['total'] += question.points
                questions_by_type['short_answer']['earned'] += result['points_earned']
                
            elif question.question_type in ['essay', 'fill_blank']:
                # Ces questions nécessitent une correction IA ou manuelle
                result = {
                    'is_correct': None,
                    'points_earned': 0,
                    'feedback': 'Correction en attente',
                    'requires_ai_grading': True
                }
                questions_by_type['essay']['total'] += question.points
            
            else:
                result = {
                    'is_correct': False,
                    'points_earned': 0,
                    'feedback': 'Type de question non supporté'
                }
            
            # Mettre à jour les réponses avec le résultat
            answer_data['is_correct'] = result.get('is_correct')
            answer_data['points_earned'] = result.get('points_earned', 0)
            answer_data['feedback'] = result.get('feedback', '')
            
            submission.answers[str(question.id)] = answer_data
            detailed_results[str(question.id)] = result
            
            # Compter les bonnes réponses
            if result.get('is_correct'):
                correct_count += 1
                earned_points += result['points_earned']
            
            # Analyser par compétence
            for skill in question.skills:
                if skill not in skills_performance:
                    skills_performance[skill] = {
                        'total_points': 0,
                        'earned_points': 0,
                        'questions_count': 0,
                        'correct_count': 0
                    }
                
                skills_performance[skill]['total_points'] += question.points
                skills_performance[skill]['earned_points'] += result.get('points_earned', 0)
                skills_performance[skill]['questions_count'] += 1
                if result.get('is_correct'):
                    skills_performance[skill]['correct_count'] += 1
        
        # Calculer le pourcentage
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = percentage >= test.passing_score
        
        # Mettre à jour la soumission
        submission.score = earned_points
        submission.percentage = percentage
        submission.passed = passed
        submission.status = 'graded'
        submission.save()
        
        return {
            'total_points': total_points,
            'earned_points': earned_points,
            'percentage': percentage,
            'passed': passed,
            'correct_count': correct_count,
            'total_count': total_count,
            'questions_by_type': questions_by_type,
            'skills_performance': skills_performance,
            'detailed_results': detailed_results
        }


class TestService:
    """
    Service pour la gestion des tests
    """
    
    @staticmethod
    def create_test(user, test_data):
        """
        Crée un nouveau test
        
        Args:
            user: Utilisateur créateur (enseignant)
            test_data: Données du test
            
        Returns:
            Test: Instance du test créé
        """
        test = Test.objects.create(
            created_by=user,
            **test_data
        )
        return test
    
    @staticmethod
    def add_question_to_test(test, question_data):
        """
        Ajoute une question à un test
        
        Args:
            test: Instance de Test
            question_data: Données de la question
            
        Returns:
            Question: Instance de la question créée
        """
        question = Question.objects.create(
            test=test,
            **question_data
        )
        
        # Mettre à jour le nombre de questions du test
        test.number_of_questions = test.questions.count()
        test.save()
        
        return question
    
    @staticmethod
    def get_student_available_tests(student):
        """
        Récupère les tests disponibles pour un étudiant
        
        Args:
            student: Instance User de l'étudiant
            
        Returns:
            QuerySet: Tests publiés
        """
        return Test.objects.filter(status='published').order_by('-created_at')
    
    @staticmethod
    def start_test(student, test):
        """
        Démarre un test pour un étudiant
        
        Args:
            student: Instance User
            test: Instance Test
            
        Returns:
            Submission: Nouvelle soumission
        """
        submission = Submission.objects.create(
            student=student,
            test=test,
            status='in_progress',
            started_at=timezone.now()
        )
        return submission
    
    @staticmethod
    def submit_test(submission, answers):
        """
        Soumet un test avec les réponses
        
        Args:
            submission: Instance Submission
            answers: Dictionnaire des réponses
            
        Returns:
            dict: Résultats de la correction
        """
        submission.answers = answers
        submission.submitted_at = timezone.now()
        submission.time_spent = int((submission.submitted_at - submission.started_at).total_seconds())
        submission.status = 'submitted'
        submission.save()
        
        # Correction automatique
        grading_results = AutoGrading.grade_submission(submission)
        
        # Mettre à jour les statistiques du test
        test = submission.test
        test.total_attempts += 1
        test.save()
        
        return grading_results
    
    @staticmethod
    def get_test_statistics(test):
        """
        Calcule les statistiques d'un test
        
        Args:
            test: Instance Test
            
        Returns:
            dict: Statistiques
        """
        submissions = Submission.objects.filter(test=test, status='graded')
        
        stats = {
            'total_attempts': submissions.count(),
            'average_score': submissions.aggregate(Avg('percentage'))['percentage__avg'] or 0,
            'pass_rate': 0,
            'average_time': submissions.aggregate(Avg('time_spent'))['time_spent__avg'] or 0
        }
        
        if stats['total_attempts'] > 0:
            passed = submissions.filter(passed=True).count()
            stats['pass_rate'] = (passed / stats['total_attempts']) * 100
        
        return stats


class ResultService:
    """
    Service pour la gestion des résultats
    """
    
    @staticmethod
    def create_detailed_result(submission, grading_results):
        """
        Crée un résultat détaillé à partir d'une soumission
        
        Args:
            submission: Instance Submission
            grading_results: Résultats de la correction
            
        Returns:
            Result: Instance du résultat créé
        """
        skills_breakdown = {}
        for skill, performance in grading_results['skills_performance'].items():
            if performance['total_points'] > 0:
                percentage = (performance['earned_points'] / performance['total_points']) * 100
                skills_breakdown[skill] = {
                    'score': performance['earned_points'],
                    'percentage': round(percentage, 2),
                    'questions_answered': performance['questions_count'],
                    'questions_correct': performance['correct_count']
                }
        
        # Calculer les scores par type
        mcq_score = grading_results['questions_by_type']['mcq']['earned']
        true_false_score = grading_results['questions_by_type']['true_false']['earned']
        essay_score = grading_results['questions_by_type']['essay']['earned']
        
        # Créer le résultat
        result = Result.objects.create(
            submission=submission,
            student=submission.student,
            test=submission.test,
            total_score=grading_results['earned_points'],
            percentage_score=grading_results['percentage'],
            mcq_score=mcq_score,
            true_false_score=true_false_score,
            essay_score=essay_score,
            skills_breakdown=skills_breakdown
        )
        
        # Assigner une note
        result.grade = result.assign_grade()
        result.save()
        
        return result
    
    @staticmethod
    def update_user_profile_stats(student, result):
        """
        Met à jour les statistiques du profil utilisateur
        
        Args:
            student: Instance User
            result: Instance Result
        """
        profile, created = UserProfile.objects.get_or_create(user=student)
        
        # Mettre à jour les statistiques
        profile.total_tests_taken += 1
        
        # Recalculer la moyenne
        all_results = Result.objects.filter(student=student)
        if all_results.exists():
            avg = all_results.aggregate(Avg('percentage_score'))['percentage_score__avg']
            profile.average_score = round(avg, 2)
        
        # Ajouter à l'historique
        if not profile.performance_history:
            profile.performance_history = []
        
        profile.performance_history.append({
            'date': timezone.now().isoformat(),
            'score': result.percentage_score,
            'test_id': result.test.id,
            'test_title': result.test.title,
            'subject': result.test.subject
        })
        
        # Mettre à jour la progression par compétence
        if not profile.skill_progress:
            profile.skill_progress = {}
        
        for skill, performance in result.skills_breakdown.items():
            if skill not in profile.skill_progress:
                profile.skill_progress[skill] = {
                    'initial': performance['percentage'],
                    'current': performance['percentage'],
                    'tests_count': 1
                }
            else:
                profile.skill_progress[skill]['current'] = performance['percentage']
                profile.skill_progress[skill]['tests_count'] += 1
        
        profile.save()
