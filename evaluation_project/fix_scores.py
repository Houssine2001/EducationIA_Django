import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Submission, Result, Question
from evaluation.services import AutoGrading

# Corriger les soumissions #10 et #11
submission_ids = [10, 11]

for sub_id in submission_ids:
    try:
        submission = Submission.objects.get(id=sub_id)
        print(f"\n{'='*70}")
        print(f"Soumission #{sub_id} - {submission.test.title}")
        print(f"Étudiant: {submission.student.username}")
        print(f"{'='*70}")
        
        # Afficher les réponses actuelles
        print("\nRéponses enregistrées:")
        for q_id, answer_data in submission.answers.items():
            question = Question.objects.get(id=q_id)
            if isinstance(answer_data, dict):
                student_ans = answer_data.get('answer')
            else:
                student_ans = answer_data
            
            print(f"\nQuestion {q_id}: {question.question_text[:80]}")
            print(f"  Réponse de l'étudiant: '{student_ans}' (type: {type(student_ans).__name__})")
            
            if question.options:
                print(f"  Options:")
                for i, opt in enumerate(question.options):
                    correct_marker = " ✅ CORRECT" if opt.get('is_correct') else ""
                    print(f"    {opt['id']} (index {i}): {opt['text'][:60]}{correct_marker}")
                
                # Convertir index en ID si nécessaire
                if student_ans is not None:
                    try:
                        # Si c'est un index numérique, convertir en ID
                        index = int(student_ans)
                        if 0 <= index < len(question.options):
                            new_answer = question.options[index]['id']
                            print(f"  ⚠️ Conversion nécessaire: index {index} → ID '{new_answer}'")
                            
                            # Mettre à jour la réponse
                            if isinstance(submission.answers[q_id], dict):
                                submission.answers[q_id]['answer'] = new_answer
                            else:
                                submission.answers[q_id] = {'answer': new_answer}
                        else:
                            print(f"  ✅ Réponse déjà au bon format: '{student_ans}'")
                    except (ValueError, TypeError):
                        # C'est déjà un ID (A, B, C, D)
                        print(f"  ✅ Réponse déjà au bon format: '{student_ans}'")
        
        # Sauvegarder les réponses converties
        submission.save()
        print("\n✅ Réponses converties et sauvegardées")
        
        # Recalculer le score
        print("\n🔄 Recalcul du score...")
        grading_results = AutoGrading.grade_submission(submission)
        
        print(f"  Total points possibles: {grading_results['total_points']}")
        print(f"  Points gagnés: {grading_results['earned_points']}")
        print(f"  Pourcentage: {grading_results['percentage']:.1f}%")
        print(f"  Questions correctes: {grading_results['correct_count']}/{grading_results['total_count']}")
        
        # Mettre à jour le résultat
        result = Result.objects.get(submission=submission)
        old_score = result.total_score
        old_percentage = result.percentage_score
        
        result.total_score = grading_results['earned_points']
        result.percentage_score = grading_results['percentage']
        result.mcq_score = grading_results['questions_by_type']['mcq']['earned']
        result.grade = result.assign_grade()
        result.save()
        
        print(f"\n📊 Comparaison:")
        print(f"  Ancien score: {old_score} pts ({old_percentage:.1f}%)")
        print(f"  Nouveau score: {result.total_score} pts ({result.percentage_score:.1f}%)")
        print(f"  Note: {result.grade}")
        
        # Régénérer l'analyse IA
        print("\n🤖 Régénération de l'analyse IA...")
        from evaluation.ai_feedback import AIFeedbackGenerator
        ai_feedback = AIFeedbackGenerator.generate_comprehensive_feedback(result, submission)
        result.ai_analysis = ai_feedback
        result.recommendations = ai_feedback.get('recommendations', [])
        result.learning_gaps = ai_feedback.get('weaknesses', [])
        result.save()
        print("  ✅ Analyse IA mise à jour")
        
    except Submission.DoesNotExist:
        print(f"⚠️ Soumission #{sub_id} introuvable")
    except Exception as e:
        print(f"❌ Erreur pour soumission #{sub_id}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("✅ CORRECTION TERMINÉE")
print("="*70)
