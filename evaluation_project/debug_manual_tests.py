"""
Script de debug pour vérifier pourquoi manual_concept_insights est vide
"""
import os
import django
from backend.mongodb_utils import get_mongodb_client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from evaluation.models import Result, UserProfile
from evaluation.concept_analysis import ConceptAnalysisService
from pymongo import MongoClient
from django.conf import settings

User = get_user_model()

# Trouver un étudiant avec des résultats
students = User.objects.filter(profile__role='student')
print(f"📊 Trouvé {students.count()} étudiants")

for student in students[:3]:
    print(f"\n{'='*60}")
    print(f"👤 Étudiant: {student.username} (ID: {student.id})")
    
    results = Result.objects.filter(student=student).select_related('test')
    print(f"📝 Résultats manuels: {results.count()}")
    
    if results.count() > 0:
        # Afficher quelques résultats
        for r in results[:3]:
            print(f"   - {r.test.title}: {r.percentage_score}% (ID: {r.id})")
        
        # Tester l'analyse par concepts
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        analyzer = ConceptAnalysisService(student, db_connection=db)
        manual_insights = analyzer.analyze_test_results(results)
        
        print(f"\n🔍 ANALYSE PAR CONCEPTS:")
        print(f"   Type: {type(manual_insights)}")
        print(f"   Vide?: {not manual_insights}")
        print(f"   Contenu: {manual_insights}")
        
        if manual_insights:
            print(f"\n📈 Détails par matière:")
            for subject, insights in manual_insights.items():
                print(f"   {subject}:")
                print(f"      - Taux de réussite: {insights.get('overall_success_rate')}%")
                print(f"      - Total questions: {insights.get('total_questions')}")
                print(f"      - Points forts: {len(insights.get('strengths', []))}")
                print(f"      - Points faibles: {len(insights.get('weaknesses', []))}")
        else:
            print("   ⚠️ manual_insights est vide!")
            
            # Déboguer plus en profondeur
            print(f"\n🔬 DÉBOGAGE APPROFONDI:")
            for result in results[:2]:
                print(f"\n   Test: {result.test.title}")
                print(f"      - Subject: {result.test.subject}")
                print(f"      - Questions count: {result.test.questions.count()}")
                
                # Vérifier les soumissions
                try:
                    submission = result.submission
                    if submission:
                        print(f"      - Submission ID: {submission.id}")
                        print(f"      - Has answers?: {bool(submission.answers)}")
                        if submission.answers:
                            import json
                            answers = json.loads(submission.answers) if isinstance(submission.answers, str) else submission.answers
                            print(f"      - Answers count: {len(answers)}")
                    else:
                        print(f"      - ⚠️ NO SUBMISSION!")
                except Exception as e:
                    print(f"      - ⚠️ Error getting submission: {e}")
        
        client.close()
        break  # Tester seulement le premier étudiant avec des résultats

print(f"\n{'='*60}\n")
