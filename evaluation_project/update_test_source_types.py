"""
Script pour mettre à jour les tests existants avec source_type
"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Test
from exercise_generator.models import GeneratedTest

def update_test_source_types():
    """
    Met à jour le champ source_type pour tous les tests existants
    """
    print("🔄 Mise à jour des types de source des tests...")
    
    # 1. Tous les tests existants sont manuels par défaut
    manual_tests = Test.objects.all()
    manual_count = 0
    
    for test in manual_tests:
        if not hasattr(test, 'source_type') or not test.source_type:
            test.source_type = 'manual'
            test.save(update_fields=['source_type'])
            manual_count += 1
    
    print(f"✅ {manual_count} tests marqués comme 'manual'")
    
    # 2. Si on a des GeneratedTest avec un lien vers Test
    generated_tests = GeneratedTest.objects.filter(evaluation_test_id__isnull=False)
    ai_count = 0
    
    for gen_test in generated_tests:
        try:
            test = Test.objects.get(id=gen_test.evaluation_test_id)
            test.source_type = 'ai_generated'
            test.save(update_fields=['source_type'])
            ai_count += 1
            print(f"  🤖 Test '{test.title}' marqué comme 'ai_generated'")
        except Test.DoesNotExist:
            print(f"  ⚠️  Test {gen_test.evaluation_test_id} introuvable")
    
    print(f"✅ {ai_count} tests marqués comme 'ai_generated'")
    
    # 3. Résumé
    print("\n📊 Résumé:")
    print(f"  Total tests: {Test.objects.count()}")
    print(f"  Tests manuels: {Test.objects.filter(source_type='manual').count()}")
    print(f"  Tests IA: {Test.objects.filter(source_type='ai_generated').count()}")

if __name__ == '__main__':
    update_test_source_types()
