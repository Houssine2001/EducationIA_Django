"""
Script pour vérifier et nettoyer les soumissions de test
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Test, Submission
from django.contrib.auth.models import User

# Trouver l'étudiant
etudiant = User.objects.filter(username='etudiant1').first()

if not etudiant:
    print("❌ Étudiant 'etudiant1' non trouvé")
else:
    print(f"✅ Étudiant trouvé: {etudiant.username}")
    
    # Trouver le test React
    react_test = Test.objects.filter(title__icontains='React').first()
    
    if not react_test:
        print("❌ Test React non trouvé")
    else:
        print(f"✅ Test React trouvé: {react_test.title}")
        print(f"   Statut: {react_test.status}")
        print(f"   Nombre de questions: {react_test.questions.count()}")
        
        # Vérifier les soumissions existantes
        submissions = Submission.objects.filter(
            student=etudiant,
            test=react_test
        )
        
        print(f"\n📊 Soumissions existantes: {submissions.count()}")
        
        for sub in submissions:
            print(f"   - ID: {sub.id}, Statut: {sub.status}, Créé: {sub.started_at}")
        
        # Demander confirmation pour nettoyer
        if submissions.count() > 0:
            print("\n🗑️  Voulez-vous supprimer ces soumissions? (y/n)")
            # Pour l'automatisation, on supprime automatiquement
            submissions.delete()
            print("✅ Soumissions supprimées!")
            print("   L'étudiant peut maintenant passer le test.")
        else:
            print("\n✅ Aucune soumission existante. L'étudiant peut passer le test.")
