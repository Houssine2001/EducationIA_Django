# 📦 GUIDE D'INSTALLATION POUR VOTRE AMI

## 🎯 Prérequis

Avant de commencer, votre ami doit avoir installé :

1. **Python 3.8+** : https://www.python.org/downloads/
2. **MongoDB** : https://www.mongodb.com/try/download/community
3. **Git** (optionnel mais recommandé) : https://git-scm.com/downloads

---

## 📥 Étape 1 : Récupérer le Projet

### Option A : Avec Git (recommandé)
```bash
git clone https://github.com/Houssine2001/EducationIA_Django.git
cd EducationIA_Django/evaluation_project
```

### Option B : Sans Git
1. Télécharger le ZIP du projet
2. Extraire le contenu
3. Ouvrir un terminal dans le dossier `evaluation_project`

---

## 🐍 Étape 2 : Créer un Environnement Virtuel

### Sur Windows (PowerShell) :
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Sur Windows (CMD) :
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Sur macOS/Linux :
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Note** : Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.

---

## 📦 Étape 3 : Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Packages principaux installés** :
- Django 4.2.16
- djongo 1.3.6 (connecteur MongoDB)
- pymongo 3.12.3
- python-dotenv
- openai (pour l'IA)
- et autres...

---

## ⚙️ Étape 4 : Configuration

### 4.1 Créer le fichier `.env`

Copier le fichier d'exemple :
```bash
# Windows PowerShell
Copy-Item .env.example .env

# Windows CMD
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 4.2 Modifier le fichier `.env`

Ouvrir `.env` et modifier les valeurs :

```env
# Django Settings
SECRET_KEY=votre-cle-secrete-aleatoire-tres-longue-123456789
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_NAME=evaluation_db

# Si MongoDB nécessite une authentification (décommentez si nécessaire)
# MONGODB_USERNAME=votre_username
# MONGODB_PASSWORD=votre_password
# MONGODB_AUTH_SOURCE=admin
```

> **Astuce** : Pour générer une SECRET_KEY aléatoire :
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🗄️ Étape 5 : Démarrer MongoDB

### Sur Windows :
```powershell
# Méthode 1 : Si MongoDB est installé comme service
net start MongoDB

# Méthode 2 : Démarrer manuellement
mongod --dbpath "C:\data\db"
```

### Sur macOS :
```bash
# Avec Homebrew
brew services start mongodb-community

# Ou manuellement
mongod --config /usr/local/etc/mongod.conf
```

### Sur Linux :
```bash
sudo systemctl start mongod
sudo systemctl enable mongod  # Pour démarrage automatique
```

**Vérifier que MongoDB fonctionne** :
```bash
mongosh
# Vous devriez voir un prompt MongoDB
# Tapez 'exit' pour quitter
```

---

## 🔄 Étape 6 : Migrations Django

```bash
# Appliquer les migrations existantes
python manage.py migrate

# Si erreur, essayer de faker les migrations
python manage.py migrate --fake
```

---

## 👤 Étape 7 : Créer un Superutilisateur

```bash
python manage.py createsuperuser
```

Suivre les instructions :
- **Nom d'utilisateur** : admin (ou votre choix)
- **Email** : votre.email@example.com
- **Mot de passe** : choisir un mot de passe sécurisé

---

## 📊 Étape 8 : Générer des Données de Test (Optionnel)

Pour avoir des données de démonstration :

```bash
# Créer des utilisateurs de test
python create_student.py

# Générer des tests de formation
python generate_training_tests.py

# Créer des profils étudiants avec badges
python create_student_profiles.py
```

---

## 🚀 Étape 9 : Lancer le Serveur

```bash
python manage.py runserver
```

Vous devriez voir :
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🌐 Étape 10 : Accéder à l'Application

Ouvrir votre navigateur et aller à :

- **Page d'accueil** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **Dashboard étudiant** : http://127.0.0.1:8000/student/dashboard/
- **Dashboard professeur** : http://127.0.0.1:8000/teacher/dashboard/

### Identifiants par défaut (si données de test créées) :

**Professeur** :
- Username : `prof1`
- Password : `password123`

**Étudiants** :
- Username : `etudiant1` / Password : `password123`
- Username : `etudiant2` / Password : `password123`
- Username : `etudiant3` / Password : `password123`

---

## 🔧 Commandes Utiles

### Gestion du Serveur
```bash
# Démarrer le serveur
python manage.py runserver

# Démarrer sur un port différent
python manage.py runserver 8080

# Démarrer accessible depuis le réseau local
python manage.py runserver 0.0.0.0:8000
```

### Gestion de la Base de Données
```bash
# Shell Django
python manage.py shell

# Shell MongoDB
mongosh
use evaluation_db
db.auth_user.find().pretty()
```

### Gestion des Utilisateurs
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Changer le mot de passe d'un utilisateur
python manage.py changepassword nom_utilisateur
```

### Nettoyage
```bash
# Vider les sessions
python clear_sessions.py

# Nettoyer MongoDB
python clean_mongodb.py
```

---

## ❗ Résolution des Problèmes Courants

### 1. Erreur : "No module named 'djongo'"
```bash
pip install djongo==1.3.6 pymongo==3.12.3 sqlparse==0.2.4
```

### 2. Erreur : "MongoDB connection refused"
- Vérifier que MongoDB est démarré : `mongosh`
- Vérifier le port dans `.env` (par défaut 27017)

### 3. Erreur : "CSRF verification failed"
- Vider le cache du navigateur
- Vérifier que `localhost` est dans `ALLOWED_HOSTS`

### 4. Erreur : "No such table: ..."
```bash
python manage.py migrate --run-syncdb
```

### 5. Erreur : "Permission denied" lors de l'activation venv (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 6. MongoDB ne démarre pas
- Créer le dossier de données : `mkdir C:\data\db`
- Vérifier les permissions du dossier

### 7. Le serveur démarre mais erreur 500
- Vérifier les logs dans le terminal
- Vérifier la configuration dans `backend/settings.py`
- S'assurer que MongoDB est accessible

---

## 📚 Structure du Projet

```
evaluation_project/
├── backend/                    # Configuration Django
│   ├── settings.py            # ⚙️ Configuration principale
│   ├── urls.py                # 🔗 Routes URL
│   └── wsgi.py
├── evaluation/                # App principale
│   ├── models.py              # 📊 Modèles de données
│   ├── views.py               # 🎯 Vues/Contrôleurs
│   ├── urls.py
│   └── ai_concept_analyzer.py # 🤖 Analyse IA
├── exercise_generator/        # Générateur d'exercices IA
│   ├── models.py
│   ├── views.py
│   └── ai_generator.py
├── templates/                 # 🎨 Templates HTML
│   └── evaluation/
│       ├── student/
│       └── teacher/
├── static/                    # 📦 Fichiers statiques (CSS, JS)
├── manage.py                  # 🔧 Commandes Django
├── requirements.txt           # 📋 Dépendances Python
├── .env.example              # ⚙️ Exemple configuration
└── README.md
```

---

## 🔐 Sécurité - IMPORTANT

### Avant de partager le projet :

1. **NE JAMAIS partager le fichier `.env`** - Il contient des secrets !
2. **Vérifier que `.gitignore` inclut** :
   ```
   .env
   *.pyc
   __pycache__/
   db.sqlite3
   venv/
   ```
3. **Générer une nouvelle SECRET_KEY** pour chaque installation
4. **En production** :
   - Mettre `DEBUG=False`
   - Configurer correctement `ALLOWED_HOSTS`
   - Utiliser HTTPS
   - Configurer une vraie base de données MongoDB distante

---

## 📞 Support

En cas de problème :

1. **Vérifier les logs** dans le terminal
2. **Consulter la documentation** :
   - Django : https://docs.djangoproject.com/
   - MongoDB : https://www.mongodb.com/docs/
   - Djongo : https://github.com/doableware/djongo
3. **Rechercher l'erreur** sur Google/Stack Overflow
4. **Contacter le développeur** (vous !)

---

## 🎓 Fonctionnalités Principales

### Pour les Étudiants
- ✅ Passer des tests de formation
- 📊 Voir la progression détaillée
- 🎯 Points forts et lacunes identifiés par IA
- 🏆 Système de badges et gamification
- 📈 Graphiques de performance

### Pour les Professeurs
- 📝 Créer et gérer des tests
- 🤖 Générer des exercices avec l'IA
- 👥 Suivre les performances des étudiants
- 📊 Analyses et statistiques détaillées
- 📄 Uploader des documents de cours

---

## 🚀 Prochaines Étapes

Une fois l'installation réussie :

1. **Explorer l'interface** avec les comptes de test
2. **Créer du contenu** (tests, exercices)
3. **Personnaliser** les templates et le design
4. **Tester les fonctionnalités** IA
5. **Déployer en production** (optionnel)

---

## ✅ Checklist d'Installation

- [ ] Python installé
- [ ] MongoDB installé et démarré
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`requirements.txt`)
- [ ] Fichier `.env` configuré
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Serveur démarre sans erreur
- [ ] Accès à http://127.0.0.1:8000/
- [ ] Connexion admin fonctionne

---

## 🎉 Félicitations !

Si toutes les étapes sont complétées, le projet est prêt à l'emploi !

**Bon développement ! 🚀**
