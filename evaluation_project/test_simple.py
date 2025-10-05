import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from evaluation.models import Test, Question, Result, Submission, UserProfile

print("=" * 70)
print("TEST FINAL DU PROJET")
print("=" * 70)

# Test 1: Base de donnees
print("\n1. BASE DE DONNEES:")
print(f"   Utilisateurs: {User.objects.count()}")
print(f"   Profils: {UserProfile.objects.count()}")
print(f"   Tests: {Test.objects.count()}")
print(f"   Questions: {Question.objects.count()}")
print(f"   Resultats: {Result.objects.count()}")
print(f"   Soumissions: {Submission.objects.count()}")

# Test 2: Authentication
client = Client()
print("\n2. AUTHENTICATION:")

response = client.get('/accounts/login/')
print(f"   Page login: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

success = client.login(username='etudiant1', password='pass123')
print(f"   Login etudiant1: {'OK' if success else 'ERREUR'}")

if success:
    response = client.get('/')
    print(f"   Dashboard etudiant: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")
    
    response = client.get('/progress/')
    print(f"   Page progression: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

client.logout()

# Test 3: Professeur
print("\n3. ESPACE PROFESSEUR:")
success = client.login(username='prof1', password='pass123')
print(f"   Login prof1: {'OK' if success else 'ERREUR'}")

if success:
    response = client.get('/teacher/')
    print(f"   Dashboard prof: {response.status_code} - {'OK' if response.status_code == 200 else 'ERREUR'}")

print("\n" + "=" * 70)
print("TOUS LES TESTS TERMINES")
print("=" * 70)
