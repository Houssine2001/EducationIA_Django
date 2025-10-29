"""
Commande pour initialiser le système de badges et créer des données de test
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from evaluation.models import UserProfile, Test, Question, Result, Submission
from evaluation.gamification import GamificationService
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialise le système de badges avec des données de test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-tests',
            action='store_true',
            help='Créer des tests de démonstration',
        )
        parser.add_argument(
            '--student-username',
            type=str,
            help='Username de l\'étudiant à tester',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Initialisation du système de badges...\n'))

        # 1. Créer ou récupérer un étudiant de test
        if options.get('student_username'):
            try:
                student = User.objects.get(username=options['student_username'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Étudiant {options["student_username"]} non trouvé'))
                return
        else:
            # Créer un étudiant de test
            student, created = User.objects.get_or_create(
                username='student_test',
                defaults={
                    'email': 'student@test.com',
                    'first_name': 'Étudiant',
                    'last_name': 'Test'
                }
            )
            if created:
                student.set_password('test123')
                student.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Étudiant créé: {student.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Étudiant existant: {student.username}'))

        # 2. Créer ou récupérer le profil
        profile, created = UserProfile.objects.get_or_create(
            user=student,
            defaults={'role': 'student'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Profil créé'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Profil existant'))

        # 3. Initialiser les badges (vide au départ)
        if not profile.badges:
            profile.badges = []
            profile.save()
            self.stdout.write(self.style.SUCCESS('✅ Liste de badges initialisée'))

        # 4. Créer des tests de démonstration si demandé
        if options.get('create_tests'):
            self.create_demo_tests(student)

        # 5. Afficher la liste des badges disponibles
        self.stdout.write(self.style.SUCCESS('\n📋 Badges disponibles:\n'))
        
        service = GamificationService(profile)
        for badge_id, badge_data in service.BADGES.items():
            rarity_colors = {
                'common': self.style.SUCCESS,
                'uncommon': self.style.HTTP_INFO,
                'rare': self.style.WARNING,
                'epic': self.style.HTTP_NOT_MODIFIED,
                'legendary': self.style.ERROR
            }
            color_func = rarity_colors.get(badge_data['rarity'], self.style.SUCCESS)
            
            self.stdout.write(
                f"  {badge_data['icon']} {color_func(badge_data['name'])} "
                f"({badge_data['rarity']}) - {badge_data['points']} XP"
            )
            self.stdout.write(f"     {badge_data['description']}\n")

        # 6. Vérifier et attribuer les badges
        self.stdout.write(self.style.SUCCESS('\n🔍 Vérification des badges...\n'))
        try:
            new_badges = service.check_and_award_badges()
            if new_badges:
                self.stdout.write(self.style.SUCCESS(f'🎉 {len(new_badges)} nouveaux badges obtenus:'))
                for badge in new_badges:
                    self.stdout.write(f"  {badge['icon']} {badge['name']} (+{badge['points']} XP)")
            else:
                self.stdout.write(self.style.WARNING('⚠️  Aucun nouveau badge obtenu'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la vérification des badges: {e}'))
            import traceback
            traceback.print_exc()

        # 7. Afficher le récapitulatif
        profile.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f'\n📊 Récapitulatif pour {student.username}:'))
        self.stdout.write(f'  • Badges obtenus: {len(profile.badges or [])}')
        self.stdout.write(f'  • XP total: {profile.total_xp}')
        self.stdout.write(f'  • Niveau: {profile.level}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée!\n'))

    def create_demo_tests(self, student):
        """Créer des tests et résultats de démonstration"""
        self.stdout.write(self.style.SUCCESS('\n📝 Création de tests de démonstration...\n'))

        # Créer un enseignant si nécessaire
        teacher, created = User.objects.get_or_create(
            username='teacher_demo',
            defaults={
                'email': 'teacher@demo.com',
                'first_name': 'Prof',
                'last_name': 'Demo',
                'is_staff': True
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()

        # Créer des tests variés
        subjects = ['Mathématiques', 'Physique', 'Informatique', 'Anglais']
        
        for i, subject in enumerate(subjects):
            test, created = Test.objects.get_or_create(
                title=f'Test {subject} #{i+1}',
                defaults={
                    'description': f'Test de démonstration pour {subject}',
                    'subject': subject,
                    'topic': f'Chapitre {i+1}',
                    'created_by': teacher,
                    'difficulty': random.choice(['easy', 'medium', 'hard']),
                    'duration': 30,
                    'passing_score': 60.0,
                    'status': 'published',
                    'is_timed': True,
                    'total_points': 100.0,
                    'number_of_questions': 10
                }
            )

            if created:
                self.stdout.write(f'  ✅ Test créé: {test.title}')

                # Créer une soumission
                submission = Submission.objects.create(
                    student=student,
                    test=test,
                    status='completed',
                    started_at=timezone.now() - timedelta(hours=2),
                    submitted_at=timezone.now() - timedelta(hours=1)
                )

                # Créer un résultat avec un score aléatoire
                score = random.uniform(70, 100)  # Scores entre 70% et 100%
                Result.objects.create(
                    submission=submission,
                    student=student,
                    test=test,
                    total_score=score,
                    percentage_score=score,
                    grade='A' if score >= 90 else 'B' if score >= 80 else 'C',
                    mcq_score=score * 0.7,
                    true_false_score=score * 0.2,
                    essay_score=score * 0.1
                )

                self.stdout.write(f'    ✅ Résultat: {score:.1f}%')

        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(subjects)} tests créés avec succès!\n'))
