"""
Script de test pour vérifier l'analyse IA des concepts
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.ai_concept_analyzer import AIConceptAnalyzer


def test_analysis_with_different_scores():
    """Test l'analyse avec différents scores"""
    
    analyzer = AIConceptAnalyzer()
    
    # Test 1: Score parfait (100%)
    print("\n" + "="*80)
    print("TEST 1: Score parfait (100%)")
    print("="*80)
    
    questions_perfect = [
        {'concept': 'Algèbre', 'is_correct': True},
        {'concept': 'Algèbre', 'is_correct': True},
        {'concept': 'Géométrie', 'is_correct': True},
        {'concept': 'Géométrie', 'is_correct': True},
        {'concept': 'Analyse', 'is_correct': True},
    ]
    
    result1 = analyzer._generate_basic_analysis(questions_perfect, 100.0, 'Mathématiques')
    print(f"\n✅ Points forts ({len(result1['strengths'])}):")
    for i, s in enumerate(result1['strengths'], 1):
        print(f"   {i}. {s}")
    
    print(f"\n⚠️ Points faibles ({len(result1['weaknesses'])}):")
    for i, w in enumerate(result1['weaknesses'], 1):
        print(f"   {i}. {w}")
    
    print(f"\n💡 Recommandations ({len(result1['recommendations'])}):")
    for i, r in enumerate(result1['recommendations'], 1):
        print(f"   {i}. {r}")
    
    print(f"\n📝 Feedback: {result1['detailed_feedback']}")
    
    # Test 2: Score moyen (60%)
    print("\n" + "="*80)
    print("TEST 2: Score moyen (60%)")
    print("="*80)
    
    questions_medium = [
        {'concept': 'Algèbre', 'is_correct': True},
        {'concept': 'Algèbre', 'is_correct': False},
        {'concept': 'Géométrie', 'is_correct': True},
        {'concept': 'Géométrie', 'is_correct': False},
        {'concept': 'Analyse', 'is_correct': True},
        {'concept': 'Analyse', 'is_correct': False},
        {'concept': 'Probabilités', 'is_correct': False},
        {'concept': 'Probabilités', 'is_correct': False},
        {'concept': 'Statistiques', 'is_correct': True},
        {'concept': 'Statistiques', 'is_correct': False},
    ]
    
    result2 = analyzer._generate_basic_analysis(questions_medium, 60.0, 'Mathématiques')
    print(f"\n✅ Points forts ({len(result2['strengths'])}):")
    for i, s in enumerate(result2['strengths'], 1):
        print(f"   {i}. {s}")
    
    print(f"\n⚠️ Points faibles ({len(result2['weaknesses'])}):")
    for i, w in enumerate(result2['weaknesses'], 1):
        print(f"   {i}. {w}")
    
    print(f"\n💡 Recommandations ({len(result2['recommendations'])}):")
    for i, r in enumerate(result2['recommendations'], 1):
        print(f"   {i}. {r}")
    
    print(f"\n📝 Feedback: {result2['detailed_feedback']}")
    
    # Test 3: Score faible (30%)
    print("\n" + "="*80)
    print("TEST 3: Score faible (30%)")
    print("="*80)
    
    questions_low = [
        {'concept': 'Algèbre', 'is_correct': False},
        {'concept': 'Algèbre', 'is_correct': False},
        {'concept': 'Algèbre', 'is_correct': True},
        {'concept': 'Géométrie', 'is_correct': False},
        {'concept': 'Géométrie', 'is_correct': False},
        {'concept': 'Analyse', 'is_correct': False},
        {'concept': 'Analyse', 'is_correct': False},
        {'concept': 'Probabilités', 'is_correct': False},
        {'concept': 'Probabilités', 'is_correct': True},
        {'concept': 'Statistiques', 'is_correct': False},
    ]
    
    result3 = analyzer._generate_basic_analysis(questions_low, 30.0, 'Mathématiques')
    print(f"\n✅ Points forts ({len(result3['strengths'])}):")
    for i, s in enumerate(result3['strengths'], 1):
        print(f"   {i}. {s}")
    
    print(f"\n⚠️ Points faibles ({len(result3['weaknesses'])}):")
    for i, w in enumerate(result3['weaknesses'], 1):
        print(f"   {i}. {w}")
    
    print(f"\n💡 Recommandations ({len(result3['recommendations'])}):")
    for i, r in enumerate(result3['recommendations'], 1):
        print(f"   {i}. {r}")
    
    print(f"\n📝 Feedback: {result3['detailed_feedback']}")
    
    # Vérifications
    print("\n" + "="*80)
    print("VÉRIFICATIONS")
    print("="*80)
    
    all_passed = True
    
    # Vérifier que tous les résultats ont au moins 3 éléments
    for i, result in enumerate([result1, result2, result3], 1):
        print(f"\nTest {i}:")
        
        if len(result['strengths']) >= 3:
            print(f"   ✅ Points forts: {len(result['strengths'])} >= 3")
        else:
            print(f"   ❌ Points forts: {len(result['strengths'])} < 3")
            all_passed = False
        
        if len(result['weaknesses']) >= 3:
            print(f"   ✅ Points faibles: {len(result['weaknesses'])} >= 3")
        else:
            print(f"   ❌ Points faibles: {len(result['weaknesses'])} < 3")
            all_passed = False
        
        if len(result['recommendations']) >= 3:
            print(f"   ✅ Recommandations: {len(result['recommendations'])} >= 3")
        else:
            print(f"   ❌ Recommandations: {len(result['recommendations'])} < 3")
            all_passed = False
        
        # Vérifier qu'il n'y a pas de messages génériques
        generic_strengths = [
            "Pas encore de concepts maîtrisés",
            "Continuez vos efforts"
        ]
        generic_weaknesses = [
            "Aucune faiblesse majeure détectée"
        ]
        
        has_generic = False
        for gs in generic_strengths:
            if any(gs in s for s in result['strengths']):
                print(f"   ⚠️ Message générique trouvé dans strengths: '{gs}'")
                has_generic = True
        
        for gw in generic_weaknesses:
            if any(gw in w for w in result['weaknesses']):
                print(f"   ⚠️ Message générique trouvé dans weaknesses: '{gw}'")
                has_generic = True
        
        if not has_generic:
            print(f"   ✅ Pas de messages génériques")
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*80 + "\n")


if __name__ == '__main__':
    test_analysis_with_different_scores()
