"""
Script pour mettre à jour le statut du test React
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Test
from django.utils import timezone

# Trouver le test React
react_test = Test.objects.filter(title__icontains='React').first()

if react_test:
    print(f"Test trouvé: {react_test.title}")
    print(f"Statut actuel: {react_test.status}")
    
    # Mettre à jour le statut
    react_test.status = 'published'
    react_test.published_at = timezone.now()
    react_test.save()
    
    print(f"✅ Test mis à jour avec succès!")
    print(f"Nouveau statut: {react_test.status}")
    print(f"Publié le: {react_test.published_at}")
else:
    print("❌ Aucun test React trouvé")
    
    # Afficher tous les tests
    print("\nTests disponibles:")
    for test in Test.objects.all():
        print(f"- {test.title} (Statut: {test.status})")
