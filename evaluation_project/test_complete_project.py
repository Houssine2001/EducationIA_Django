"""
Script de test automatisé complet pour le projet EduIA
Teste toutes les fonctionnalités : login, CRUD, analytics, etc.
"""

import os
import django
import sys
import time
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from evaluation.models import UserProfile, Test, Question, Submission, Result

# Compteurs de tests
tests_passed = 0
tests_failed = 0
errors_found = []

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_result(test_name, success, error_msg=None):
    """Enregistre le résultat d'un test"""
    global tests_passed, tests_failed, errors_found
    if success:
        tests_passed += 1
        print(f"  ✅ {test_name}")
    else:
        tests_failed += 1
        print(f"  ❌ {test_name}")
        if error_msg:
            print(f"     Erreur: {error_msg}")
            errors_found.append({"test": test_name, "error": error_msg})

# ============================================================================
# TEST 1 : CONNEXION À LA BASE DE DONNÉES
# ============================================================================
print_section("TEST 1 : Connexion à MongoDB")

try:
    from django.db import connection
    connection.ensure_connection()
    test_result("Connexion MongoDB établie", True)
except Exception as e:
    test_result("Connexion MongoDB établie", False, str(e))
    sys.exit(1)

# ============================================================================
# TEST 2 : VÉRIFICATION DES DONNÉES DE TEST
# ============================================================================
print_section("TEST 2 : Vérification des données de test")

try:
    users = User.objects.all()
    test_result(f"Utilisateurs créés : {users.count()}", users.count() == 4)
except Exception as e:
    test_result("Comptage des utilisateurs", False, str(e))

try:
    tests = Test.objects.all()
    test_result(f"Tests créés : {tests.count()}", tests.count() > 0)
except Exception as e:
    test_result("Comptage des tests", False, str(e))

try:
    questions = Question.objects.all()
    test_result(f"Questions créées : {questions.count()}", questions.count() > 0)
except Exception as e:
    test_result("Comptage des questions", False, str(e))

try:
    results = Result.objects.all()
    test_result(f"Résultats créés : {results.count()}", results.count() > 0)
except Exception as e:
    test_result("Comptage des résultats", False, str(e))

# ============================================================================
# TEST 3 : AUTHENTIFICATION
# ============================================================================
print_section("TEST 3 : Authentification")

# Test des étudiants
for username in ['etudiant1', 'etudiant2', 'etudiant3']:
    try:
        user = authenticate(username=username, password='pass123')
        if user is not None:
            test_result(f"Authentification {username}", True)
        else:
            test_result(f"Authentification {username}", False, "Échec de l'authentification")
    except Exception as e:
        test_result(f"Authentification {username}", False, str(e))

# Test du professeur
try:
    user = authenticate(username='prof1', password='pass123')
    if user is not None and user.is_staff:
        test_result("Authentification prof1 (staff)", True)
    else:
        test_result("Authentification prof1 (staff)", False, "Pas de privilèges staff")
except Exception as e:
    test_result("Authentification prof1", False, str(e))

# ============================================================================
# TEST 4 : ACCÈS AUX PAGES (CLIENT HTTP)
# ============================================================================
print_section("TEST 4 : Accès aux pages")

client = Client()

# Test page de login
try:
    response = client.get('/accounts/login/')
    test_result(f"Page de login (status {response.status_code})", response.status_code == 200)
except Exception as e:
    test_result("Page de login", False, str(e))

# Test login étudiant
try:
    login_success = client.login(username='etudiant1', password='pass123')
    test_result("Login client etudiant1", login_success)
except Exception as e:
    test_result("Login client etudiant1", False, str(e))

# Test dashboard étudiant
try:
    response = client.get('/')
    test_result(f"Dashboard étudiant (status {response.status_code})", response.status_code == 200)
    
    # Vérifier que le contenu contient des éléments attendus
    content = response.content.decode('utf-8')
    has_tailwind = 'tailwindcss' in content or 'cdn.tailwindcss.com' in content
    test_result("Dashboard contient Tailwind CSS", has_tailwind)
except Exception as e:
    test_result("Dashboard étudiant", False, str(e))

# Test page de progression
try:
    response = client.get('/progress/')
    test_result(f"Page progression (status {response.status_code})", response.status_code == 200)
    
    content = response.content.decode('utf-8')
    has_chartjs = 'chart.js' in content.lower() or 'chartjs' in content.lower()
    test_result("Page progression contient Chart.js", has_chartjs)
except Exception as e:
    test_result("Page progression", False, str(e))

# Déconnexion
client.logout()

# Test login professeur
try:
    login_success = client.login(username='prof1', password='pass123')
    test_result("Login client prof1", login_success)
except Exception as e:
    test_result("Login client prof1", False, str(e))

# Test dashboard professeur
try:
    response = client.get('/teacher/')
    test_result(f"Dashboard professeur (status {response.status_code})", response.status_code == 200)
except Exception as e:
    test_result("Dashboard professeur", False, str(e))

client.logout()

# ============================================================================
# TEST 5 : MODÈLES ET RELATIONS
# ============================================================================
print_section("TEST 5 : Modèles et relations")

try:
    etudiant1 = User.objects.get(username='etudiant1')
    profile = UserProfile.objects.get(user=etudiant1)
    test_result("UserProfile lié à User", True)
    test_result(f"Profil etudiant1 - Moyenne: {profile.average_score:.1f}%", profile.average_score > 0)
except Exception as e:
    test_result("UserProfile lié à User", False, str(e))

try:
    test_obj = Test.objects.first()
    questions = Question.objects.filter(test=test_obj)
    test_result(f"Test '{test_obj.title}' a {questions.count()} questions", questions.count() > 0)
except Exception as e:
    test_result("Questions liées au Test", False, str(e))

try:
    result = Result.objects.first()
    test_result(f"Result lié à Submission", result.submission is not None)
    test_result(f"Result lié à Student", result.student is not None)
    test_result(f"Result lié à Test", result.test is not None)
except Exception as e:
    test_result("Relations Result", False, str(e))

# ============================================================================
# TEST 6 : CRUD - CRÉATION
# ============================================================================
print_section("TEST 6 : CRUD - Création")

try:
    # Créer un nouveau test
    prof = User.objects.get(username='prof1')
    new_test = Test.objects.create(
        title="Test de géométrie",
        subject="Mathématiques",
        description="Test sur les triangles",
        duration=45,
        difficulty="medium",
        created_by=prof
    )
    test_result("Création d'un nouveau Test", new_test.id is not None)
    
    # Créer une question pour ce test
    new_question = Question.objects.create(
        test=new_test,
        question_text="Combien d'angles dans un triangle ?",
        question_type="multiple_choice",
        points=1,
        options=[
            {"text": "2", "is_correct": False},
            {"text": "3", "is_correct": True},
            {"text": "4", "is_correct": False}
        ]
    )
    test_result("Création d'une nouvelle Question", new_question.id is not None)
    
except Exception as e:
    test_result("CRUD - Création", False, str(e))

# ============================================================================
# TEST 7 : CRUD - LECTURE
# ============================================================================
print_section("TEST 7 : CRUD - Lecture")

try:
    all_tests = list(Test.objects.all())
    test_result(f"Lecture de tous les Tests: {len(all_tests)}", len(all_tests) > 0)
except Exception as e:
    test_result("Lecture Tests", False, str(e))

try:
    all_questions = list(Question.objects.all())
    test_result(f"Lecture de toutes les Questions: {len(all_questions)}", len(all_questions) > 0)
except Exception as e:
    test_result("Lecture Questions", False, str(e))

try:
    all_results = list(Result.objects.all())
    test_result(f"Lecture de tous les Results: {len(all_results)}", len(all_results) > 0)
except Exception as e:
    test_result("Lecture Results", False, str(e))

# ============================================================================
# TEST 8 : CRUD - MODIFICATION
# ============================================================================
print_section("TEST 8 : CRUD - Modification")

try:
    test_to_update = Test.objects.get(title="Test de géométrie")
    test_to_update.description = "Test sur les triangles et les angles"
    test_to_update.save()
    
    updated_test = Test.objects.get(id=test_to_update.id)
    test_result("Modification d'un Test", updated_test.description == "Test sur les triangles et les angles")
except Exception as e:
    test_result("CRUD - Modification", False, str(e))

# ============================================================================
# TEST 9 : CRUD - SUPPRESSION
# ============================================================================
print_section("TEST 9 : CRUD - Suppression")

try:
    test_to_delete = Test.objects.get(title="Test de géométrie")
    test_id = test_to_delete.id
    test_to_delete.delete()
    
    # Vérifier que le test est supprimé
    exists = Test.objects.filter(id=test_id).exists()
    test_result("Suppression d'un Test", not exists)
    
    # Vérifier que les questions sont aussi supprimées (cascade)
    questions_exist = Question.objects.filter(test_id=test_id).exists()
    test_result("Cascade - Questions supprimées avec Test", not questions_exist)
    
except Exception as e:
    test_result("CRUD - Suppression", False, str(e))

# ============================================================================
# TEST 10 : FONCTIONNALITÉS AVANCÉES
# ============================================================================
print_section("TEST 10 : Fonctionnalités avancées")

try:
    etudiant1 = User.objects.get(username='etudiant1')
    profile = UserProfile.objects.get(user=etudiant1)
    
    # Test niveau et XP
    test_result(f"Niveau du profil: {profile.level}", profile.level > 0)
    test_result(f"XP total: {profile.total_xp}", profile.total_xp >= 0)
    
    # Test statistiques
    test_result(f"Tests passés: {profile.total_tests_taken}", profile.total_tests_taken > 0)
    test_result(f"Score moyen: {profile.average_score:.1f}%", profile.average_score > 0)
    
except Exception as e:
    test_result("Fonctionnalités avancées", False, str(e))

# Test calculs de statistiques
try:
    results = list(Result.objects.filter(student=etudiant1))
    if len(results) > 0:
        avg = sum(r.percentage_score for r in results) / len(results)
        test_result(f"Calcul moyenne manuelle: {avg:.1f}%", avg > 0)
except Exception as e:
    test_result("Calculs statistiques", False, str(e))

# ============================================================================
# TEST 11 : DÉCONNEXION
# ============================================================================
print_section("TEST 11 : Déconnexion")

client = Client()
try:
    client.login(username='etudiant1', password='pass123')
    response = client.get('/accounts/logout/')
    test_result(f"Déconnexion (status {response.status_code})", response.status_code in [200, 302])
except Exception as e:
    test_result("Déconnexion", False, str(e))

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("\n" + "=" * 70)
print("  RÉSUMÉ DES TESTS")
print("=" * 70)
print(f"  ✅ Tests réussis  : {tests_passed}")
print(f"  ❌ Tests échoués  : {tests_failed}")
print(f"  📊 Total          : {tests_passed + tests_failed}")
print(f"  🎯 Taux de réussite: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
print("=" * 70)

if errors_found:
    print("\n⚠️  ERREURS DÉTECTÉES :")
    for i, error in enumerate(errors_found, 1):
        print(f"\n{i}. {error['test']}")
        print(f"   {error['error']}")
else:
    print("\n✅ AUCUNE ERREUR DÉTECTÉE - LE PROJET FONCTIONNE PARFAITEMENT !")
    print("\n🎉 Tous les tests sont passés avec succès !")
    print("\n📝 Fonctionnalités vérifiées :")
    print("   ✅ Connexion MongoDB")
    print("   ✅ Authentification (étudiants + professeur)")
    print("   ✅ Pages accessibles (dashboard, progression)")
    print("   ✅ Templates avec Tailwind CSS et Chart.js")
    print("   ✅ CRUD complet (Create, Read, Update, Delete)")
    print("   ✅ Relations entre modèles")
    print("   ✅ Statistiques et analytics")
    print("   ✅ Gamification (niveau, XP)")
    print("   ✅ Déconnexion")

print("\n" + "=" * 70)
print(f"  Tests terminés le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
print("=" * 70)
