# 🎓 EduIA - Système d'Évaluation Intelligent avec IA

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-4.2.16-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-brightgreen)
![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38B2AC)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Plateforme d'évaluation et de suivi pédagogique propulsée par l'Intelligence Artificielle

---

## 🚀 Démarrage Rapide (5 minutes)

```powershell
# 1. Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# 2. Créer les données de test automatiquement
python create_test_data.py

# 3. Vérifier que tout fonctionne
python verify_system.py

# 4. Lancer le serveur
python manage.py runserver
```

**Ouvrez** : http://127.0.0.1:8000/student/dashboard/  
**Connectez-vous** : `etudiant1` / `pass123`

✅ **C'est tout ! Le système est opérationnel.**

---

## ✨ Fonctionnalités Principales

### 📊 Analytics Avancées
- Statistiques détaillées (moyenne, médiane, tendances)
- Analyse temporelle de la progression
- Performance par matière
- Identification des forces et faiblesses

### 🏆 Gamification
- 14 types de badges
- Système de 10 niveaux (Débutant → Légende)
- Points XP et classements
- Notifications de progression

### 🤖 Intelligence Artificielle
- Génération automatique de questions
- Feedback personnalisé
- Recommandations d'apprentissage
- Analyse des faiblesses

### 🎨 Interface Moderne
- Design Tailwind CSS responsive
- Graphiques Chart.js interactifs
- Animations fluides
- Mobile, tablet, desktop

---

## 📋 Documentation Complète

- **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** - Installation et premier test (5 min)
- **[GUIDE_DE_TEST.md](GUIDE_DE_TEST.md)** - Tests complets et scénarios détaillés
- **[Architecture](#architecture)** - Structure du projet ci-dessous

---

## 🏗️ Architecture

```
evaluation_project/
├── evaluation/
│   ├── models.py          # UserProfile, Test, Result
│   ├── views.py           # Dashboards, tests
│   ├── analytics.py       # Système d'analytics
│   ├── gamification.py    # Badges, XP, niveaux
│   └── ai_services.py     # Services IA
├── templates/
│   ├── base.html          # Template Tailwind
│   └── evaluation/
│       ├── student/
│       │   ├── dashboard.html
│       │   └── progress.html
│       └── teacher/
├── create_test_data.py    # Script de test
├── verify_system.py       # Vérification système
└── requirements.txt
```

---

## 🛠️ Technologies

- **Backend** : Django 4.2.16, MongoDB (Djongo)
- **IA** : Transformers (Hugging Face), PyTorch
- **Frontend** : Tailwind CSS, Chart.js
- **Outils** : Git, PowerShell

---

## 📸 Aperçu

### Dashboard Étudiant
- 4 cards statistiques (Score, Tests, Niveau, Classement)
- Section badges avec icônes colorées
- Recommandations IA personnalisées
- Performances par matière (grid 3 colonnes)
- Classement général avec médailles

### Page de Progression
- 3 graphiques Chart.js interactifs
- Analyse détaillée par matière
- Analyse IA des faiblesses
- Historique complet

---

## 🧪 Tests

### Automatique
```powershell
python create_test_data.py   # Crée 3 étudiants + 3 tests
python verify_system.py      # Vérifie tout le système
```

### Manuel
Consultez [GUIDE_DE_TEST.md](GUIDE_DE_TEST.md) pour les tests détaillés.

---

## 🤝 Contribuer

Les contributions sont bienvenues ! Forkez le projet et ouvrez une Pull Request.

---

## 📄 License

MIT License - Utilisez librement pour votre école ou institution.

---

## 👤 Auteur

**Houssine** - [Houssine2001](https://github.com/Houssine2001)

---

**Fait avec ❤️ et 🤖**
