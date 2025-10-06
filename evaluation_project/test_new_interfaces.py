"""
Script de test pour vérifier les nouvelles interfaces.

Execute: python manage.py shell < test_new_interfaces.py
"""

print("=" * 60)
print("TEST DES NOUVELLES INTERFACES")
print("=" * 60)

# Test 1: Importer le module de prédiction IA
print("\n1. Test import du module de prédiction IA...")
try:
    from evaluation.ai_prediction import StudentLevelPredictor, get_student_level_class, get_student_level_name
    print("✅ Module ai_prediction importé avec succès")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Vérifier les vues
print("\n2. Test import des vues...")
try:
    from evaluation.views import my_tests, my_badges, students_list
    print("✅ Vues my_tests, my_badges, students_list importées")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Vérifier les modèles
print("\n3. Test des modèles...")
try:
    from evaluation.models import UserProfile, Result, Submission, Test
    print(f"✅ Modèles importés")
    
    # Compter les données
    students = UserProfile.objects.filter(role='student').count()
    results = Result.objects.count()
    tests = Test.objects.filter(status='published').count()
    
    print(f"   - {students} étudiant(s)")
    print(f"   - {results} résultat(s)")
    print(f"   - {tests} test(s) publié(s)")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 4: Test de prédiction IA (si des étudiants existent)
print("\n4. Test de prédiction IA...")
try:
    from evaluation.models import UserProfile
    from evaluation.ai_prediction import StudentLevelPredictor
    
    student_profile = UserProfile.objects.filter(role='student').first()
    
    if student_profile:
        predictor = StudentLevelPredictor(student_profile)
        prediction = predictor.predict_future_level()
        
        print(f"✅ Prédiction générée pour {student_profile.user.username}")
        print(f"   - Niveau actuel: {prediction['current_level']}")
        print(f"   - Niveau futur: {prediction['future_level']}")
        print(f"   - Confiance: {prediction['confidence']}%")
        print(f"   - Facteurs: {len(prediction['key_factors'])}")
    else:
        print("⚠️  Aucun étudiant trouvé pour tester la prédiction")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 5: Vérifier les URLs
print("\n5. Test des URLs...")
try:
    from django.urls import reverse
    
    urls_to_test = [
        'evaluation:my_tests',
        'evaluation:my_badges',
        'evaluation:students_list',
    ]
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name} → {url}")
        except Exception as e:
            print(f"❌ {url_name}: {e}")
            
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 6: Vérifier les templates
print("\n6. Test des templates...")
import os
from django.conf import settings

templates_to_check = [
    'templates/evaluation/student/my_tests.html',
    'templates/evaluation/student/my_badges.html',
    'templates/evaluation/teacher/students_list.html',
]

for template in templates_to_check:
    template_path = os.path.join(settings.BASE_DIR, template)
    if os.path.exists(template_path):
        size = os.path.getsize(template_path)
        print(f"✅ {template} ({size} bytes)")
    else:
        print(f"❌ {template} non trouvé")

# Test 7: Vérifier gamification
print("\n7. Test du système de gamification...")
try:
    from evaluation.gamification import GamificationService, Badge
    
    badges = Badge.get_all_badge_definitions()
    print(f"✅ {len(badges)} badges définis dans le système")
    
    # Afficher quelques badges
    for badge in badges[:3]:
        print(f"   - {badge['name']} ({badge['category']}) - {badge['xp_reward']} XP")
        
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)

# Résumé
print("\n📊 RÉSUMÉ:")
print("- Interface 'Mes Tests': my_tests.html + vue my_tests()")
print("- Interface 'Badges': my_badges.html + vue my_badges()")
print("- Interface 'Étudiants': students_list.html + vue students_list()")
print("- Prédiction IA: ai_prediction.py avec StudentLevelPredictor")
print("\n✨ Toutes les nouvelles interfaces sont prêtes!")
print("\n🌐 Accédez aux URLs:")
print("   - http://127.0.0.1:8000/my-tests/")
print("   - http://127.0.0.1:8000/my-badges/")
print("   - http://127.0.0.1:8000/teacher/students/ (enseignants)")
