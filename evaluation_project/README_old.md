# 🎓 Évaluation & Suivi des Performances avec IA

> Système complet d'évaluation et de suivi des performances utilisant **Django 4.2.16**, **MongoDB** et **Intelligence Artificielle (Hugging Face)**

[![Django](https://img.shields.io/badge/Django-4.2.16-green.svg)](https://www.djangoproject.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-brightgreen.svg)](https://www.mongodb.com/)
[![AI](https://img.shields.io/badge/AI-Hugging%20Face-orange.svg)](https://huggingface.co/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## 🎯 Vue d'Ensemble

Système d'évaluation intelligent permettant aux enseignants de créer des tests et aux étudiants de les passer avec correction automatique et feedback personnalisé par IA.

### ✨ Fonctionnalités Principales

#### Pour les Enseignants 👨‍🏫
- ✅ Créer des tests avec 5 types de questions (QCM, Vrai/Faux, Courte, Dissertation, Code)
- ✅ Configurer durée, difficulté, tentatives multiples
- ✅ Activer l'IA pour correction automatique
- ✅ Consulter statistiques détaillées et taux de réussite
- ✅ Mélanger l'ordre des questions
- ✅ Afficher/masquer réponses correctes

#### Pour les Étudiants 👨‍🎓
- ✅ Voir tests disponibles avec détails complets
- ✅ Passer tests avec timer et auto-sauvegarde AJAX
- ✅ Recevoir feedback IA personnalisé
- ✅ Consulter progression et historique
- ✅ Voir points forts et faiblesses
- ✅ Recevoir recommandations adaptées

#### Intelligence Artificielle 🤖
- ✅ Correction automatique d'essais via Hugging Face
- ✅ Analyse de sentiment des réponses
- ✅ Génération de feedback personnalisé
- ✅ Détection des points faibles
- ✅ Recommandations d'apprentissage
- ✅ Fallback automatique si IA indisponible

---

## 🚀 Technologies Utilisées

### Backend
- **Django** : 4.2.16
- **Djongo** : 1.3.7 (ORM MongoDB)
- **PyMongo** : 4.15.2

### Base de Données
- **MongoDB** : NoSQL database
- **Collections** : 5 (UserProfile, Test, Question, Submission, Result)

### Intelligence Artificielle
- **Hugging Face API** : API d'inférence gratuite
- **Modèles utilisés** :
  - `mistralai/Mistral-7B-Instruct-v0.1` (génération de texte)
  - `cardiffnlp/twitter-roberta-base-sentiment-latest` (sentiment)
  - `facebook/bart-large-mnli` (classification zero-shot)

### Frontend
- **Bootstrap** : 5.3.0
- **Chart.js** : 3.9.1 (graphiques)
- **Font Awesome** : 6.4.0 (icônes)
- **jQuery** : 3.6.0 (AJAX)

---

## 📁 Structure du Projet

```
evaluation_project/
│
├── backend/                    # Configuration Django
│   ├── settings.py            # ✅ MongoDB + IA configurés
│   ├── urls.py                # ✅ URLs principales
│   ├── wsgi.py
│   └── asgi.py
│
├── evaluation/                 # Application principale
│   ├── models.py              # ✅ 5 modèles MongoDB (400+ lignes)
│   ├── views.py               # ✅ 15 vues (320+ lignes)
│   ├── urls.py                # ✅ 13 endpoints
│   ├── admin.py               # ✅ 5 interfaces admin (400+ lignes)
│   ├── services.py            # ✅ Logique métier (300+ lignes)
│   └── migrations/
│       └── 0001_initial.py    # ✅ Migration initiale
│
├── ai_modules/                 # Modules IA
│   └── ai_services.py         # ✅ 4 services IA (250+ lignes)
│
├── templates/                  # Templates HTML
│   ├── base.html              # ✅ Template Bootstrap 5
│   └── evaluation/
│       ├── teacher/           # ✅ 2 templates enseignant
│       └── student/           # ✅ 5 templates étudiant
│
├── static/                     # CSS, JS, Images
├── media/                      # Uploads utilisateurs
├── logs/                       # Logs système
│
├── docs/                       # Documentation (8 fichiers)
│   ├── AI_INTEGRATION_GUIDE.md
│   ├── MODELS_DOCUMENTATION.md
│   ├── QUICKSTART.md
│   └── ...
│
├── manage.py                   # Commandes Django
├── requirements.txt            # ✅ Dépendances (15 packages)
├── README.md                   # ✅ Ce fichier
└── DEMARRAGE_COMPLET.md       # ✅ Guide de démarrage
│
├── docs/                       # Documentation du projet
│
├── manage.py                   # Script de gestion Django
└── requirements.txt            # Dépendances Python
```

---

## ⚙️ Installation et Configuration

### 1. Prérequis

- Python 3.10 ou supérieur
- MongoDB installé et en cours d'exécution
- Git (optionnel)

### 2. Installation

```bash
# Cloner le projet (si sur Git)
git clone <votre-repo>
cd evaluation_project

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration MongoDB

Assurez-vous que MongoDB est installé et en cours d'exécution :

```bash
# Démarrer MongoDB (Windows)
net start MongoDB

# Démarrer MongoDB (Linux/Mac)
sudo systemctl start mongod
```

Par défaut, le projet est configuré pour se connecter à :
- **Host** : `localhost`
- **Port** : `27017`
- **Database** : `evaluation_db`

Pour modifier ces paramètres, éditez le fichier `backend/settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'evaluation_db',
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
        }
    }
}
```

### 4. Migrations et Démarrage

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# Démarrer le serveur de développement
python manage.py runserver
```

Le projet sera accessible à : `http://127.0.0.1:8000/`

---

## 🔧 Configuration Avancée

### Variables d'Environnement

Pour la production, créez un fichier `.env` à la racine du projet :

```env
SECRET_KEY=votre_clé_secrète
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_NAME=evaluation_db
```

### Fichiers Statiques

Pour collecter les fichiers statiques en production :

```bash
python manage.py collectstatic
```

---

## 👥 Collaboration

### Bonnes Pratiques

1. **Branches Git** :
   - `main` : branche principale (production)
   - `develop` : branche de développement
   - `feature/nom-feature` : nouvelles fonctionnalités

2. **Commits** :
   - Messages clairs et descriptifs
   - Un commit = une modification logique

3. **Pull Requests** :
   - Toujours faire une PR avant de merger sur `main`
   - Code review obligatoire

### Workflow de Développement

```bash
# 1. Créer une nouvelle branche
git checkout -b feature/ma-fonctionnalite

# 2. Développer et committer
git add .
git commit -m "Description de la modification"

# 3. Pousser la branche
git push origin feature/ma-fonctionnalite

# 4. Créer une Pull Request sur GitHub/GitLab
```

---

## 📝 Prochaines Étapes

- [ ] Définir les modèles de données
- [ ] Créer les vues et templates
- [ ] Intégrer les modules IA
- [ ] Créer l'API REST (si nécessaire)
- [ ] Ajouter les tests unitaires
- [ ] Configurer le déploiement

---

## 📧 Contact

Pour toute question ou suggestion, contactez l'équipe de développement.

---

## 📄 Licence

Ce projet est sous licence [Votre Licence].
