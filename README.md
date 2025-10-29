# 🎓 EducationIA Django - Plateforme d'Évaluation avec IA

**Plateforme d'évaluation éducative intelligente avec analyse IA et recommandations personnalisées**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com)

---

## 📋 Table des Matières

- [Fonctionnalités](#fonctionnalités)
- [Technologies](#technologies)
- [Architecture](#architecture)
- [Installation Locale](#installation-locale)
- [Déploiement Render](#déploiement-render)
- [Documentation](#documentation)
- [Licence](#licence)

---

## ✨ Fonctionnalités

### Pour les Étudiants
- ✅ Passage de tests interactifs (QCM, Vrai/Faux, Questions ouvertes)
- 🤖 Analyse automatique par IA après chaque test
- 📊 Dashboard personnel avec statistiques détaillées
- 🎯 Recommandations personnalisées basées sur les performances
- 🏆 Système de gamification (badges, niveaux, classements)
- 📈 Suivi de progression par matière et compétence
- 💡 Identification des points forts et lacunes spécifiques

### Pour les Professeurs
- 📝 Création de tests personnalisés
- 📊 Dashboard avec analytics globales
- 👥 Suivi individuel des étudiants
- 📈 Statistiques de classe et par test
- 🎯 Génération automatique de questions avec IA
- 📄 Gestion de ressources pédagogiques (PDF, DOCX, vidéos)

### Intelligence Artificielle
- 🧠 **Analyse conceptuelle** : Détection précise des compétences maîtrisées
- 🎯 **Feedback personnalisé** : Recommandations spécifiques par étudiant
- 📊 **Prédiction de performance** : Prévision du niveau futur
- 🔍 **Détection de patterns** : Identification des erreurs récurrentes
- 💬 **Analyse en langage naturel** via Hugging Face Mistral-7B

---

## 🛠️ Technologies

### Backend
- **Django 4.2** - Framework web Python
- **Gunicorn** - Serveur WSGI production
- **WhiteNoise** - Service des fichiers statiques

### Base de Données
- **MongoDB Atlas** - Base de données cloud NoSQL
- **Djongo** - ORM MongoDB pour Django

### Intelligence Artificielle
- **Hugging Face API** - Modèles IA (Mistral-7B-Instruct)
- **Pattern Matching** - Détection de compétences techniques (70+ patterns)
- **Algorithmes statistiques** - Prédictions et analyses

### Frontend
- **Django Templates** - Templating engine
- **Bootstrap 5** - Framework CSS responsive
- **JavaScript** - Interactivité client

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          Interface Utilisateur (Templates)           │
│  - Dashboard Étudiant/Professeur                    │
│  - Passage de tests                                  │
│  - Affichage résultats et analyses                  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Views Django (Controllers)                 │
│  - Gestion requêtes HTTP                            │
│  - Validation des données                           │
│  - Orchestration des services                       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         Services Métier (Business Logic)             │
│  ├─ ai_concept_analyzer.py (Hugging Face)          │
│  ├─ ai_analysis_enhanced.py (Pattern Matching)     │
│  ├─ ai_feedback.py (Feedback personnalisé)         │
│  ├─ ai_prediction.py (Prédiction performance)      │
│  ├─ analytics.py (Statistiques)                    │
│  └─ gamification.py (Badges, XP, Niveaux)          │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│     Modèles Django (5 Modèles Principaux)          │
│  ├─ UserProfile (Profils étudiants)                │
│  ├─ Test (Évaluations)                             │
│  ├─ Question (Questions avec metadata IA)          │
│  ├─ Submission (Réponses étudiants)                │
│  └─ Result (Résultats avec analyse IA)             │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│     Base de Données (MongoDB Atlas Cloud)           │
└─────────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         APIs Externes (IA)                           │
│  └─ Hugging Face Inference API (Mistral-7B)        │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Installation Locale

### Prérequis
- Python 3.11+
- Git
- Compte MongoDB Atlas (gratuit)

### Étapes

1. **Cloner le projet**
```bash
git clone https://github.com/votre-username/EducationIA_Django.git
cd EducationIA_Django
```

2. **Créer environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
cd evaluation_project
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine :
```env
DJANGO_SECRET_KEY=votre-cle-secrete
DEBUG=1
USE_MONGO=1
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster
MONGO_DB_NAME=django_education
```

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer un superuser**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur**
```bash
python manage.py runserver
```

Ouvrir http://localhost:8000

---

## 🚀 Déploiement Render

### Option 1 : Démarrage Rapide (10 minutes)

Suivre le guide : **[RENDER_QUICK_START.md](RENDER_QUICK_START.md)**

### Option 2 : Guide Complet

Suivre le guide détaillé : **[README_RENDER.md](README_RENDER.md)**

### Résumé des Étapes

1. **Pousser sur GitHub**
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

2. **Créer Web Service sur Render**
- Build Command : `bash build.sh`
- Start Command : `cd evaluation_project && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`

3. **Configurer les variables d'environnement**
```env
PYTHON_VERSION=3.11.0
DJANGO_SECRET_KEY=<générer-nouvelle-clé>
DEBUG=0
USE_MONGO=1
MONGO_URI=mongodb+srv://...
MONGO_DB_NAME=django_education
```

4. **Attendre le build** (5-10 min)

5. **Accéder à l'application**
```
https://votre-app.onrender.com
```

---

## 📚 Documentation

### Guides de Déploiement
- **[RENDER_QUICK_START.md](RENDER_QUICK_START.md)** - Démarrage rapide (10 min)
- **[README_RENDER.md](README_RENDER.md)** - Guide complet de déploiement
- **[RENDER_CHECKLIST.md](RENDER_CHECKLIST.md)** - Checklist de vérification

### Documentation Technique
- **[evaluation/houssine.md](evaluation_project/evaluation/houssine.md)** - Architecture complète du module evaluation
- **[evaluation/README.md](evaluation_project/evaluation/README.md)** - Documentation des modèles

### Configuration
- **[.env.example](.env.example)** - Template des variables d'environnement
- **[requirements.txt](evaluation_project/requirements.txt)** - Dépendances Python optimisées

---

## 🔧 Structure du Projet

```
EducationIA_Django/
├── evaluation_project/          # 🎯 Projet Django principal
│   ├── backend/                 # Configuration Django
│   │   ├── settings.py         # ⚙️ Settings (Render-ready)
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── evaluation/              # 📚 App principale
│   │   ├── models.py           # 5 modèles core
│   │   ├── views.py            # Vues étudiants/profs
│   │   ├── services.py         # Business logic
│   │   ├── ai_concept_analyzer.py  # 🤖 IA Hugging Face
│   │   ├── ai_analysis_enhanced.py # 🔍 Pattern matching
│   │   ├── ai_feedback.py          # 💬 Feedback personnalisé
│   │   ├── ai_prediction.py        # 📈 Prédictions
│   │   ├── analytics.py            # 📊 Analytics
│   │   └── gamification.py         # 🏆 Badges & XP
│   ├── exercise_generator/      # 🎲 Générateur d'exercices
│   ├── analytics_dashboard/     # 📊 Dashboard analytics
│   ├── resources/               # 📄 Gestion ressources
│   ├── static/                  # CSS, JS, images
│   ├── templates/               # Templates HTML
│   ├── manage.py
│   └── requirements.txt        # 📦 Dépendances optimisées
├── build.sh                     # 🔨 Script build Render
├── runtime.txt                  # 🐍 Python 3.11.0
├── .env.example                 # Template env vars
├── .gitignore
├── README.md                    # Ce fichier
├── README_RENDER.md             # Guide déploiement complet
├── RENDER_QUICK_START.md        # Démarrage rapide
└── RENDER_CHECKLIST.md          # Checklist
```

---

## 🎯 Fonctionnement de l'IA

### 1. Analyse Conceptuelle (Hugging Face)

Utilise **Mistral-7B-Instruct-v0.2** via l'API Hugging Face :

```python
# ai_concept_analyzer.py
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

response = requests.post(API_URL, headers=headers, json={
    "inputs": "Analyser les performances de l'étudiant...",
    "parameters": {
        "max_new_tokens": 800,
        "temperature": 0.7
    }
})
```

**Résultat** : Points forts, lacunes, recommandations précises

### 2. Détection de Compétences (Pattern Matching)

70+ patterns techniques définis :

```python
# ai_analysis_enhanced.py
SKILL_PATTERNS = {
    'react': {
        'hooks': [r'useState', r'useEffect', r'useContext', ...],
        'components': [r'component', r'props', r'lifecycle', ...],
        ...
    },
    'python': {...},
    'sql': {...},
}
```

**Résultat** : "Excellente maîtrise des Hooks React (92%)"

### 3. Prédiction de Performance

Algorithme de prédiction basé sur 5 facteurs pondérés :

```python
# ai_prediction.py
WEIGHTS = {
    'average_score': 0.35,      # 35%
    'trend': 0.25,              # 25% (pente régression linéaire)
    'consistency': 0.15,        # 15%
    'improvement_rate': 0.15,   # 15%
    'activity_level': 0.10      # 10%
}
```

**Résultat** : Prédiction niveau futur avec confiance

---

## 🔐 Sécurité

### En Production
```python
DEBUG = False
ALLOWED_HOSTS = ['.onrender.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

### Variables Sensibles
- ✅ `SECRET_KEY` depuis variable d'environnement
- ✅ `MONGO_URI` depuis variable d'environnement
- ✅ Fichier `.env` dans `.gitignore`

---

## 📊 Monitoring

### Logs Render
```bash
Render Dashboard → Logs → Live Tail
```

### Métriques
- CPU Usage
- Memory Usage
- Request Count
- Response Time

---

## 🐛 Debugging

### Logs Django
```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Opération réussie")
logger.error("❌ Erreur rencontrée")
```

### Shell Render
```bash
Render Dashboard → Shell
cd evaluation_project
python manage.py shell
```

---

## 🔄 Mises à Jour

### Déploiement Automatique
```bash
git add .
git commit -m "Nouvelles fonctionnalités"
git push origin main
```

Render redéploie automatiquement !

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/NouvelleFonctionnalite`)
3. Commit les changements (`git commit -m 'Ajout NouvelleFonctionnalite'`)
4. Push sur la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrir une Pull Request

---

## 📞 Support

- **Documentation** : Voir les fichiers README_*.md
- **Issues** : GitHub Issues
- **Email** : votre-email@example.com

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **Django** - Framework web
- **MongoDB Atlas** - Base de données cloud
- **Hugging Face** - API d'intelligence artificielle
- **Render** - Plateforme de déploiement
- **Bootstrap** - Framework CSS

---

## 📈 Statistiques du Projet

- **5 modèles Django** interconnectés
- **7 modules IA** avec Hugging Face
- **70+ patterns** de détection de compétences
- **15+ badges** de gamification
- **3 dashboards** (étudiant, professeur, analytics)

---

**Fait avec ❤️ pour l'éducation**

---

*Dernière mise à jour : 29 octobre 2025*
