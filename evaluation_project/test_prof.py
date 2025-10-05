import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 70)
print("TEST ESPACE PROFESSEUR")
print("=" * 70)

client = Client()

# Login prof
print("\n1. LOGIN PROFESSEUR")
success = client.login(username='prof1', password='pass123')
print(f"   Login prof1: {'OK' if success else 'ERREUR'}")

if not success:
    print("❌ Impossible de continuer")
    exit(1)

# Tests des pages prof
pages = [
    ('/teacher/', 'Dashboard professeur'),
    ('/teacher/test/create/', 'Créer un test'),
    ('/teacher/test/1/edit/', 'Modifier test 1'),
    ('/teacher/test/2/edit/', 'Modifier test 2'),
    ('/teacher/test/3/edit/', 'Modifier test 3'),
]

print("\n2. PAGES PROFESSEUR")
for url, name in pages:
    try:
        response = client.get(url)
        if response.status_code == 200:
            print(f"   ✅ {name}: OK")
        elif response.status_code == 404:
            print(f"   ⚠️  {name}: Not Found (404)")
        else:
            print(f"   ❌ {name}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: ERREUR - {str(e)[:60]}")

print("\n" + "=" * 70)
print("TESTS TERMINÉS")
print("=" * 70)
