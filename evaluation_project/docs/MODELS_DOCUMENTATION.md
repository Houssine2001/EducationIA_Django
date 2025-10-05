# 📋 Documentation des Modèles MongoDB

## Vue d'Ensemble

Ce document décrit les modèles de données pour le système d'évaluation et de suivi des performances avec IA, optimisés pour MongoDB via Djongo.

---

## 🗂️ Structure des Modèles

### 1. UserProfile - Profil Utilisateur/Étudiant

**Collection MongoDB**: `user_profiles`

**Description**: Extension du modèle User Django avec données académiques et analyses de performance.

#### Champs Principaux

| Champ | Type | Description |
|-------|------|-------------|
| `user` | OneToOne | Liaison avec Django User |
| `student_id` | String | Identifiant unique étudiant |
| `class_level` | String | Niveau scolaire |
| `total_tests_taken` | Integer | Nombre total de tests passés |
| `average_score` | Float | Score moyen global |
| `strengths` | JSONField | Liste des points forts |
| `weaknesses` | JSONField | Liste des points faibles |
| `ai_recommendations` | JSONField | Recommandations IA personnalisées |
| `performance_history` | JSONField | Historique des performances |
| `skill_progress` | JSONField | Progression par compétence |

#### Structure JSON

```json
{
  "strengths": ["mathématiques", "logique", "analyse"],
  "weaknesses": ["orthographe", "grammaire"],
  "ai_recommendations": {
    "focus_areas": ["Améliorer la grammaire française"],
    "suggested_exercises": ["Exercices de conjugaison"],
    "learning_path": "progressive"
  },
  "performance_history": [
    {"date": "2025-10-01", "score": 85, "test_id": 1},
    {"date": "2025-10-05", "score": 90, "test_id": 2}
  ],
  "skill_progress": {
    "mathématiques": {"initial": 70, "current": 85, "target": 90},
    "français": {"initial": 60, "current": 65, "target": 80}
  }
}
```

---

### 2. Test - Test/Évaluation

**Collection MongoDB**: `tests`

**Description**: Modèle pour les tests et évaluations avec métadonnées complètes.

#### Champs Principaux

| Champ | Type | Description |
|-------|------|-------------|
| `title` | String | Titre du test |
| `subject` | String | Matière (Math, Français, etc.) |
| `difficulty` | Choice | Niveau de difficulté (easy/medium/hard/expert) |
| `duration` | Integer | Durée en minutes |
| `passing_score` | Float | Score minimum pour réussir (%) |
| `status` | Choice | Statut (draft/published/archived) |
| `tags` | JSONField | Tags pour catégorisation |
| `skills_tested` | JSONField | Compétences évaluées |
| `ai_metadata` | JSONField | Métadonnées pour analyse IA |

#### Structure JSON

```json
{
  "tags": ["algèbre", "équations", "niveau-seconde"],
  "skills_tested": ["calcul", "raisonnement logique", "résolution de problèmes"],
  "ai_metadata": {
    "recommended_for": ["students_weak_in_algebra"],
    "prerequisite_skills": ["arithmétique de base"],
    "difficulty_score": 0.75,
    "estimated_time": 45
  }
}
```

---

### 3. Question - Question

**Collection MongoDB**: `questions`

**Description**: Questions individuelles avec support multi-formats (QCM, Vrai/Faux, Rédaction).

#### Types de Questions

- **mcq**: QCM (Choix Multiple)
- **true_false**: Vrai/Faux
- **short_answer**: Réponse Courte
- **essay**: Rédaction
- **fill_blank**: Texte à Trous

#### Champs Principaux

| Champ | Type | Description |
|-------|------|-------------|
| `question_text` | Text | Texte de la question |
| `question_type` | Choice | Type de question |
| `points` | Float | Points attribués |
| `options` | JSONField | Options pour QCM |
| `correct_answer` | Text | Réponse correcte |
| `skills` | JSONField | Compétences évaluées |
| `ai_analysis` | JSONField | Analyse IA de la question |
| `common_mistakes` | JSONField | Erreurs fréquentes |

#### Structure JSON - Options QCM

```json
{
  "options": [
    {"id": "A", "text": "Paris", "is_correct": true},
    {"id": "B", "text": "Londres", "is_correct": false},
    {"id": "C", "text": "Berlin", "is_correct": false},
    {"id": "D", "text": "Madrid", "is_correct": false}
  ]
}
```

#### Structure JSON - Analyse IA

```json
{
  "ai_analysis": {
    "difficulty_score": 0.65,
    "cognitive_level": "application",
    "bloom_taxonomy": "level_3",
    "estimated_time": 90
  },
  "common_mistakes": [
    {
      "mistake": "Confusion entre capitale politique et économique",
      "frequency": 0.35,
      "explanation": "Beaucoup confondent Paris avec d'autres grandes villes"
    }
  ]
}
```

---

### 4. Submission - Soumission/Réponses

**Collection MongoDB**: `submissions`

**Description**: Soumissions de tests par les étudiants avec réponses et métadonnées.

#### Champs Principaux

| Champ | Type | Description |
|-------|------|-------------|
| `student` | ForeignKey | Étudiant ayant soumis |
| `test` | ForeignKey | Test concerné |
| `status` | Choice | Statut (in_progress/submitted/graded) |
| `answers` | JSONField | Réponses de l'étudiant |
| `score` | Float | Score obtenu |
| `ai_feedback` | JSONField | Feedback automatique IA |
| `performance_analysis` | JSONField | Analyse détaillée |

#### Structure JSON - Réponses

```json
{
  "answers": {
    "question_1": {
      "answer": "A",
      "time_spent": 45,
      "is_correct": true,
      "confidence": 0.8
    },
    "question_2": {
      "answer": "B",
      "time_spent": 120,
      "is_correct": false,
      "confidence": 0.5
    }
  }
}
```

#### Structure JSON - Feedback IA

```json
{
  "ai_feedback": {
    "overall_performance": "Bon travail ! Quelques points à améliorer.",
    "strengths_shown": ["Rapidité de calcul", "Logique"],
    "areas_to_improve": ["Attention aux détails", "Vérification"],
    "personalized_tips": [
      "Prenez le temps de relire vos réponses",
      "Pratiquez les exercices sur les fractions"
    ]
  },
  "performance_analysis": {
    "speed_score": 0.85,
    "accuracy_score": 0.75,
    "consistency_score": 0.80,
    "improvement_rate": 0.12
  }
}
```

---

### 5. Result - Résultats & Statistiques

**Collection MongoDB**: `results`

**Description**: Résultats détaillés avec analyses approfondies et recommandations IA.

#### Champs Principaux

| Champ | Type | Description |
|-------|------|-------------|
| `submission` | OneToOne | Soumission associée |
| `total_score` | Float | Score total |
| `percentage_score` | Float | Pourcentage |
| `grade` | String | Note lettre (A+, A, B, etc.) |
| `skills_breakdown` | JSONField | Analyse par compétence |
| `rank` | Integer | Classement |
| `ai_analysis` | JSONField | Analyse IA complète |
| `recommendations` | JSONField | Recommandations |
| `error_patterns` | JSONField | Patterns d'erreurs |

#### Structure JSON - Analyse IA Complète

```json
{
  "ai_analysis": {
    "strengths": [
      "Excellente compréhension des concepts de base",
      "Rapidité de calcul mental",
      "Bonne gestion du temps"
    ],
    "weaknesses": [
      "Attention aux détails insuffisante",
      "Erreurs d'inattention fréquentes",
      "Vérification des résultats à améliorer"
    ],
    "recommendations": [
      "Pratiquer 15 min/jour sur les exercices de vérification",
      "Utiliser la méthode de double vérification",
      "Faire des pauses régulières pendant les tests longs"
    ],
    "predicted_next_score": 88.5,
    "learning_trajectory": "progressive",
    "confidence_score": 0.92,
    "study_time_needed": 120,
    "optimal_practice_frequency": "daily"
  }
}
```

#### Structure JSON - Breakdown Compétences

```json
{
  "skills_breakdown": {
    "calcul": {
      "score": 90,
      "percentage": 90,
      "questions_answered": 10,
      "questions_correct": 9,
      "improvement": "+5%"
    },
    "logique": {
      "score": 85,
      "percentage": 85,
      "questions_answered": 8,
      "questions_correct": 7,
      "improvement": "+3%"
    },
    "raisonnement": {
      "score": 75,
      "percentage": 75,
      "questions_answered": 12,
      "questions_correct": 9,
      "improvement": "-2%"
    }
  }
}
```

#### Structure JSON - Patterns d'Erreurs

```json
{
  "error_patterns": [
    {
      "pattern_type": "calculation_error",
      "frequency": 0.25,
      "affected_skills": ["calcul mental", "arithmétique"],
      "severity": "medium",
      "suggestion": "Pratiquer les tables de multiplication"
    },
    {
      "pattern_type": "time_management",
      "frequency": 0.15,
      "affected_skills": ["gestion du temps"],
      "severity": "low",
      "suggestion": "Utiliser un chronomètre pendant la pratique"
    }
  ]
}
```

---

## 🔗 Relations entre Modèles

```
User (Django)
    ↓ (OneToOne)
UserProfile
    ↓
    ├── Submissions (Multiple)
    │       ↓ (OneToOne)
    │   Results
    │
    └── Tests créés (si professeur)

Test
    ↓ (Multiple)
Questions
    ↓
Submissions → Results
```

---

## 📊 Utilisation Pratique

### Créer un Profil Utilisateur

```python
from django.contrib.auth.models import User
from evaluation.models import UserProfile

# Créer ou récupérer un utilisateur
user = User.objects.get(username='etudiant1')

# Créer le profil
profile = UserProfile.objects.create(
    user=user,
    student_id='ETU2025001',
    class_level='Seconde',
    strengths=['mathématiques', 'physique'],
    weaknesses=['français', 'histoire']
)
```

### Créer un Test

```python
from evaluation.models import Test

test = Test.objects.create(
    title='Test d\'Algèbre - Chapitre 1',
    subject='Mathématiques',
    topic='Équations du premier degré',
    difficulty='medium',
    duration=45,
    passing_score=60.0,
    tags=['algèbre', 'équations', 'seconde'],
    skills_tested=['calcul', 'raisonnement']
)
```

### Créer des Questions

```python
from evaluation.models import Question

# Question QCM
question_mcq = Question.objects.create(
    test=test,
    question_text='Quelle est la capitale de la France?',
    question_type='mcq',
    points=1.0,
    options=[
        {'id': 'A', 'text': 'Paris', 'is_correct': True},
        {'id': 'B', 'text': 'Londres', 'is_correct': False},
        {'id': 'C', 'text': 'Berlin', 'is_correct': False},
    ],
    skills=['culture générale']
)

# Question Vrai/Faux
question_tf = Question.objects.create(
    test=test,
    question_text='2 + 2 = 4',
    question_type='true_false',
    points=0.5,
    correct_answer='True',
    skills=['calcul']
)
```

---

## 🤖 Intégration IA

Tous les modèles incluent des champs JSON pour stocker :

1. **Analyses IA** : Patterns, prédictions, classifications
2. **Recommandations** : Suggestions personnalisées basées sur les performances
3. **Métadonnées** : Données pour entraînement et amélioration des modèles ML

### Exemple d'Utilisation IA

```python
# Après analyse IA d'une soumission
submission.ai_feedback = {
    'overall_performance': 'Très bon travail !',
    'strengths_shown': ['rapidité', 'précision'],
    'areas_to_improve': ['gestion du temps'],
    'confidence_score': 0.89
}
submission.save()

# Mise à jour du profil avec recommandations
profile.ai_recommendations = {
    'focus_areas': ['Améliorer la gestion du temps'],
    'suggested_practice': ['Tests chronométrés'],
    'expected_improvement': 5.5
}
profile.save()
```

---

## 🛠️ Bonnes Pratiques

1. **Utiliser JSONField** pour les données flexibles et évolutives
2. **Indexer** les champs fréquemment recherchés
3. **Valider** les données avant sauvegarde
4. **Documenter** les structures JSON
5. **Tester** les requêtes complexes sur MongoDB

---

## 📝 Notes Importantes

- Les modèles utilisent **Djongo** pour compatibilité MongoDB
- Les champs JSON permettent une **flexibilité maximale**
- L'architecture est **prête pour l'IA** avec de nombreux champs dédiés
- Les **relations** restent simples malgré NoSQL
- Les **métadonnées** facilitent les analyses futures

---

*Documentation mise à jour le : 5 octobre 2025*
