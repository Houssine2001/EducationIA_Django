"""
Générateur de questions réalistes avec mots-clés techniques pour l'analyse granulaire.

Au lieu de :
- "Question 1 sur Mathématiques?" ❌

Génère :
- "Comment utiliser useState et useEffect ensemble dans React?" ✅
- "Quelle est la différence entre INNER JOIN et LEFT JOIN en SQL?" ✅
- "Comment résoudre un conflit de merge dans Git?" ✅
"""

# Templates de questions par matière et compétence
QUESTION_TEMPLATES = {
    'Mathématiques': {
        'algèbre': [
            "Résoudre l'équation du second degré: x² + {a}x + {b} = 0",
            "Factoriser l'expression: {a}x² + {b}x + {c}",
            "Simplifier l'expression algébrique: ({a}x + {b})({c}x + {d})",
        ],
        'géométrie': [
            "Calculer l'aire d'un triangle avec base {a}cm et hauteur {b}cm",
            "Trouver le périmètre d'un cercle de rayon {a}cm (π = 3.14)",
            "Calculer le volume d'un cube d'arête {a}cm",
        ],
        'fonctions': [
            "Déterminer la dérivée de f(x) = {a}x² + {b}x + {c}",
            "Trouver les racines de la fonction f(x) = x² - {a}x + {b}",
            "Calculer l'intégrale de f(x) = {a}x + {b} entre 0 et {c}",
        ]
    },
    
    'Informatique': {
        'python_basics': [
            "Quel est le type de données retourné par len([1, 2, 3])?",
            "Comment déclarer une variable en Python?",
            "Quelle est la différence entre list et tuple?",
        ],
        'python_oop': [
            "Comment créer une class en Python avec __init__?",
            "Qu'est-ce que l'héritage (inheritance) en Python?",
            "Comment utiliser super() dans une classe enfant?",
        ],
        'algorithms': [
            "Quelle est la complexité temporelle de la recherche binaire?",
            "Comment implémenter un tri à bulles (bubble sort)?",
            "Qu'est-ce qu'une structure de données pile (stack)?",
        ],
        'data_structures': [
            "Quelle est la différence entre list et dictionary?",
            "Comment utiliser les comprehensions de liste?",
            "Qu'est-ce qu'un set et quand l'utiliser?",
        ]
    },
    
    'Physique': {
        'mécanique': [
            "Calculer la force avec F = m × a si m = {a}kg et a = {b}m/s²",
            "Trouver l'énergie cinétique: E = ½mv² avec m = {a}kg et v = {b}m/s",
            "Déterminer la vitesse après {a}s avec accélération {b}m/s²",
        ],
        'électricité': [
            "Calculer la résistance totale de {a}Ω et {b}Ω en série",
            "Trouver l'intensité avec U = {a}V et R = {b}Ω (loi d'Ohm)",
            "Calculer la puissance: P = UI avec U = {a}V et I = {b}A",
        ],
        'optique': [
            "Calculer l'indice de réfraction avec sin(i) = {a} et sin(r) = {b}",
            "Trouver la distance focale d'une lentille convergente",
            "Déterminer la position de l'image avec une lentille",
        ]
    },
    
    'Chimie': {
        'réactions': [
            "Équilibrer l'équation: H₂ + O₂ → H₂O",
            "Calculer la masse molaire de H₂SO₄",
            "Déterminer le nombre de moles dans {a}g de NaCl",
        ],
        'pH': [
            "Calculer le pH d'une solution avec [H⁺] = {a} mol/L",
            "Quelle est la nature acide/basique d'une solution de pH {a}?",
            "Calculer la concentration en OH⁻ si pH = {a}",
        ],
        'atomes': [
            "Combien d'électrons dans l'atome de carbone (Z = 6)?",
            "Quelle est la configuration électronique de l'oxygène?",
            "Déterminer le nombre de neutrons dans un isotope",
        ]
    },
    
    'Français': {
        'grammaire': [
            "Conjuguer le verbe 'aller' au présent de l'indicatif",
            "Identifier le COD dans : 'Je mange une pomme'",
            "Accorder l'adjectif : 'Les fleurs sont ______ (beau)'",
        ],
        'orthographe': [
            "Choisir la bonne orthographe : leur/leurs",
            "Écrire le pluriel de 'cheval'",
            "Accorder le participe passé : 'Les lettres qu'il a ______' (écrire)",
        ],
        'conjugaison': [
            "Conjuguer 'être' au passé composé (3ème personne pluriel)",
            "Imparfait ou passé simple : Il ______ (venir) me voir",
            "Conditionnel présent de 'pouvoir' (2ème personne singulier)",
        ]
    },
    
    'Anglais': {
        'grammar': [
            "Choose the correct form: He ______ (go/goes) to school",
            "Past simple of 'eat': I ______ an apple yesterday",
            "Present perfect: She ______ (live) here for 5 years",
        ],
        'vocabulary': [
            "Translate: 'Bonjour' in English",
            "What is the opposite of 'happy'?",
            "Choose the synonym of 'big': large/small/tall",
        ],
        'tenses': [
            "Future: Tomorrow I ______ (go) to Paris",
            "Present continuous: They ______ (play) football now",
            "Past continuous: I ______ (read) when he arrived",
        ]
    },
    
    'Histoire': {
        'dates': [
            "En quelle année a eu lieu la Révolution française?",
            "Quand a commencé la Première Guerre mondiale?",
            "Date de la chute du mur de Berlin?",
        ],
        'personnages': [
            "Qui était Napoléon Bonaparte?",
            "Quel rôle a joué Louis XIV dans l'histoire de France?",
            "Qui a découvert l'Amérique en 1492?",
        ],
        'événements': [
            "Qu'est-ce que la Renaissance?",
            "Expliquer la Révolution industrielle",
            "Qu'est-ce que la Guerre froide?",
        ]
    },
    
    'Géographie': {
        'capitales': [
            "Quelle est la capitale de la France?",
            "Capitale de l'Espagne?",
            "Quelle ville est la capitale de l'Italie?",
        ],
        'continents': [
            "Combien de continents y a-t-il?",
            "Quel est le plus grand continent?",
            "Sur quel continent se trouve le Brésil?",
        ],
        'relief': [
            "Quel est le plus haut sommet du monde?",
            "Qu'est-ce qu'une plaine?",
            "Différence entre montagne et colline?",
        ]
    }
}

# Options de réponse par matière
ANSWER_OPTIONS = {
    'Mathématiques': {
        'algèbre': lambda a, b, c: [
            f"{a}", f"{b}", f"{c}", f"{a+b}"
        ],
        'géométrie': lambda a, b: [
            f"{a*b}cm²", f"{a+b}cm²", f"{(a*b)/2}cm²", f"{2*(a+b)}cm"
        ],
    },
    'Informatique': {
        'python_basics': [
            ['int', 'str', 'list', 'tuple'],
            ['var x = 5', 'x = 5', 'int x = 5', 'define x = 5'],
            ['list mutable, tuple immutable', 'list immutable, tuple mutable', 'Aucune différence', 'list plus rapide']
        ],
        'python_oop': [
            ['def __init__(self):', 'function __init__():', 'init(self):', 'constructor():'],
            ['Réutiliser du code', 'Créer des variables', 'Importer des modules', 'Rien']
        ]
    }
}


def generate_realistic_question(subject: str, skill: str = None, params: dict = None):
    """
    Générer une question réaliste avec mots-clés techniques.
    
    Args:
        subject: Matière (Mathématiques, Informatique, etc.)
        skill: Compétence spécifique (optionnel)
        params: Paramètres pour personnaliser (optionnel)
        
    Returns:
        dict avec question_text, options, correct_answer, skill
    """
    import random
    
    if params is None:
        params = {
            'a': random.randint(1, 10),
            'b': random.randint(1, 10),
            'c': random.randint(1, 10),
            'd': random.randint(1, 10)
        }
    
    # Sélectionner une compétence aléatoire si non spécifiée
    if subject in QUESTION_TEMPLATES:
        available_skills = list(QUESTION_TEMPLATES[subject].keys())
        if skill is None or skill not in available_skills:
            skill = random.choice(available_skills)
        
        # Sélectionner un template
        templates = QUESTION_TEMPLATES[subject][skill]
        question_text = random.choice(templates).format(**params)
        
        # Générer options
        if subject in ANSWER_OPTIONS and skill in ANSWER_OPTIONS[subject]:
            if callable(ANSWER_OPTIONS[subject][skill]):
                options = ANSWER_OPTIONS[subject][skill](params['a'], params['b'], params.get('c', 0))
            else:
                options = random.choice(ANSWER_OPTIONS[subject][skill])
        else:
            # Options génériques
            options = [
                f"Option A ({params['a']})",
                f"Option B ({params['b']})",
                f"Option C ({params['c']})",
                f"Option D ({params['a'] + params['b']})"
            ]
        
        correct_index = random.randint(0, len(options) - 1)
        
        return {
            'question_text': question_text,
            'options': [
                {'text': opt, 'is_correct': i == correct_index}
                for i, opt in enumerate(options)
            ],
            'correct_answer': options[correct_index],
            'skill': skill,
            'difficulty': random.choice(['easy', 'medium', 'hard'])
        }
    
    # Fallback pour matières sans templates
    return {
        'question_text': f"Question sur {subject} - {skill or 'général'}",
        'options': [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': False},
            {'text': 'Option C', 'is_correct': False},
            {'text': 'Option D', 'is_correct': False}
        ],
        'correct_answer': 'Option A',
        'skill': skill or 'general',
        'difficulty': 'medium'
    }
