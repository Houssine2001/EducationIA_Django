"""
Commande pour nettoyer toutes les données de test.

Supprime :
- Tous les résultats
- Toutes les soumissions
- Toutes les questions
- Tous les tests
- Tous les étudiants de test (etudiant1, etudiant2, etc.)
- Tous les profils associés

Usage:
    python manage.py cleanup_test_data
    python manage.py cleanup_test_data --confirm
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evaluation.models import Test, Question, Submission, Result, UserProfile


class Command(BaseCommand):
    help = 'Nettoyer toutes les données de test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmer la suppression (requis)'
        )

    def handle(self, *args, **options):
        """Point d'entrée de la commande"""
        if not options.get('confirm'):
            self.stdout.write(self.style.WARNING(
                '⚠️  ATTENTION: Cette commande va SUPPRIMER toutes les données de test !'
            ))
            self.stdout.write('\nPour confirmer, exécutez :')
            self.stdout.write(self.style.SUCCESS('python manage.py cleanup_test_data --confirm'))
            return
        
        self.stdout.write(self.style.WARNING('\n🗑️  Nettoyage des données de test...\n'))
        
        # Compteurs
        counts = {
            'results': 0,
            'submissions': 0,
            'questions': 0,
            'tests': 0,
            'users': 0,
            'profiles': 0
        }
        
        # 1. Supprimer tous les résultats
        results = Result.objects.all()
        counts['results'] = results.count()
        results.delete()
        self.stdout.write(f'  ✓ {counts["results"]} résultats supprimés')
        
        # 2. Supprimer toutes les soumissions
        submissions = Submission.objects.all()
        counts['submissions'] = submissions.count()
        submissions.delete()
        self.stdout.write(f'  ✓ {counts["submissions"]} soumissions supprimées')
        
        # 3. Supprimer toutes les questions
        questions = Question.objects.all()
        counts['questions'] = questions.count()
        questions.delete()
        self.stdout.write(f'  ✓ {counts["questions"]} questions supprimées')
        
        # 4. Supprimer tous les tests
        tests = Test.objects.all()
        counts['tests'] = tests.count()
        tests.delete()
        self.stdout.write(f'  ✓ {counts["tests"]} tests supprimés')
        
        # 5. Supprimer les étudiants de test
        test_users = User.objects.filter(
            username__startswith='etudiant'
        ).exclude(is_staff=True).exclude(is_superuser=True)
        counts['users'] = test_users.count()
        test_users.delete()
        self.stdout.write(f'  ✓ {counts["users"]} utilisateurs de test supprimés')
        
        # 6. Nettoyer les profils orphelins
        orphan_profiles = UserProfile.objects.filter(user__isnull=True)
        orphan_count = orphan_profiles.count()
        orphan_profiles.delete()
        if orphan_count > 0:
            self.stdout.write(f'  ✓ {orphan_count} profils orphelins supprimés')
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Nettoyage terminé !\n'))
        self.stdout.write('Résumé:')
        for key, value in counts.items():
            self.stdout.write(f'  - {key}: {value}')
        
        self.stdout.write(self.style.SUCCESS('\n✨ Base de données propre ! Prête pour de nouvelles données.\n'))
