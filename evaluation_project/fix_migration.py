"""
Script pour corriger le problème de migration PerformanceTrend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from analytics_dashboard.models import PerformanceTrend
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('localhost', 27017)
db = client['django_education']

# Supprimer l'ancienne collection PerformanceTrend si elle existe
if 'analytics_dashboard_performancetrend' in db.list_collection_names():
    print("Suppression de l'ancienne collection PerformanceTrend...")
    db['analytics_dashboard_performancetrend'].drop()
    print("✅ Collection supprimée")
else:
    print("ℹ️ Aucune collection PerformanceTrend existante")

print("\n✅ Prêt pour la migration. Exécutez maintenant:")
print("   python manage.py makemigrations analytics_dashboard")
print("   python manage.py migrate analytics_dashboard")
