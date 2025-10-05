"""
Script pour recalculer et corriger les scores des soumissions existantes
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Submission, Result, Question
from evaluation.services import AutoGrading, ResultService
from django.contrib.auth.models import User

print("=" * 80)
print("RECALCUL DES SCORES POUR LES SOUMISSIONS EXISTANTES")
print("=" * 80)

# Trouver toutes les soumissions déjà notées
submissions = Submission.objects.filter(status='submitted')

for submission in submissions:
    print(f"\n{'='*60}")
    print(f"Soumission #{submission.id} - Test: {submission.test.title}")
    print(f"Étudiant: {submission.student.username}")
    print(f"{'='*60}")
    
    # Vérifier les réponses
    if not submission.answers:
        print("⚠️ Pas de réponses enregistrées")
        continue
    
    print(f"\nRéponses enregistrées:")
    for q_id, answer_data in submission.answers.items():
        question = Question.objects.get(id=q_id)
        if isinstance(answer_data, dict):
            student_ans = answer_data.get('answer')
        else:
            student_ans = answer_data
        print(f"  Question {q_id}: Réponse = '{student_ans}'")
        
        # Afficher les options de la question
        if question.options:
            print(f"    Options disponibles:")
            for opt in question.options:
                marker = " ✓" if opt.get('is_correct') else ""
                print(f"      {opt['id']}: {opt['text'][:50]}{marker}")
    
    # Recalculer le score
    print(f"\n🔄 Recalcul du score...")
    grading_results = AutoGrading.grade_submission(submission)
    
    print(f"  Total points: {grading_results['total_points']}")
    print(f"  Points gagnés: {grading_results['earned_points']}")
    print(f"  Pourcentage: {grading_results['percentage']:.1f}%")
    print(f"  Questions correctes: {grading_results['correct_count']}/{grading_results['total_count']}")
    
    # Mettre à jour ou créer le résultat
    try:
        result = Result.objects.get(submission=submission)
        print(f"\n  Ancien score: {result.total_score}/{result.test.total_points} ({result.percentage_score:.1f}%)")
        
        # Mettre à jour
        result.total_score = grading_results['earned_points']
        result.percentage_score = grading_results['percentage']
        result.mcq_score = grading_results['questions_by_type']['mcq']['earned']
        result.true_false_score = grading_results['questions_by_type']['true_false']['earned']
        result.grade = result.assign_grade()
        result.save()
        
        print(f"  ✅ Nouveau score: {result.total_score}/{result.test.total_points} ({result.percentage_score:.1f}%)")
        print(f"  Note: {result.grade}")
        
    except Result.DoesNotExist:
        print(f"  ⚠️ Pas de résultat trouvé - création...")
        result = ResultService.create_detailed_result(submission, grading_results)
        print(f"  ✅ Résultat créé: {result.total_score}/{result.test.total_points} ({result.percentage_score:.1f}%)")

print("\n" + "=" * 80)
print("✅ RECALCUL TERMINÉ")
print("=" * 80)
