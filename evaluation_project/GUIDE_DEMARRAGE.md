# 🚀 Guide de Démarrage Rapide - EduIA avec MongoDB

## ⚡ Démarrage en 3 Étapes

### 📋 **Prérequis**
Assurez-vous que vous êtes dans le bon dossier :
```powershell
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
```

---

## 🎯 **Étape 1 : Démarrer MongoDB**

```powershell
# Démarrer MongoDB (TOUJOURS FAIRE EN PREMIER)
Start-Process mongod -ArgumentList "--dbpath", "C:\data\db" -WindowStyle Hidden

# Vérifier que MongoDB tourne
Get-Process -Name mongod
```

**✅ Résultat attendu :** Vous devriez voir un processus `mongod` actif

---

## 🐍 **Étape 2 : Activer l'Environnement Virtuel**

```powershell
..\venv\Scripts\Activate.ps1
```

**✅ Résultat attendu :** Vous devriez voir `(venv)` au début de votre ligne de commande

---

## 🌐 **Étape 3 : Lancer le Serveur Django**

```powershell
python manage.py runserver
```

**✅ Résultat attendu :** 
```
Starting development server at http://127.0.0.1:8000/
```

---

## 🔓 **Connexion**

Ouvrez votre navigateur : **http://127.0.0.1:8000/**

### 🔑 **Comptes de Test**

| Username | Password | Rôle | Score Moyen |
|----------|----------|------|-------------|
| **etudiant1** | pass123 | Étudiant | 86.7% ⭐⭐⭐ |
| **etudiant2** | pass123 | Étudiant | 63.3% ⭐⭐ |
| **etudiant3** | pass123 | Étudiant | 96.7% ⭐⭐⭐⭐ |
| **prof1** | pass123 | Professeur | - |

---

## 🛑 **Arrêt Propre**

### Arrêter le Serveur Django
Dans le terminal où le serveur tourne :
```
CTRL + C
```

### Arrêter MongoDB
```powershell
Stop-Process -Name mongod
```

---

## ⚠️ **Problèmes Courants**

### ❌ Erreur : "Cannot use MongoClient after close"
**Cause :** MongoDB n'est pas démarré  
**Solution :** Exécutez l'Étape 1 (démarrer MongoDB)

### ❌ Erreur : "No such file or directory: 'C:\\data\\db'"
**Cause :** Le dossier de données MongoDB n'existe pas  
**Solution :**
```powershell
New-Item -ItemType Directory -Path "C:\data\db" -Force
```

### ❌ Page de login ne s'affiche pas
**Cause :** Le serveur Django n'est pas lancé  
**Solution :** Exécutez l'Étape 3

### ❌ "404 Not Found" sur /accounts/login/
**Cause :** Modifications non rechargées  
**Solution :** Arrêtez et relancez le serveur (CTRL+C puis `python manage.py runserver`)

---

## 📊 **Données Disponibles**

Le système contient déjà des données de test :

### ✅ **Tests Créés**
1. **Algèbre Niveau 1** (Mathématiques) - 5 questions
2. **Forces et Mouvement** (Physique) - 5 questions
3. **Introduction Python** (Informatique) - 5 questions

### ✅ **Résultats Simulés**

**Étudiant 1** :
- Algèbre : 90% (15 min)
- Forces : 70% (25 min)
- Python : 100% (10 min)

**Étudiant 2** :
- Algèbre : 70% (20 min)
- Forces : 50% (30 min)
- Python : 70% (15 min)

**Étudiant 3** :
- Algèbre : 100% (12 min)
- Forces : 90% (20 min)
- Python : 100% (8 min)

---

## 🎨 **Fonctionnalités Disponibles**

### Pour les Étudiants :
- ✅ Dashboard avec statistiques personnalisées
- ✅ Graphiques de progression (Chart.js)
- ✅ Badges et système de gamification
- ✅ Recommandations IA
- ✅ Classement général
- ✅ Historique des résultats

### Pour les Professeurs :
- ✅ Création de tests
- ✅ Gestion des questions
- ✅ Statistiques des élèves
- ✅ Interface d'administration

---

## 📁 **Structure du Projet**

```
evaluation_project/
├── backend/          # Configuration Django
│   ├── settings.py   # MongoDB configuré ici
│   └── urls.py       # Routes de l'application
├── evaluation/       # Application principale
│   ├── models.py     # Modèles (UserProfile, Test, Question, etc.)
│   ├── views.py      # Vues (dashboard, progress, etc.)
│   ├── analytics.py  # Calculs statistiques
│   └── gamification.py  # Système de badges et niveaux
├── templates/        # Templates HTML
│   ├── base.html     # Template de base Tailwind CSS
│   ├── registration/
│   │   └── login.html  # Page de connexion
│   └── evaluation/
│       └── student/
│           ├── dashboard.html  # Dashboard étudiant
│           └── progress.html   # Page de progression
├── create_test_data.py  # Script de création de données
├── verify_system.py     # Script de vérification
└── clean_mongodb.py     # Script de nettoyage MongoDB
```

---

## 🔄 **Workflow Complet**

```powershell
# 1. Démarrer MongoDB
Start-Process mongod -ArgumentList "--dbpath", "C:\data\db" -WindowStyle Hidden

# 2. Activer venv
..\venv\Scripts\Activate.ps1

# 3. Lancer le serveur
python manage.py runserver

# 4. Ouvrir le navigateur
# http://127.0.0.1:8000/

# 5. Se connecter avec etudiant1 / pass123

# 6. Explorer le dashboard avec :
#    - 4 cards statistiques
#    - Badges obtenus
#    - Recommandations IA
#    - Graphiques de progression
#    - Classement général
```

---

## 📞 **Support**

Pour recréer les données de test :
```powershell
python clean_mongodb.py
python create_test_data.py
```

Pour vérifier le système :
```powershell
python verify_system.py
```

---

**🎉 Profitez de votre plateforme d'évaluation intelligente avec MongoDB ! 🚀**
