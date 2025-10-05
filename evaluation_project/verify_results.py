"""
Script pour tester l'affichage complet des résultats
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Result, Submission
from django.contrib.auth.models import User

# Chercher les résultats de etudiant1 pour le test React
student = User.objects.get(username='etudiant1')
results = Result.objects.filter(student=student, test_id=4).order_by('-created_at')

print("=" * 80)
print("VÉRIFICATION DES RÉSULTATS")
print("=" * 80)

if results.exists():
    for i, result in enumerate(results, 1):
        print(f"\n{'=' * 60}")
        print(f"Tentative #{i}")
        print(f"{'=' * 60}")
        print(f"Score: {result.total_score}/{result.test.total_points}")
        print(f"Pourcentage: {result.percentage_score}%")
        print(f"Note: {result.grade}")
        print(f"Date: {result.created_at}")
        
        if result.ai_analysis:
            print(f"\n--- Analyse IA ---")
            print(f"Feedback global: {result.ai_analysis.get('overall_feedback', 'N/A')}")
            print(f"Encouragement: {result.ai_analysis.get('encouragement', 'N/A')}")
            
            strengths = result.ai_analysis.get('strengths', [])
            print(f"\nPoints forts ({len(strengths)}):")
            for s in strengths:
                print(f"  ✓ {s}")
            
            weaknesses = result.ai_analysis.get('weaknesses', [])
            print(f"\nLacunes ({len(weaknesses)}):")
            for w in weaknesses:
                print(f"  ✗ {w}")
            
            recommendations = result.ai_analysis.get('recommendations', [])
            print(f"\nRecommandations ({len(recommendations)}):")
            for r in recommendations:
                print(f"  → {r}")
            
            chapters = result.ai_analysis.get('chapters_to_review', [])
            print(f"\nChapitres à revoir ({len(chapters)}):")
            for c in chapters:
                print(f"  📖 {c}")
            
            exercises = result.ai_analysis.get('exercises_to_redo', [])
            print(f"\nExercices recommandés ({len(exercises)}):")
            for e in exercises:
                print(f"  💪 {e.get('skill')}: {e.get('recommendation')}")
        else:
            print("\n⚠️ Aucune analyse IA générée")
else:
    print("\n⚠️ Aucun résultat trouvé pour etudiant1 sur le test React")
    print("Veuillez d'abord soumettre le test.")

print("\n" + "=" * 80)
