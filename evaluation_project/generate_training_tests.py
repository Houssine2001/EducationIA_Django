import os
import django
import sys
from datetime import datetime, timedelta
import random

# Configuration Django
sys.path.append('C:\\Users\\Lenovo\\Desktop\\DjangoEducation\\evaluation_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from evaluation.models import Test, Question, Result, UserProfile, Submission
from django.contrib.auth.models import User
from django.utils import timezone

# Tests de programmation variés
TESTS_DATA = [
    {
        'title': 'JavaScript ES6+ Avancé',
        'subject': 'JavaScript',
        'duration': 30,
        'questions': [
            {
                'text': 'Quelle est la différence entre let et const?',
                'options': [
                    {'id': 'A', 'text': 'let permet la réaffectation, const non', 'is_correct': True},
                    {'id': 'B', 'text': 'const est plus rapide', 'is_correct': False},
                    {'id': 'C', 'text': 'Aucune différence', 'is_correct': False},
                    {'id': 'D', 'text': 'let est obsolète', 'is_correct': False},
                ]
            },
            {
                'text': 'Que retourne [...arr] ?',
                'options': [
                    {'id': 'A', 'text': 'Une copie superficielle du tableau', 'is_correct': True},
                    {'id': 'B', 'text': 'Une référence au tableau', 'is_correct': False},
                    {'id': 'C', 'text': 'Une erreur', 'is_correct': False},
                    {'id': 'D', 'text': 'Un objet', 'is_correct': False},
                ]
            },
            {
                'text': 'Qu\'est-ce qu\'une Arrow Function?',
                'options': [
                    {'id': 'A', 'text': 'Une syntaxe concise pour les fonctions', 'is_correct': True},
                    {'id': 'B', 'text': 'Un type de boucle', 'is_correct': False},
                    {'id': 'C', 'text': 'Un tableau spécial', 'is_correct': False},
                    {'id': 'D', 'text': 'Un objet graphique', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'Python - Structures de Données',
        'subject': 'Python',
        'duration': 25,
        'questions': [
            {
                'text': 'Quelle structure de données Python est ordonnée et modifiable?',
                'options': [
                    {'id': 'A', 'text': 'Liste', 'is_correct': True},
                    {'id': 'B', 'text': 'Tuple', 'is_correct': False},
                    {'id': 'C', 'text': 'Set', 'is_correct': False},
                    {'id': 'D', 'text': 'Frozenset', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment créer un dictionnaire vide en Python?',
                'options': [
                    {'id': 'A', 'text': '{}', 'is_correct': True},
                    {'id': 'B', 'text': '[]', 'is_correct': False},
                    {'id': 'C', 'text': '()', 'is_correct': False},
                    {'id': 'D', 'text': 'set()', 'is_correct': False},
                ]
            },
            {
                'text': 'Que fait la méthode .append() sur une liste?',
                'options': [
                    {'id': 'A', 'text': 'Ajoute un élément à la fin', 'is_correct': True},
                    {'id': 'B', 'text': 'Supprime le dernier élément', 'is_correct': False},
                    {'id': 'C', 'text': 'Trie la liste', 'is_correct': False},
                    {'id': 'D', 'text': 'Inverse la liste', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'HTML5 & Sémantique',
        'subject': 'HTML',
        'duration': 20,
        'questions': [
            {
                'text': 'Quelle balise définit un en-tête de section?',
                'options': [
                    {'id': 'A', 'text': '<header>', 'is_correct': True},
                    {'id': 'B', 'text': '<head>', 'is_correct': False},
                    {'id': 'C', 'text': '<top>', 'is_correct': False},
                    {'id': 'D', 'text': '<section>', 'is_correct': False},
                ]
            },
            {
                'text': 'Quelle balise est utilisée pour une navigation?',
                'options': [
                    {'id': 'A', 'text': '<nav>', 'is_correct': True},
                    {'id': 'B', 'text': '<menu>', 'is_correct': False},
                    {'id': 'C', 'text': '<navigation>', 'is_correct': False},
                    {'id': 'D', 'text': '<links>', 'is_correct': False},
                ]
            },
            {
                'text': 'Quelle balise HTML5 définit un contenu indépendant?',
                'options': [
                    {'id': 'A', 'text': '<article>', 'is_correct': True},
                    {'id': 'B', 'text': '<div>', 'is_correct': False},
                    {'id': 'C', 'text': '<section>', 'is_correct': False},
                    {'id': 'D', 'text': '<content>', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'CSS3 - Flexbox & Grid',
        'subject': 'CSS',
        'duration': 25,
        'questions': [
            {
                'text': 'Quelle propriété active Flexbox?',
                'options': [
                    {'id': 'A', 'text': 'display: flex', 'is_correct': True},
                    {'id': 'B', 'text': 'flexbox: true', 'is_correct': False},
                    {'id': 'C', 'text': 'layout: flex', 'is_correct': False},
                    {'id': 'D', 'text': 'flex: on', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment centrer verticalement avec Flexbox?',
                'options': [
                    {'id': 'A', 'text': 'align-items: center', 'is_correct': True},
                    {'id': 'B', 'text': 'vertical-align: middle', 'is_correct': False},
                    {'id': 'C', 'text': 'center: vertical', 'is_correct': False},
                    {'id': 'D', 'text': 'justify-content: center', 'is_correct': False},
                ]
            },
            {
                'text': 'Quelle propriété CSS Grid définit les colonnes?',
                'options': [
                    {'id': 'A', 'text': 'grid-template-columns', 'is_correct': True},
                    {'id': 'B', 'text': 'columns', 'is_correct': False},
                    {'id': 'C', 'text': 'grid-columns', 'is_correct': False},
                    {'id': 'D', 'text': 'template-columns', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'Node.js - Backend Fundamentals',
        'subject': 'Node.js',
        'duration': 30,
        'questions': [
            {
                'text': 'Qu\'est-ce que npm?',
                'options': [
                    {'id': 'A', 'text': 'Node Package Manager', 'is_correct': True},
                    {'id': 'B', 'text': 'New Project Manager', 'is_correct': False},
                    {'id': 'C', 'text': 'Node Programming Module', 'is_correct': False},
                    {'id': 'D', 'text': 'Network Protocol Manager', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment importer un module en Node.js?',
                'options': [
                    {'id': 'A', 'text': 'require()', 'is_correct': True},
                    {'id': 'B', 'text': 'import()', 'is_correct': False},
                    {'id': 'C', 'text': 'include()', 'is_correct': False},
                    {'id': 'D', 'text': 'use()', 'is_correct': False},
                ]
            },
            {
                'text': 'Quel framework Node.js est le plus populaire?',
                'options': [
                    {'id': 'A', 'text': 'Express.js', 'is_correct': True},
                    {'id': 'B', 'text': 'Angular', 'is_correct': False},
                    {'id': 'C', 'text': 'Django', 'is_correct': False},
                    {'id': 'D', 'text': 'Flask', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'React Hooks Avancés',
        'subject': 'React',
        'duration': 35,
        'questions': [
            {
                'text': 'Quel Hook gère l\'état local?',
                'options': [
                    {'id': 'A', 'text': 'useState', 'is_correct': True},
                    {'id': 'B', 'text': 'useEffect', 'is_correct': False},
                    {'id': 'C', 'text': 'useContext', 'is_correct': False},
                    {'id': 'D', 'text': 'useReducer', 'is_correct': False},
                ]
            },
            {
                'text': 'Quand useEffect s\'exécute-t-il?',
                'options': [
                    {'id': 'A', 'text': 'Après chaque rendu', 'is_correct': True},
                    {'id': 'B', 'text': 'Avant chaque rendu', 'is_correct': False},
                    {'id': 'C', 'text': 'Une seule fois au montage', 'is_correct': False},
                    {'id': 'D', 'text': 'Jamais', 'is_correct': False},
                ]
            },
            {
                'text': 'Que retourne useState?',
                'options': [
                    {'id': 'A', 'text': 'Un tableau [state, setState]', 'is_correct': True},
                    {'id': 'B', 'text': 'Un objet {state, setState}', 'is_correct': False},
                    {'id': 'C', 'text': 'Seulement la valeur', 'is_correct': False},
                    {'id': 'D', 'text': 'Une fonction', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment optimiser un composant React?',
                'options': [
                    {'id': 'A', 'text': 'Avec React.memo()', 'is_correct': True},
                    {'id': 'B', 'text': 'Avec useOptimize()', 'is_correct': False},
                    {'id': 'C', 'text': 'Avec shouldUpdate()', 'is_correct': False},
                    {'id': 'D', 'text': 'Automatiquement', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'SQL - Requêtes Avancées',
        'subject': 'SQL',
        'duration': 30,
        'questions': [
            {
                'text': 'Quelle clause filtre les résultats?',
                'options': [
                    {'id': 'A', 'text': 'WHERE', 'is_correct': True},
                    {'id': 'B', 'text': 'FILTER', 'is_correct': False},
                    {'id': 'C', 'text': 'HAVING', 'is_correct': False},
                    {'id': 'D', 'text': 'SELECT', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment joindre deux tables?',
                'options': [
                    {'id': 'A', 'text': 'JOIN', 'is_correct': True},
                    {'id': 'B', 'text': 'MERGE', 'is_correct': False},
                    {'id': 'C', 'text': 'COMBINE', 'is_correct': False},
                    {'id': 'D', 'text': 'LINK', 'is_correct': False},
                ]
            },
            {
                'text': 'Quelle fonction compte les lignes?',
                'options': [
                    {'id': 'A', 'text': 'COUNT()', 'is_correct': True},
                    {'id': 'B', 'text': 'SUM()', 'is_correct': False},
                    {'id': 'C', 'text': 'TOTAL()', 'is_correct': False},
                    {'id': 'D', 'text': 'LENGTH()', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'Git & GitHub Workflow',
        'subject': 'Git',
        'duration': 20,
        'questions': [
            {
                'text': 'Comment créer une branche?',
                'options': [
                    {'id': 'A', 'text': 'git branch nom', 'is_correct': True},
                    {'id': 'B', 'text': 'git create branch', 'is_correct': False},
                    {'id': 'C', 'text': 'git new branch', 'is_correct': False},
                    {'id': 'D', 'text': 'git add branch', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment fusionner une branche?',
                'options': [
                    {'id': 'A', 'text': 'git merge', 'is_correct': True},
                    {'id': 'B', 'text': 'git combine', 'is_correct': False},
                    {'id': 'C', 'text': 'git join', 'is_correct': False},
                    {'id': 'D', 'text': 'git fusion', 'is_correct': False},
                ]
            },
            {
                'text': 'Comment annuler le dernier commit?',
                'options': [
                    {'id': 'A', 'text': 'git reset HEAD~1', 'is_correct': True},
                    {'id': 'B', 'text': 'git undo', 'is_correct': False},
                    {'id': 'C', 'text': 'git revert last', 'is_correct': False},
                    {'id': 'D', 'text': 'git delete commit', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'TypeScript - Types Avancés',
        'subject': 'TypeScript',
        'duration': 30,
        'questions': [
            {
                'text': 'Comment définir une interface?',
                'options': [
                    {'id': 'A', 'text': 'interface Name { }', 'is_correct': True},
                    {'id': 'B', 'text': 'type Name = { }', 'is_correct': False},
                    {'id': 'C', 'text': 'class Name { }', 'is_correct': False},
                    {'id': 'D', 'text': 'struct Name { }', 'is_correct': False},
                ]
            },
            {
                'text': 'Quel type pour un tableau de nombres?',
                'options': [
                    {'id': 'A', 'text': 'number[]', 'is_correct': True},
                    {'id': 'B', 'text': 'array<number>', 'is_correct': False},
                    {'id': 'C', 'text': '[number]', 'is_correct': False},
                    {'id': 'D', 'text': 'numbers', 'is_correct': False},
                ]
            },
            {
                'text': 'Que signifie le type "any"?',
                'options': [
                    {'id': 'A', 'text': 'N\'importe quel type', 'is_correct': True},
                    {'id': 'B', 'text': 'Type vide', 'is_correct': False},
                    {'id': 'C', 'text': 'Type numérique', 'is_correct': False},
                    {'id': 'D', 'text': 'Type invalide', 'is_correct': False},
                ]
            },
        ]
    },
    {
        'title': 'API REST - Bonnes Pratiques',
        'subject': 'API',
        'duration': 25,
        'questions': [
            {
                'text': 'Quelle méthode HTTP pour créer?',
                'options': [
                    {'id': 'A', 'text': 'POST', 'is_correct': True},
                    {'id': 'B', 'text': 'GET', 'is_correct': False},
                    {'id': 'C', 'text': 'PUT', 'is_correct': False},
                    {'id': 'D', 'text': 'DELETE', 'is_correct': False},
                ]
            },
            {
                'text': 'Code HTTP pour succès?',
                'options': [
                    {'id': 'A', 'text': '200', 'is_correct': True},
                    {'id': 'B', 'text': '404', 'is_correct': False},
                    {'id': 'C', 'text': '500', 'is_correct': False},
                    {'id': 'D', 'text': '301', 'is_correct': False},
                ]
            },
            {
                'text': 'Que signifie REST?',
                'options': [
                    {'id': 'A', 'text': 'Representational State Transfer', 'is_correct': True},
                    {'id': 'B', 'text': 'Remote State Transfer', 'is_correct': False},
                    {'id': 'C', 'text': 'Request State Transfer', 'is_correct': False},
                    {'id': 'D', 'text': 'Resource State Transfer', 'is_correct': False},
                ]
            },
        ]
    },
]

def create_test_with_questions(test_data, teacher):
    """Créer un test avec ses questions"""
    test = Test.objects.create(
        title=test_data['title'],
        subject=test_data['subject'],
        duration=test_data['duration'],
        passing_score=70,
        status='published',
        shuffle_questions=True,
        created_by=teacher
    )
    
    for i, q_data in enumerate(test_data['questions'], 1):
        Question.objects.create(
            test=test,
            question_text=q_data['text'],
            question_type='mcq',
            options=q_data['options'],
            points=1.0,
            order=i
        )
    
    # Calculer le total des points
    test.total_points = len(test_data['questions'])
    test.save()
    
    return test

def generate_realistic_results(student, test, num_attempts=3):
    """Générer des résultats réalistes avec progression"""
    base_score = random.uniform(40, 65)  # Score de départ
    
    for attempt in range(num_attempts):
        # Progression réaliste: amélioration entre les tentatives
        improvement = random.uniform(5, 15) * attempt
        score = min(base_score + improvement + random.uniform(-5, 5), 100)
        
        # Date réaliste (espacée)
        days_ago = (num_attempts - attempt) * random.randint(2, 7)
        created_at = timezone.now() - timedelta(days=days_ago)
        
        # Créer une submission d'abord
        submission = Submission.objects.create(
            student=student.user,
            test=test,
            status='graded',
            started_at=created_at - timedelta(minutes=test.duration),
            submitted_at=created_at,
            answers={}  # Réponses vides pour simplifier
        )
        
        # Créer le résultat
        total_score = (score / 100) * test.total_points
        
        Result.objects.create(
            submission=submission,
            student=student.user,
            test=test,
            total_score=total_score,
            percentage_score=score,
            grade=get_grade(score),
            ai_analysis={
                'overall_feedback': f"Performance {'excellente' if score >= 80 else 'bonne' if score >= 70 else 'moyenne'}",
                'encouragement': "Continuez sur cette voie!" if score >= 70 else "Vous progressez!",
                'strengths': [{'skill': test.subject, 'description': 'Bonne compréhension'}],
                'weaknesses': [{'skill': 'Détails', 'description': 'Revoir les concepts avancés'}] if score < 80 else [],
                'recommendations': [{'title': 'Pratique', 'message': 'Continuez à pratiquer régulièrement'}]
            }
        )

def get_grade(score):
    """Convertir le score en note"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'

def main():
    print("🚀 Génération de tests variés pour entraîner l'IA...")
    
    # Récupérer les utilisateurs
    try:
        teacher = User.objects.filter(groups__name='Professeur').first()
        if not teacher:
            teacher = User.objects.filter(is_staff=True).first()
        
        student = User.objects.filter(username='etudiant1').first()
        if not student:
            print("❌ Étudiant 'etudiant1' non trouvé!")
            return
        
        student_profile, _ = UserProfile.objects.get_or_create(user=student)
        
        print(f"✅ Professeur: {teacher.username}")
        print(f"✅ Étudiant: {student.username}")
        print()
        
        # Créer les tests
        created_tests = []
        for test_data in TESTS_DATA:
            print(f"📝 Création du test: {test_data['title']}")
            test = create_test_with_questions(test_data, teacher)
            created_tests.append(test)
            print(f"   ✓ {test.questions.count()} questions créées")
            
            # Générer des résultats variés
            num_attempts = random.randint(2, 5)
            print(f"   📊 Génération de {num_attempts} tentatives...")
            generate_realistic_results(student_profile, test, num_attempts)
            print(f"   ✓ Résultats générés\n")
        
        # Statistiques finales
        total_tests = len(created_tests)
        total_results = Result.objects.filter(student=student).count()
        avg_score = Result.objects.filter(student=student).aggregate(
            avg=django.db.models.Avg('percentage_score')
        )['avg'] or 0
        
        print("=" * 60)
        print("🎉 GÉNÉRATION TERMINÉE!")
        print("=" * 60)
        print(f"✅ Tests créés: {total_tests}")
        print(f"✅ Résultats générés: {total_results}")
        print(f"✅ Score moyen: {avg_score:.1f}%")
        print(f"\n📈 L'IA dispose maintenant de {total_results} résultats pour analyser les performances!")
        print("🎯 Points forts et faibles seront identifiés avec précision.")
        print("\n💡 Connectez-vous avec 'etudiant1' pour voir votre progression!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
