"""
Système d'analyse IA amélioré pour détection granulaire des compétences.

Au lieu de détecter "Point fort: React", détecte précisément:
- "Excellente maîtrise des Hooks React (useState, useEffect)"
- "Bonne compréhension du cycle de vie des composants"
- "Maîtrise de la gestion d'état avec Redux"

Basé sur l'analyse détaillée de chaque question et réponse.
"""

import re
import json
from typing import Dict, List, Tuple
from collections import defaultdict


class EnhancedSkillAnalyzer:
    """
    Analyseur de compétences granulaire basé sur les questions individuelles.
    """
    
    # Mapping des patterns de questions vers compétences spécifiques
    SKILL_PATTERNS = {
        # REACT
        'react': {
            'hooks': [
                r'useState', r'useEffect', r'useContext', r'useReducer', 
                r'useMemo', r'useCallback', r'useRef', r'custom hook'
            ],
            'components': [
                r'component', r'props', r'state', r'lifecycle',
                r'render', r'class component', r'functional component'
            ],
            'routing': [
                r'react router', r'route', r'navigation', r'link', r'redirect'
            ],
            'state_management': [
                r'redux', r'context api', r'state management', r'store',
                r'action', r'reducer', r'dispatch'
            ],
            'performance': [
                r'memo', r'optimization', r'lazy loading', r'suspense',
                r'code splitting', r'performance'
            ],
            'events': [
                r'event', r'onclick', r'onchange', r'handler', r'synthetic event'
            ],
            'forms': [
                r'form', r'input', r'controlled', r'uncontrolled', r'validation'
            ],
            'jsx': [
                r'jsx', r'fragment', r'expression', r'conditional rendering'
            ]
        },
        
        # JAVASCRIPT
        'javascript': {
            'es6': [
                r'arrow function', r'let', r'const', r'template literal',
                r'destructuring', r'spread', r'rest parameter'
            ],
            'async': [
                r'promise', r'async', r'await', r'callback', r'asynchronous'
            ],
            'dom': [
                r'dom', r'getelementbyid', r'queryselector', r'addeventlistener',
                r'createelement', r'appendchild'
            ],
            'arrays': [
                r'map', r'filter', r'reduce', r'foreach', r'find', r'some', r'every'
            ],
            'objects': [
                r'object', r'property', r'method', r'prototype', r'this', r'bind'
            ],
            'closures': [
                r'closure', r'scope', r'lexical', r'iife'
            ],
            'classes': [
                r'class', r'constructor', r'extends', r'super', r'inheritance'
            ]
        },
        
        # PYTHON
        'python': {
            'basics': [
                r'variable', r'type', r'string', r'int', r'float', r'list', r'dict'
            ],
            'oop': [
                r'class', r'object', r'inheritance', r'polymorphism', r'encapsulation'
            ],
            'functions': [
                r'function', r'def', r'return', r'parameter', r'argument', r'lambda'
            ],
            'data_structures': [
                r'list', r'tuple', r'set', r'dictionary', r'comprehension'
            ],
            'modules': [
                r'import', r'module', r'package', r'pip', r'library'
            ],
            'exceptions': [
                r'try', r'except', r'finally', r'raise', r'exception'
            ],
            'file_io': [
                r'open', r'read', r'write', r'file', r'with'
            ]
        },
        
        # SQL
        'sql': {
            'queries': [
                r'select', r'where', r'order by', r'group by', r'having'
            ],
            'joins': [
                r'join', r'inner join', r'left join', r'right join', r'outer join'
            ],
            'dml': [
                r'insert', r'update', r'delete', r'truncate'
            ],
            'ddl': [
                r'create', r'alter', r'drop', r'table', r'index'
            ],
            'functions': [
                r'count', r'sum', r'avg', r'max', r'min', r'aggregate'
            ],
            'subqueries': [
                r'subquery', r'nested', r'in', r'exists'
            ]
        },
        
        # GIT
        'git': {
            'basics': [
                r'git init', r'git clone', r'git status', r'git add', r'git commit'
            ],
            'branching': [
                r'branch', r'checkout', r'switch', r'git branch'
            ],
            'merging': [
                r'merge', r'rebase', r'conflict', r'resolve'
            ],
            'remote': [
                r'push', r'pull', r'fetch', r'remote', r'origin'
            ],
            'history': [
                r'log', r'diff', r'show', r'blame'
            ]
        },
        
        # DJANGO
        'django': {
            'models': [
                r'model', r'field', r'foreignkey', r'manytomany', r'onetone'
            ],
            'views': [
                r'view', r'function view', r'class view', r'generic view'
            ],
            'templates': [
                r'template', r'template tag', r'filter', r'extends', r'include'
            ],
            'forms': [
                r'form', r'modelform', r'validation', r'clean'
            ],
            'orm': [
                r'queryset', r'filter', r'get', r'all', r'annotate', r'aggregate'
            ],
            'urls': [
                r'url', r'path', r'urlpattern', r'routing'
            ],
            'admin': [
                r'admin', r'modeladmin', r'register'
            ]
        },
        
        # BASES DE DONNÉES
        'database': {
            'normalization': [
                r'normalization', r'1nf', r'2nf', r'3nf', r'bcnf'
            ],
            'indexing': [
                r'index', r'primary key', r'foreign key', r'unique'
            ],
            'transactions': [
                r'transaction', r'commit', r'rollback', r'acid'
            ],
            'optimization': [
                r'optimization', r'query plan', r'explain', r'performance'
            ]
        }
    }
    
    # Labels français pour les compétences
    SKILL_LABELS = {
        'react': {
            'hooks': 'Hooks React (useState, useEffect, etc.)',
            'components': 'Composants et cycle de vie',
            'routing': 'Routing et navigation',
            'state_management': 'Gestion d\'état (Redux, Context)',
            'performance': 'Optimisation des performances',
            'events': 'Gestion des événements',
            'forms': 'Formulaires et validation',
            'jsx': 'JSX et syntaxe'
        },
        'javascript': {
            'es6': 'Syntaxe ES6+ moderne',
            'async': 'Programmation asynchrone',
            'dom': 'Manipulation du DOM',
            'arrays': 'Méthodes de tableaux',
            'objects': 'Objets et prototypes',
            'closures': 'Closures et scope',
            'classes': 'Classes et héritage'
        },
        'python': {
            'basics': 'Types de données de base',
            'oop': 'Programmation orientée objet',
            'functions': 'Fonctions et lambdas',
            'data_structures': 'Structures de données',
            'modules': 'Modules et packages',
            'exceptions': 'Gestion des exceptions',
            'file_io': 'Fichiers et I/O'
        },
        'sql': {
            'queries': 'Requêtes SELECT',
            'joins': 'Jointures (INNER, LEFT, RIGHT)',
            'dml': 'Manipulation de données (INSERT, UPDATE, DELETE)',
            'ddl': 'Définition de schéma (CREATE, ALTER)',
            'functions': 'Fonctions d\'agrégation',
            'subqueries': 'Sous-requêtes'
        },
        'git': {
            'basics': 'Commandes de base',
            'branching': 'Gestion des branches',
            'merging': 'Fusion et résolution de conflits',
            'remote': 'Collaboration à distance',
            'history': 'Historique et différences'
        },
        'django': {
            'models': 'Modèles et relations',
            'views': 'Vues et contrôleurs',
            'templates': 'Templates et affichage',
            'forms': 'Formulaires',
            'orm': 'ORM et requêtes',
            'urls': 'Routage d\'URLs',
            'admin': 'Interface d\'administration'
        },
        'database': {
            'normalization': 'Normalisation',
            'indexing': 'Index et clés',
            'transactions': 'Transactions',
            'optimization': 'Optimisation de requêtes'
        }
    }
    
    def __init__(self):
        """Initialiser l'analyseur"""
        self.skill_scores = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    
    def detect_skill_from_question(self, question_text: str, options: List[str] = None) -> List[Tuple[str, str]]:
        """
        Détecter les compétences spécifiques d'une question.
        
        Args:
            question_text: Texte de la question
            options: Liste des options de réponse (optionnel)
            
        Returns:
            Liste de tuples (matière, compétence)
        """
        detected_skills = []
        full_text = question_text.lower()
        
        # Ajouter les options au texte à analyser
        if options:
            full_text += ' ' + ' '.join([str(opt).lower() for opt in options])
        
        # Parcourir tous les patterns
        for subject, skills in self.SKILL_PATTERNS.items():
            for skill_name, patterns in skills.items():
                # Vérifier si un pattern correspond
                for pattern in patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        detected_skills.append((subject, skill_name))
                        break  # Une seule détection par compétence
        
        return detected_skills
    
    def analyze_question_result(self, question_text: str, options: List[str], 
                                is_correct: bool, subject: str = None):
        """
        Analyser le résultat d'une question et mettre à jour les scores.
        
        Args:
            question_text: Texte de la question
            options: Options de la question
            is_correct: Si la réponse était correcte
            subject: Matière du test (optionnel, pour contexte)
        """
        # Détecter les compétences
        skills = self.detect_skill_from_question(question_text, options)
        
        # Si aucune compétence détectée mais sujet connu, utiliser "général"
        if not skills and subject:
            subject_key = subject.lower().replace(' ', '_')
            skills = [(subject_key, 'general')]
        
        # Mettre à jour les scores
        for subject_key, skill_name in skills:
            self.skill_scores[subject_key][skill_name]['total'] += 1
            if is_correct:
                self.skill_scores[subject_key][skill_name]['correct'] += 1
    
    def get_detailed_analysis(self, min_questions: int = 3) -> Dict:
        """
        Obtenir l'analyse détaillée des compétences.
        
        Args:
            min_questions: Nombre minimum de questions pour considérer une compétence
            
        Returns:
            Dict avec strengths, weaknesses, recommendations
        """
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyser chaque matière et compétence
        for subject, skills in self.skill_scores.items():
            for skill_name, scores in skills.items():
                if scores['total'] < min_questions:
                    continue  # Pas assez de données
                
                percentage = (scores['correct'] / scores['total'] * 100) if scores['total'] > 0 else 0
                
                # Obtenir le label français
                skill_label = self._get_skill_label(subject, skill_name)
                subject_label = self._get_subject_label(subject)
                
                # Déterminer si c'est un point fort ou faible
                if percentage >= 80:
                    strengths.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'percentage': round(percentage, 1),
                        'correct': scores['correct'],
                        'total': scores['total'],
                        'level': 'excellence',
                        'description': f"Excellence en {subject_label} : {skill_label} ({percentage:.0f}% - {scores['correct']}/{scores['total']})"
                    })
                elif percentage >= 70:
                    strengths.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'percentage': round(percentage, 1),
                        'correct': scores['correct'],
                        'total': scores['total'],
                        'level': 'good',
                        'description': f"Bonne maîtrise de {subject_label} : {skill_label} ({percentage:.0f}% - {scores['correct']}/{scores['total']})"
                    })
                elif percentage < 60:
                    weaknesses.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'percentage': round(percentage, 1),
                        'correct': scores['correct'],
                        'total': scores['total'],
                        'severity': 'high' if percentage < 40 else 'medium',
                        'description': f"À améliorer en {subject_label} : {skill_label} ({percentage:.0f}% - {scores['correct']}/{scores['total']})"
                    })
                    
                    # Générer recommandation spécifique
                    recommendations.append({
                        'subject': subject_label,
                        'skill': skill_label,
                        'priority': 'high' if percentage < 40 else 'medium',
                        'title': f"Renforcer {skill_label}",
                        'description': f"Vous avez {percentage:.0f}% de réussite en {skill_label}. Pratiquez davantage avec des exercices ciblés.",
                        'action': f"Faire 5-10 exercices supplémentaires sur {skill_label}"
                    })
        
        # Trier par pourcentage
        strengths.sort(key=lambda x: x['percentage'], reverse=True)
        weaknesses.sort(key=lambda x: x['percentage'])
        recommendations.sort(key=lambda x: (x['priority'] == 'high', -weaknesses[recommendations.index(x)]['percentage'] if x in [r for r in recommendations] else 0), reverse=True)
        
        return {
            'strengths': strengths[:10],  # Top 10
            'weaknesses': weaknesses[:10],  # Top 10
            'recommendations': recommendations[:8],  # Top 8
            'total_skills_analyzed': sum(len(skills) for skills in self.skill_scores.values()),
            'subjects_covered': len(self.skill_scores)
        }
    
    def _get_skill_label(self, subject: str, skill_name: str) -> str:
        """Obtenir le label français d'une compétence"""
        if subject in self.SKILL_LABELS and skill_name in self.SKILL_LABELS[subject]:
            return self.SKILL_LABELS[subject][skill_name]
        return skill_name.replace('_', ' ').title()
    
    def _get_subject_label(self, subject: str) -> str:
        """Obtenir le label français d'une matière"""
        labels = {
            'react': 'React',
            'javascript': 'JavaScript',
            'python': 'Python',
            'sql': 'SQL',
            'git': 'Git',
            'django': 'Django',
            'database': 'Bases de données'
        }
        return labels.get(subject, subject.title())


def analyze_student_results_detailed(student, results_queryset):
    """
    Analyser en détail les résultats d'un étudiant.
    
    Args:
        student: User object
        results_queryset: QuerySet de Result
        
    Returns:
        Dict avec analyse détaillée
    """
    from evaluation.models import Question, Submission
    
    analyzer = EnhancedSkillAnalyzer()
    
    # Analyser chaque résultat
    for result in results_queryset:
        try:
            # Récupérer la soumission
            submission = result.submission
            test = result.test
            
            # Récupérer les questions du test
            questions = Question.objects.filter(test=test)
            
            # Analyser les réponses de l'étudiant
            student_answers = submission.answers if hasattr(submission, 'answers') else {}
            
            for question in questions:
                # Déterminer si la réponse était correcte
                is_correct = False
                if isinstance(student_answers, dict) and str(question.id) in student_answers:
                    student_answer = student_answers[str(question.id)]
                    # Comparer avec la bonne réponse
                    if hasattr(question, 'correct_answer'):
                        is_correct = (student_answer == question.correct_answer)
                
                # Extraire les options
                options = []
                if hasattr(question, 'options') and question.options:
                    if isinstance(question.options, dict):
                        options = list(question.options.values())
                    elif isinstance(question.options, list):
                        options = question.options
                
                # Analyser la question
                analyzer.analyze_question_result(
                    question_text=question.question_text,  # ✅ Utiliser question_text
                    options=options,
                    is_correct=is_correct,
                    subject=test.subject
                )
        
        except Exception as e:
            print(f"Erreur lors de l'analyse du résultat {result.id}: {e}")
            continue
    
    # Obtenir l'analyse
    return analyzer.get_detailed_analysis()
