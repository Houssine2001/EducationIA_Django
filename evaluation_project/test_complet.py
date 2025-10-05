import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 70)
print("TEST COMPLET DES URLS")
print("=" * 70)

client = Client()

# Login
print("\n1. LOGIN")
success = client.login(username='etudiant1', password='pass123')
print(f"   Login: {'OK' if success else 'ERREUR'}")

if not success:
    print("❌ Impossible de continuer sans login")
    exit(1)

# Tests des pages principales
pages = [
    ('/', 'Dashboard étudiant'),
    ('/progress/', 'Page progression'),
    ('/result/1/', 'Détail résultat 1'),
    ('/result/2/', 'Détail résultat 2'),
    ('/result/3/', 'Détail résultat 3'),
    ('/test/1/', 'Test 1 détail'),
    ('/test/2/', 'Test 2 détail'),
    ('/test/3/', 'Test 3 détail'),
]

print("\n2. PAGES ÉTUDIANT")
for url, name in pages:
    try:
        response = client.get(url)
        if response.status_code == 200:
            print(f"   ✅ {name}: OK")
        else:
            print(f"   ❌ {name}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: ERREUR - {str(e)[:60]}")

# Test logout
print("\n3. DÉCONNEXION")
try:
    response = client.post('/accounts/logout/')
    if response.status_code in [200, 302]:
        print(f"   ✅ Logout: OK (redirect {response.status_code})")
    else:
        print(f"   ❌ Logout: {response.status_code}")
except Exception as e:
    print(f"   ❌ Logout: ERREUR - {str(e)}")

# Vérifier qu'on est déconnecté
response = client.get('/')
if response.status_code == 302:
    print("   ✅ Redirection après logout: OK")
else:
    print(f"   ❌ Toujours connecté: {response.status_code}")

print("\n" + "=" * 70)
print("TESTS TERMINÉS")
print("=" * 70)
