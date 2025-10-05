"""
Exemples d'utilisation des modèles
Script pour tester et comprendre les modèles MongoDB
"""

from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test, Question, Submission, Result
from datetime import datetime, timedelta


def create_sample_users():
    """
    Créer des utilisateurs exemples
    """
    # Créer un professeur
    teacher = User.objects.create_user(
        username='prof_martin',
        email='martin@school.com',
        password='password123',
        first_name='Jean',
        last_name='Martin'
    )
    teacher.is_staff = True
    teacher.save()
    
    # Créer des étudiants
    student1 = User.objects.create_user(
        username='alice_dupont',
        email='alice@student.com',
        password='password123',
        first_name='Alice',
        last_name='Dupont'
    )
    
    student2 = User.objects.create_user(
        username='bob_martin',
        email='bob@student.com',
        password='password123',
        first_name='Bob',
        last_name='Martin'
    )
    
    print("✓ Utilisateurs créés")
    return teacher, student1, student2


def create_student_profiles(student1, student2):
    """
    Créer des profils étudiants
    """
    profile1 = UserProfile.objects.create(
        user=student1,
        student_id='ETU2025001',
        class_level='Seconde',
        specialization='Sciences',
        strengths=['mathématiques', 'physique', 'logique'],
        weaknesses=['français', 'expression écrite'],
        learning_style='visuel',
        ai_recommendations={
            'focus_areas': ['Améliorer l\'expression écrite'],
            'suggested_exercises': ['Rédaction quotidienne', 'Lecture'],
            'learning_path': 'progressive'
        },
        performance_history=[
            {'date': '2025-09-15', 'score': 82, 'subject': 'Mathématiques'},
            {'date': '2025-09-20', 'score': 75, 'subject': 'Français'},
        ],
        skill_progress={
            'mathématiques': {'initial': 75, 'current': 82, 'target': 90},
            'français': {'initial': 70, 'current': 75, 'target': 80}
        }
    )
    
    profile2 = UserProfile.objects.create(
        user=student2,
        student_id='ETU2025002',
        class_level='Seconde',
        specialization='Littéraire',
        strengths=['français', 'histoire', 'analyse'],
        weaknesses=['mathématiques', 'calcul'],
        learning_style='auditif',
        ai_recommendations={
            'focus_areas': ['Renforcer les bases en mathématiques'],
            'suggested_exercises': ['Exercices de calcul mental', 'Révision des fondamentaux'],
            'learning_path': 'remedial'
        }
    )
    
    print("✓ Profils étudiants créés")
    return profile1, profile2


def create_sample_test(teacher):
    """
    Créer un test exemple
    """
    test = Test.objects.create(
        title='Test de Mathématiques - Chapitre 1',
        description='Évaluation sur les équations du premier degré et les fonctions linéaires',
        subject='Mathématiques',
        topic='Algèbre - Équations et Fonctions',
        created_by=teacher,
        difficulty='medium',
        duration=60,
        passing_score=50.0,
        total_points=20.0,
        is_timed=True,
        allow_review=True,
        shuffle_questions=False,
        status='published',
        published_at=datetime.now(),
        tags=['algèbre', 'équations', 'fonctions', 'seconde'],
        skills_tested=[
            'Résolution d\'équations',
            'Calcul algébrique',
            'Raisonnement logique',
            'Représentation graphique'
        ],
        ai_metadata={
            'recommended_for': ['students_weak_in_algebra'],
            'prerequisite_skills': ['arithmétique de base', 'calcul mental'],
            'difficulty_score': 0.65,
            'estimated_completion_time': 55
        }
    )
    
    print(f"✓ Test créé: {test.title}")
    return test


def create_sample_questions(test):
    """
    Créer des questions exemples pour le test
    """
    questions = []
    
    # Question 1 - QCM
    q1 = Question.objects.create(
        test=test,
        question_text='Quelle est la solution de l\'équation 2x + 5 = 13 ?',
        question_type='mcq',
        order=1,
        points=2.0,
        difficulty_level='easy',
        options=[
            {'id': 'A', 'text': 'x = 4', 'is_correct': True},
            {'id': 'B', 'text': 'x = 9', 'is_correct': False},
            {'id': 'C', 'text': 'x = 6.5', 'is_correct': False},
            {'id': 'D', 'text': 'x = 8', 'is_correct': False},
        ],
        explanation='Pour résoudre 2x + 5 = 13, on soustrait 5 de chaque côté: 2x = 8, puis on divise par 2: x = 4',
        hint='Isole d\'abord le terme en x',
        skills=['Résolution d\'équations', 'Calcul algébrique'],
        ai_analysis={
            'difficulty_score': 0.3,
            'cognitive_level': 'application',
            'bloom_taxonomy': 'level_3',
            'estimated_time': 60
        },
        common_mistakes=[
            {
                'mistake': 'Oublier de soustraire 5 avant de diviser',
                'frequency': 0.25,
                'explanation': 'Beaucoup d\'étudiants divisent directement par 2'
            }
        ]
    )
    questions.append(q1)
    
    # Question 2 - Vrai/Faux
    q2 = Question.objects.create(
        test=test,
        question_text='Vrai ou Faux: Une fonction linéaire passe toujours par l\'origine (0,0)',
        question_type='true_false',
        order=2,
        points=1.0,
        difficulty_level='easy',
        correct_answer='True',
        explanation='Une fonction linéaire est de la forme f(x) = ax, donc f(0) = a×0 = 0',
        skills=['Fonctions linéaires', 'Propriétés mathématiques'],
        ai_analysis={
            'difficulty_score': 0.25,
            'cognitive_level': 'comprehension',
            'bloom_taxonomy': 'level_2'
        }
    )
    questions.append(q2)
    
    # Question 3 - QCM plus difficile
    q3 = Question.objects.create(
        test=test,
        question_text='Soit f(x) = 3x - 2. Quelle est la valeur de x pour laquelle f(x) = 10 ?',
        question_type='mcq',
        order=3,
        points=3.0,
        difficulty_level='medium',
        options=[
            {'id': 'A', 'text': 'x = 3', 'is_correct': False},
            {'id': 'B', 'text': 'x = 4', 'is_correct': True},
            {'id': 'C', 'text': 'x = 2.67', 'is_correct': False},
            {'id': 'D', 'text': 'x = 6', 'is_correct': False},
        ],
        explanation='3x - 2 = 10 → 3x = 12 → x = 4',
        hint='Remplace f(x) par 10 et résous l\'équation',
        skills=['Fonctions', 'Résolution d\'équations', 'Substitution'],
        ai_analysis={
            'difficulty_score': 0.5,
            'cognitive_level': 'application',
            'bloom_taxonomy': 'level_3',
            'estimated_time': 90
        }
    )
    questions.append(q3)
    
    # Question 4 - Réponse courte
    q4 = Question.objects.create(
        test=test,
        question_text='Résoudre: 5(x - 2) = 3x + 4. Donner la valeur de x.',
        question_type='short_answer',
        order=4,
        points=4.0,
        difficulty_level='medium',
        correct_answer='7',
        explanation='5x - 10 = 3x + 4 → 2x = 14 → x = 7',
        hint='Développe d\'abord 5(x - 2)',
        skills=['Résolution d\'équations', 'Développement', 'Calcul algébrique'],
        ai_analysis={
            'difficulty_score': 0.6,
            'cognitive_level': 'application',
            'bloom_taxonomy': 'level_3',
            'estimated_time': 120
        }
    )
    questions.append(q4)
    
    # Question 5 - Rédaction
    q5 = Question.objects.create(
        test=test,
        question_text='Expliquez en quelques phrases ce qu\'est une fonction affine et donnez un exemple concret d\'utilisation dans la vie quotidienne.',
        question_type='essay',
        order=5,
        points=10.0,
        difficulty_level='hard',
        explanation='Réponse attendue: Une fonction affine est de la forme f(x) = ax + b. Exemple: calcul d\'un prix avec un tarif de base + coût par unité.',
        skills=['Compréhension des concepts', 'Expression écrite', 'Application pratique'],
        ai_analysis={
            'difficulty_score': 0.7,
            'cognitive_level': 'synthesis',
            'bloom_taxonomy': 'level_5',
            'estimated_time': 300
        }
    )
    questions.append(q5)
    
    # Mettre à jour le nombre de questions du test
    test.number_of_questions = len(questions)
    test.save()
    
    print(f"✓ {len(questions)} questions créées pour le test")
    return questions


def create_sample_submission(student, test, questions):
    """
    Créer une soumission exemple
    """
    submission = Submission.objects.create(
        student=student,
        test=test,
        status='submitted',
        started_at=datetime.now() - timedelta(minutes=45),
        submitted_at=datetime.now(),
        time_spent=2700,  # 45 minutes en secondes
        answers={
            str(questions[0].id): {
                'answer': 'A',
                'time_spent': 60,
                'is_correct': True,
                'confidence': 0.9
            },
            str(questions[1].id): {
                'answer': 'True',
                'time_spent': 30,
                'is_correct': True,
                'confidence': 1.0
            },
            str(questions[2].id): {
                'answer': 'B',
                'time_spent': 90,
                'is_correct': True,
                'confidence': 0.8
            },
            str(questions[3].id): {
                'answer': '7',
                'time_spent': 120,
                'is_correct': True,
                'confidence': 0.85
            },
            str(questions[4].id): {
                'answer': 'Une fonction affine est une fonction de la forme f(x) = ax + b où a et b sont des constantes...',
                'time_spent': 300,
                'is_correct': True,
                'confidence': 0.7
            }
        },
        score=19.0,
        percentage=95.0,
        passed=True,
        ai_feedback={
            'overall_performance': 'Excellent travail ! Vous maîtrisez bien les concepts.',
            'strengths_shown': ['Rapidité de calcul', 'Précision', 'Bonne compréhension'],
            'areas_to_improve': ['Confiance en vos réponses'],
            'personalized_tips': [
                'Continuez à pratiquer pour gagner en assurance',
                'Excellente gestion du temps'
            ]
        },
        performance_analysis={
            'speed_score': 0.95,
            'accuracy_score': 0.95,
            'consistency_score': 0.90,
            'improvement_rate': 0.15
        }
    )
    
    print(f"✓ Soumission créée pour {student.username}")
    return submission


def create_sample_result(submission, student, test):
    """
    Créer un résultat détaillé
    """
    result = Result.objects.create(
        submission=submission,
        student=student,
        test=test,
        total_score=19.0,
        percentage_score=95.0,
        grade='A+',
        mcq_score=5.0,
        true_false_score=1.0,
        essay_score=10.0,
        skills_breakdown={
            'Résolution d\'équations': {
                'score': 9.0,
                'percentage': 90,
                'questions_answered': 3,
                'questions_correct': 3
            },
            'Calcul algébrique': {
                'score': 6.0,
                'percentage': 100,
                'questions_answered': 2,
                'questions_correct': 2
            },
            'Compréhension des concepts': {
                'score': 10.0,
                'percentage': 100,
                'questions_answered': 1,
                'questions_correct': 1
            }
        },
        rank=1,
        percentile=95.0,
        compared_to_average=20.0,
        questions_per_minute=0.11,
        average_time_per_question=540.0,
        time_efficiency=0.95,
        ai_analysis={
            'strengths': [
                'Excellente maîtrise des équations du premier degré',
                'Rapidité et précision dans les calculs',
                'Bonne expression écrite'
            ],
            'weaknesses': [
                'Peut gagner encore en confiance'
            ],
            'recommendations': [
                'Continuer à ce rythme',
                'Aborder des exercices plus complexes',
                'Pratiquer les équations du second degré'
            ],
            'predicted_next_score': 96.5,
            'learning_trajectory': 'excellent',
            'confidence_score': 0.95,
            'study_time_needed': 30,
            'optimal_practice_frequency': 'every_2_days'
        },
        recommendations=[
            'Passer au niveau supérieur: équations du second degré',
            'Pratiquer les systèmes d\'équations',
            'Aider les camarades qui ont des difficultés'
        ],
        study_suggestions=[
            'Exercices avancés d\'algèbre',
            'Problèmes de synthèse',
            'Préparation aux olympiades mathématiques'
        ],
        error_patterns=[],
        learning_gaps=[],
        performance_chart_data={
            'timeline': [
                {'date': '2025-09-15', 'score': 82},
                {'date': '2025-09-25', 'score': 88},
                {'date': '2025-10-05', 'score': 95}
            ],
            'skills': {
                'Résolution d\'équations': [75, 85, 90],
                'Calcul algébrique': [80, 90, 100],
                'Compréhension': [85, 95, 100]
            }
        }
    )
    
    print(f"✓ Résultat créé: Note {result.grade} ({result.percentage_score}%)")
    return result


def run_complete_example():
    """
    Exécuter l'exemple complet
    """
    print("\n" + "="*50)
    print("CRÉATION DE DONNÉES EXEMPLES")
    print("="*50 + "\n")
    
    # 1. Créer les utilisateurs
    print("1. Création des utilisateurs...")
    teacher, student1, student2 = create_sample_users()
    
    # 2. Créer les profils
    print("\n2. Création des profils étudiants...")
    profile1, profile2 = create_student_profiles(student1, student2)
    
    # 3. Créer un test
    print("\n3. Création d'un test...")
    test = create_sample_test(teacher)
    
    # 4. Créer des questions
    print("\n4. Création des questions...")
    questions = create_sample_questions(test)
    
    # 5. Créer une soumission
    print("\n5. Création d'une soumission...")
    submission = create_sample_submission(student1, test, questions)
    
    # 6. Créer un résultat
    print("\n6. Création du résultat détaillé...")
    result = create_sample_result(submission, student1, test)
    
    print("\n" + "="*50)
    print("✓ EXEMPLE COMPLET CRÉÉ AVEC SUCCÈS !")
    print("="*50)
    print(f"\nVous pouvez maintenant:")
    print(f"  - Accéder à l'admin Django")
    print(f"  - Consulter les données créées")
    print(f"  - Tester les modèles et leurs relations")
    print(f"\nProfesseur: {teacher.username} / password123")
    print(f"Étudiant: {student1.username} / password123")
    print(f"\nTest créé: {test.title}")
    print(f"Score obtenu: {result.percentage_score}% (Note: {result.grade})")


# Pour exécuter cet exemple:
# python manage.py shell
# >>> exec(open('evaluation/examples.py').read())
# >>> run_complete_example()
