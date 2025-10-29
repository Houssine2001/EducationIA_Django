"""
Script de test pour l'analyse par concepts
Teste que le nouveau service ConceptAnalysisService fonctionne correctement
"""

import os
import django
from backend.mongodb_utils import get_mongodb_client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import Result
from evaluation.concept_analysis import ConceptAnalysisService
from pymongo import MongoClient
from django.conf import settings

def test_concept_analysis():
    """Test de l'analyse par concepts"""
    
    print("=" * 60)
    print("TEST: Analyse Détaillée par Concepts")
    print("=" * 60)
    
    # Récupérer un étudiant qui a des résultats
    user = User.objects.filter(profile__role='student').first()
    
    if not user:
        print("ERREUR: Aucun etudiant trouve dans la base de donnees")
        return
    
    print(f"\nOK Etudiant: {user.username}")
    
    # Récupérer les résultats manuels
    manual_results = Result.objects.filter(student=user)
    print(f"   - Résultats manuels: {manual_results.count()}")
    
    # Récupérer les soumissions IA
    client = get_mongodb_client()
    db = client[settings.MONGO_DB_NAME]
    
    ai_submissions = list(db.student_exercise_submissions.find({
        'student_id': user.id,
        'status': 'completed'
    }))
    print(f"   - Soumissions IA: {len(ai_submissions)}")
    
    if manual_results.count() == 0 and len(ai_submissions) == 0:
        print("\nAVERTISSEMENT: Pas de resultats trouves pour cet etudiant")
        client.close()
        return
    
    # Créer le service d'analyse
    print("\nCreation du service d'analyse...")
    analyzer = ConceptAnalysisService(user, db_connection=db)
    
    # Test 1: Analyser tests manuels
    if manual_results.count() > 0:
        print("\n--- Test 1: Analyse des tests MANUELS ---")
        manual_insights = analyzer.analyze_test_results(manual_results)
        
        for subject, insights in manual_insights.items():
            print(f"\n{subject}:")
            print(f"   Taux de reussite: {insights['overall_success_rate']}%")
            print(f"   Total questions: {insights['total_questions']}")
            
            if insights['strengths']:
                print(f"\n   POINTS FORTS:")
                for strength in insights['strengths'][:3]:
                    print(f"      - {strength['concept']}: {strength['success_rate']}% ({strength['correct']}/{strength['total']})")
            
            if insights['weaknesses']:
                print(f"\n   POINTS FAIBLES:")
                for weakness in insights['weaknesses'][:3]:
                    print(f"      - {weakness['concept']}: {weakness['success_rate']}% ({weakness['correct']}/{weakness['total']})")
            
            if insights['recommendations']:
                print(f"\n   RECOMMANDATIONS:")
                for rec in insights['recommendations'][:2]:
                    print(f"      - {rec}")
    
    # Test 2: Analyser tests IA
    if len(ai_submissions) > 0:
        print("\n--- Test 2: Analyse des tests IA ---")
        ai_insights = analyzer.analyze_ai_test_results(ai_submissions)
        
        for subject, insights in ai_insights.items():
            print(f"\n{subject}:")
            print(f"   Taux de reussite: {insights['overall_success_rate']}%")
            print(f"   Total questions: {insights['total_questions']}")
            
            if insights['strengths']:
                print(f"\n   POINTS FORTS:")
                for strength in insights['strengths'][:3]:
                    print(f"      - {strength['concept']}: {strength['success_rate']}% ({strength['correct']}/{strength['total']})")
            
            if insights['weaknesses']:
                print(f"\n   POINTS FAIBLES:")
                for weakness in insights['weaknesses'][:3]:
                    print(f"      - {weakness['concept']}: {weakness['success_rate']}% ({weakness['correct']}/{strength['total']})")
    
    # Test 3: Analyse combinée
    print("\n--- Test 3: Analyse COMBINEE (Manuels + IA) ---")
    combined_insights = analyzer.get_combined_analysis(manual_results, ai_submissions)
    
    for subject, insights in combined_insights.items():
        print(f"\n{subject}:")
        print(f"   Taux de reussite: {insights['overall_success_rate']}%")
        print(f"   Total questions: {insights['total_questions']}")
        print(f"   Tests manuels: {'Oui' if insights['has_manual_tests'] else 'Non'}")
        print(f"   Tests IA: {'Oui' if insights['has_ai_tests'] else 'Non'}")
        
        if insights['strengths']:
            print(f"\n   POINTS FORTS combinesemails:")
            for strength in insights['strengths'][:5]:
                print(f"      - {strength['concept']}: {strength['success_rate']}% ({strength['correct']}/{strength['total']})")
        
        if insights['weaknesses']:
            print(f"\n   POINTS FAIBLES combines:")
            for weakness in insights['weaknesses'][:5]:
                print(f"      - {weakness['concept']}: {weakness['success_rate']}% ({weakness['correct']}/{weakness['total']})")
        
        if insights['recommendations']:
            print(f"\n   RECOMMANDATIONS:")
            for rec in insights['recommendations']:
                print(f"      - {rec}")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("Test termine avec succes !")
    print("=" * 60)

if __name__ == '__main__':
    test_concept_analysis()
