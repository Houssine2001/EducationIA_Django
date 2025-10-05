# 🤖 Guide d'Intégration de l'IA avec Hugging Face

## Vue d'Ensemble

Ce guide explique comment intégrer et utiliser l'IA pour :
- ✅ Corriger automatiquement les questions ouvertes
- ✅ Générer du feedback personnalisé
- ✅ Identifier les points faibles des étudiants
- ✅ Fournir des recommandations d'apprentissage

---

## 📦 Étape 1 : Installation des Dépendances

### Mettre à jour requirements.txt

Ajoutez ces packages au fichier `requirements.txt` :

```txt
# Déjà installés
Django==4.2.16
djongo==1.2.31
pymongo==4.3.3
six==1.16.0

# Nouveaux packages pour IA
requests==2.31.0          # Pour appels API
transformers==4.30.0      # (Optionnel) Hugging Face local
torch==2.0.1              # (Optionnel) Pour modèles locaux
```

### Installer les packages

```bash
pip install requests
```

**Note** : Les packages `transformers` et `torch` sont **optionnels** et uniquement nécessaires si vous voulez exécuter les modèles IA localement (consomme beaucoup de ressources).

---

## 🔑 Étape 2 : Obtenir une Clé API Hugging Face (GRATUIT)

### 2.1 Créer un Compte

1. Allez sur https://huggingface.co/
2. Cliquez sur **Sign Up** (gratuit)
3. Vérifiez votre email

### 2.2 Générer un Token API

1. Une fois connecté, allez sur votre **Profile** → **Settings**
2. Cliquez sur **Access Tokens**
3. Cliquez sur **New token**
4. Donnez un nom (ex: "EvaluationIA")
5. Sélectionnez le type : **Read** (suffisant)
6. Cliquez sur **Generate**
7. **Copiez le token** (vous ne le verrez qu'une fois)

Exemple de token : `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## ⚙️ Étape 3 : Configuration dans Django

### 3.1 Ajouter le Token dans settings.py

Ouvrez `backend/settings.py` et ajoutez à la fin :

```python
# ============================================
# Configuration Hugging Face IA
# ============================================

HUGGINGFACE_API_TOKEN = 'hf_votre_token_ici'  # Remplacez par votre token

# Modèles IA utilisés
AI_MODELS = {
    'text_generation': 'mistralai/Mistral-7B-Instruct-v0.1',
    'sentiment': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
    'summarization': 'facebook/bart-large-cnn',
}
```

### 3.2 Utiliser les Variables d'Environnement (Recommandé)

Pour la **sécurité**, utilisez plutôt un fichier `.env` :

**Créer `.env` à la racine du projet** :

```env
HUGGINGFACE_API_TOKEN=hf_votre_token_ici
DEBUG=True
SECRET_KEY=votre-secret-key
```

**Installer python-decouple** :

```bash
pip install python-decouple
```

**Modifier settings.py** :

```python
from decouple import config

# Configuration Hugging Face
HUGGINGFACE_API_TOKEN = config('HUGGINGFACE_API_TOKEN', default=None)
```

---

## 🚀 Étape 4 : Utilisation de l'IA

### 4.1 Services IA Disponibles

Le fichier `ai_modules/ai_services.py` contient 3 services principaux :

#### 1. **EssayGrader** - Correction de Questions Ouvertes

```python
from ai_modules.ai_services import EssayGrader

# Initialiser le service
grader = EssayGrader()

# Corriger une rédaction
result = grader.grade_essay(
    question=question_instance,
    student_answer="Réponse de l'étudiant...",
    max_points=10
)

print(result)
# {
#     'points_earned': 7.5,
#     'feedback': "Bonne analyse mais manque de détails...",
#     'positive_points': [...],
#     'improvements': [...]
# }
```

#### 2. **FeedbackGenerator** - Feedback Personnalisé

```python
from ai_modules.ai_services import FeedbackGenerator

generator = FeedbackGenerator()

# Générer du feedback basé sur le profil et les résultats
feedback = generator.generate_personalized_feedback(
    student_profile=profile,
    result=result_instance
)

print(feedback)
# {
#     'overall_feedback': "Excellent travail en mathématiques...",
#     'encouragement': "Continuez ainsi !",
#     'ai_generated': True
# }
```

#### 3. **WeaknessAnalyzer** - Analyse des Points Faibles

```python
from ai_modules.ai_services import WeaknessAnalyzer

analyzer = WeaknessAnalyzer()

# Analyser les faiblesses sur les derniers tests
analysis = analyzer.identify_weaknesses(
    student_profile=profile,
    recent_results=recent_results_queryset
)

print(analysis)
# {
#     'weaknesses': [
#         {'skill': 'Grammaire', 'average_score': 55, 'trend': 'declining'}
#     ],
#     'strengths': [
#         {'skill': 'Mathématiques', 'average_score': 85}
#     ],
#     'recommendations': [...]
# }
```

### 4.2 Intégration Automatique dans les Vues

L'IA est **déjà intégrée** dans les vues Django :

**Lors de la soumission d'un test** (`views.py` → `submit_test`) :

```python
# Correction automatique
grading_results = TestService.submit_test(submission, answers)

# Création du résultat
result = ResultService.create_detailed_result(submission, grading_results)

# 🤖 Génération automatique du feedback IA
profile = UserProfile.objects.get(user=request.user)
ai_services = get_ai_services()
feedback = ai_services['feedback_generator'].generate_personalized_feedback(
    profile, result
)

# Sauvegarde du feedback
result.ai_analysis = feedback
result.save()
```

**Page de progression** (`views.py` → `student_progress`) :

```python
# 🤖 Analyse automatique des faiblesses
ai_services = get_ai_services()
weaknesses_analysis = ai_services['weakness_analyzer'].identify_weaknesses(
    profile, recent_results
)
```

---

## 🔧 Étape 5 : Test de l'API Hugging Face

### Test Simple dans le Shell Django

```bash
python manage.py shell
```

```python
from ai_modules.ai_services import HuggingFaceAI

# Initialiser l'IA
ai = HuggingFaceAI()

# Test de génération de texte
prompt = "Évalue cette réponse d'étudiant: La photosynthèse est..."
result = ai.generate_text(prompt, max_length=100)
print(result)

# Test d'analyse de sentiment
sentiment = ai.analyze_sentiment("Excellent travail !")
print(sentiment)
```

### Test Complet avec une Question

```python
from evaluation.models import Question, Test
from ai_modules.ai_services import EssayGrader

# Créer une question test
test = Test.objects.first()
question = Question.objects.create(
    test=test,
    question_text="Qu'est-ce que la photosynthèse ?",
    question_type='essay',
    points=10.0,
    explanation="La photosynthèse est le processus..."
)

# Tester la correction IA
grader = EssayGrader()
result = grader.grade_essay(
    question=question,
    student_answer="La photosynthèse est un processus biologique où les plantes utilisent la lumière du soleil pour produire du glucose à partir de CO2 et d'eau.",
    max_points=10
)

print(result)
```

---

## 📊 Étape 6 : Monitoring et Limites

### Limites de l'API Gratuite Hugging Face

- **Requêtes** : ~1000 requêtes/jour (gratuit)
- **Timeout** : 30 secondes par requête
- **Rate Limiting** : ~1 requête par seconde

### Fallback Automatique

Si l'API échoue, le système utilise **automatiquement** une correction basique :

```python
def _basic_essay_grading(self, answer, max_points):
    """
    Correction basique sans IA (fallback)
    """
    word_count = len(answer.split())
    
    if word_count < 20:
        score = max_points * 0.3
    elif word_count < 50:
        score = max_points * 0.5
    # ...
```

### Activer les Logs IA

Dans `settings.py` :

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'ai_debug.log',
        },
    },
    'loggers': {
        'ai_services': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 🎯 Étape 7 : Optimisations

### Cache des Résultats IA

Pour éviter de ré-interroger l'API pour les mêmes questions :

```python
from django.core.cache import cache

def grade_essay_cached(self, question, answer, max_points):
    cache_key = f"ai_grade_{question.id}_{hash(answer)}"
    
    # Vérifier le cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Appeler l'IA
    result = self.grade_essay(question, answer, max_points)
    
    # Sauvegarder dans le cache (1 heure)
    cache.set(cache_key, result, 3600)
    
    return result
```

### Traitement Asynchrone (Avancé)

Pour ne pas bloquer l'utilisateur :

```bash
pip install celery redis
```

```python
# tasks.py
from celery import shared_task

@shared_task
def generate_ai_feedback_async(result_id):
    result = Result.objects.get(id=result_id)
    # Générer le feedback...
```

---

## 📝 Étape 8 : Exemples Pratiques

### Exemple 1 : Corriger une Dissertation

```python
# Dans la console Django
from evaluation.models import *
from ai_modules.ai_services import EssayGrader

submission = Submission.objects.get(id=1)
question = Question.objects.get(id=5)  # Question de type essay

grader = EssayGrader()
result = grader.grade_essay(
    question=question,
    student_answer=submission.answers[str(question.id)]['answer'],
    max_points=question.points
)

print(f"Note: {result['points_earned']}/{question.points}")
print(f"Feedback: {result['feedback']}")
```

### Exemple 2 : Générer des Recommandations

```python
from evaluation.models import UserProfile, Result
from ai_modules.ai_services import WeaknessAnalyzer

profile = UserProfile.objects.get(user__username='alice')
recent_results = Result.objects.filter(student=profile.user)[:5]

analyzer = WeaknessAnalyzer()
analysis = analyzer.identify_weaknesses(profile, recent_results)

print("Points faibles détectés:")
for weakness in analysis['weaknesses']:
    print(f"- {weakness['skill']}: {weakness['average_score']}%")

print("\nRecommandations:")
for rec in analysis['recommendations']:
    print(f"- [{rec['priority']}] {rec['suggestion']}")
```

---

## 🔐 Sécurité

### Ne JAMAIS Commiter le Token

Ajoutez au `.gitignore` :

```
.env
*.env
```

### Rotation des Tokens

Changez votre token API tous les 3-6 mois sur Hugging Face.

---

## 🆘 Dépannage

### Erreur : "Unauthorized" ou 401

➡️ Vérifiez que votre token est correct dans `settings.py` ou `.env`

### Erreur : "Model is loading"

➡️ L'API Hugging Face charge le modèle. Attendez 20-30 secondes et réessayez.

### Erreur : "Rate limit exceeded"

➡️ Vous avez dépassé les limites gratuites. Attendez ou passez au plan payant.

### Pas de Réponse IA

➡️ Le système utilise automatiquement le fallback. Vérifiez les logs.

---

## 📚 Ressources

- **Hugging Face Docs** : https://huggingface.co/docs/api-inference
- **Modèles Gratuits** : https://huggingface.co/models
- **Limites API** : https://huggingface.co/pricing

---

## ✅ Checklist Finale

- [ ] Créer un compte Hugging Face
- [ ] Générer un token API
- [ ] Ajouter le token dans `.env` ou `settings.py`
- [ ] Installer `requests` : `pip install requests`
- [ ] Tester l'API dans le shell Django
- [ ] Vérifier les logs en cas d'erreur
- [ ] Activer le fallback automatique

---

**🎉 Félicitations ! Votre IA est maintenant intégrée et fonctionnelle !**

*Date de création : 5 octobre 2025*
