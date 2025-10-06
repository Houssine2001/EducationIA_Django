"""
Commande Django pour générer des données de test.
Crée des tests, des soumissions et des résultats pour tester l'interface.

Usage:
    python manage.py generate_test_data --students 5 --tests 20
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from evaluation.models import (
    Test, Question, Submission, Result, UserProfile
)
from evaluation.question_generator import generate_realistic_question, QUESTION_TEMPLATES

User = get_user_model()


class Command(BaseCommand):
    help = 'Génère des données de test pour l\'application evaluation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=3,
            help='Nombre d\'étudiants à créer'
        )
        parser.add_argument(
            '--tests',
            type=int,
            default=15,
            help='Nombre de tests à créer'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprimer les données existantes avant de générer'
        )

    def handle(self, *args, **options):
        students_count = options['students']
        tests_count = options['tests']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write('Suppression des données existantes...')
            # Supprimer dans l'ordre pour respecter les contraintes FK
            Result.objects.all().delete()
            Submission.objects.all().delete()
            Question.objects.all().delete()
            Test.objects.all().delete()
            User.objects.filter(is_staff=False, is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✓ Données supprimées'))

        # Matières disponibles
        subjects = [
            'Mathématiques',
            'Physique',
            'Chimie',
            'Informatique',
            'Français',
            'Anglais',
            'Histoire',
            'Géographie'
        ]

        # Créer des étudiants
        self.stdout.write(f'Création de {students_count} étudiants...')
        students = []
        for i in range(students_count):
            username = f'etudiant{i+1}'
            email = f'etudiant{i+1}@example.com'
            
            # Supprimer si existe déjà
            User.objects.filter(username=username).delete()
            
            student = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=f'Étudiant',
                last_name=f'{i+1}'
            )
            
            # Créer le profil
            profile, created = UserProfile.objects.get_or_create(
                user=student,
                defaults={
                    'student_id': f'STU{1000+i}',
                    'class_level': random.choice(['1ère', 'Terminale', 'Licence 1', 'Licence 2']),
                    'specialization': random.choice(['Sciences', 'Lettres', 'Informatique', 'Économie']),
                }
            )
            
            students.append(student)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Créé: {username}'))

        # Créer des tests
        self.stdout.write(f'\nCréation de {tests_count} tests...')
        tests = []
        for i in range(tests_count):
            subject = random.choice(subjects)
            test = Test.objects.create(
                title=f'Test {subject} #{i+1}',
                description=f'Test de niveau intermédiaire en {subject}',
                subject=subject,
                topic=f'Chapitre {random.randint(1, 10)}',
                difficulty=random.choice(['easy', 'medium', 'hard']),
                duration=random.choice([30, 45, 60, 90]),
                passing_score=random.choice([50.0, 60.0, 70.0]),
                status='published',
                shuffle_questions=random.choice([True, False]),
                allow_review=True,
                is_timed=True
            )
            
            # Créer des questions pour ce test (AVEC MOTS-CLÉS TECHNIQUES)
            num_questions = random.randint(8, 15)
            
            # Récupérer les compétences disponibles pour ce sujet
            available_skills = None
            if subject in QUESTION_TEMPLATES:
                available_skills = list(QUESTION_TEMPLATES[subject].keys())
            
            for q in range(num_questions):
                # Générer une question technique réaliste
                try:
                    # Choisir une compétence aléatoire
                    skill = random.choice(available_skills) if available_skills else None
                    
                    q_data = generate_realistic_question(
                        subject=subject,
                        skill=skill
                    )
                    
                    question = Question.objects.create(
                        test=test,
                        question_text=q_data['question_text'],
                        question_type='mcq',
                        points=random.choice([1, 2, 3, 5]),
                        order=q+1,
                        options=q_data['options'],
                        correct_answer=q_data['correct_answer'],
                        skills=[q_data['skill']],
                        difficulty_level=q_data['difficulty']
                    )
                except Exception as e:
                    # Fallback vers question simple
                    num_options = random.randint(3, 5)
                    correct_index = random.randint(0, num_options-1)
                    
                    options_list = []
                    for opt in range(num_options):
                        options_list.append({
                            'text': f'Option {chr(65+opt)}',
                            'is_correct': (opt == correct_index)
                        })
                    
                    question = Question.objects.create(
                        test=test,
                        question_text=f'Question {q+1} du test {subject}',
                        question_type='mcq',
                        points=random.choice([1, 2, 3, 5]),
                        order=q+1,
                        options=options_list
                    )
            
            tests.append(test)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Test créé: {test.title} ({num_questions} questions techniques)'))

        # Générer des soumissions et résultats
        self.stdout.write('\nGénération des soumissions et résultats...')
        total_submissions = 0
        
        for student in students:
            # Chaque étudiant fait entre 10 et tous les tests
            tests_to_take = random.sample(tests, random.randint(min(10, len(tests)), len(tests)))
            
            for test in tests_to_take:
                # Certains tests sont faits plusieurs fois (max 3 tentatives)
                attempts = random.randint(1, 3)
                
                for attempt in range(attempts):
                    # Date de la tentative (dans les 30 derniers jours)
                    days_ago = random.randint(1, 30)
                    submission_date = timezone.now() - timedelta(days=days_ago)
                    
                    # Créer la soumission
                    submission = Submission.objects.create(
                        student=student,
                        test=test,
                        started_at=submission_date,
                        submitted_at=submission_date + timedelta(minutes=random.randint(15, test.duration)),
                        status='graded'
                    )
                    
                    # Calculer le score basé sur les questions
                    questions = test.questions.all()
                    correct_answers = 0
                    total_points = 0
                    earned_points = 0
                    student_answers = {}  # Dictionnaire pour stocker les réponses
                    
                    for question in questions:
                        total_points += question.points
                        # Simuler une réponse (70% de chance de répondre correctement)
                        if random.random() < 0.7:
                            # Réponse correcte
                            is_correct = True
                            correct_answers += 1
                            earned_points += question.points
                            # Stocker la bonne réponse
                            student_answers[str(question.id)] = question.correct_answer
                        else:
                            # Réponse incorrecte - choisir une mauvaise option
                            is_correct = False
                            # Choisir une option différente de la bonne réponse
                            wrong_options = [f'Option {chr(65+i)} ({i})' for i in range(4) if f'Option {chr(65+i)} ({i})' != question.correct_answer]
                            if wrong_options:
                                student_answers[str(question.id)] = random.choice(wrong_options)
                    
                    # Mettre à jour la soumission avec les réponses
                    submission.answers = student_answers
                    submission.save()
                    
                    # Créer le résultat
                    percentage = (earned_points / total_points * 100) if total_points > 0 else 0
                    
                    # Générer des points forts et lacunes basés sur le sujet
                    strengths = []
                    weaknesses = []
                    
                    if percentage >= 70:
                        strengths = [
                            f'Excellente maîtrise du {test.subject}',
                            'Compréhension approfondie des concepts',
                            'Résolution rapide des problèmes'
                        ]
                        if percentage < 90:
                            weaknesses = ['Quelques détails à revoir']
                    elif percentage >= 50:
                        strengths = [
                            f'Bonne base en {test.subject}',
                            'Capacité d\'analyse correcte'
                        ]
                        weaknesses = [
                            'Approfondir certains chapitres',
                            'Travailler la précision'
                        ]
                    else:
                        strengths = ['Motivation à progresser']
                        weaknesses = [
                            f'Revoir les fondamentaux de {test.subject}',
                            'Pratiquer davantage',
                            'Demander de l\'aide si nécessaire'
                        ]
                    
                    result = Result.objects.create(
                        submission=submission,
                        student=student,
                        test=test,
                        total_score=total_points,
                        percentage_score=percentage,
                        ai_analysis={
                            'strengths': strengths,
                            'weaknesses': weaknesses,
                            'recommendations': [
                                f'Continuer à pratiquer le {test.subject}',
                                'Réviser les exercices difficiles'
                            ]
                        }
                    )
                    
                    total_submissions += 1
                    
                    # Mettre à jour le profil de l'étudiant
                    profile, created = UserProfile.objects.get_or_create(user=student)
                    profile.total_tests_taken += 1
                    
                    # Mettre à jour la moyenne
                    all_results = Result.objects.filter(student=student)
                    profile.average_score = sum(r.percentage_score for r in all_results) / all_results.count()
                    
                    # Ajouter XP
                    xp_gained = int(percentage)
                    profile.total_xp += xp_gained
                    
                    # Calculer le niveau (100 XP par niveau)
                    profile.level = profile.total_xp // 100
                    
                    # Mettre à jour les forces et faiblesses globales
                    if not profile.strengths:
                        profile.strengths = []
                    if not profile.weaknesses:
                        profile.weaknesses = []
                    
                    # Ajouter les nouvelles forces (sans doublons)
                    for strength in strengths:
                        if strength not in profile.strengths and len(profile.strengths) < 5:
                            profile.strengths.append(strength)
                    
                    # Ajouter les nouvelles lacunes (sans doublons)
                    for weakness in weaknesses:
                        if weakness not in profile.weaknesses and len(profile.weaknesses) < 5:
                            profile.weaknesses.append(weakness)
                    
                    profile.save()

        self.stdout.write(self.style.SUCCESS(f'\n✓ {total_submissions} soumissions créées'))
        
        # Résumé
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('GÉNÉRATION TERMINÉE !'))
        self.stdout.write('='*60)
        self.stdout.write(f'Étudiants créés: {students_count}')
        self.stdout.write(f'Tests créés: {tests_count}')
        self.stdout.write(f'Soumissions: {total_submissions}')
        self.stdout.write('\nIdentifiants de connexion:')
        for i in range(students_count):
            self.stdout.write(f'  • Username: etudiant{i+1} | Password: password123')
        self.stdout.write('\nVous pouvez maintenant tester l\'interface avec ces comptes !')
