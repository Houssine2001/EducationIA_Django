# 🔄 Guide de Migration SQLite → MongoDB

## 📋 Vue d'ensemble

Ce guide vous accompagne dans la migration complète de SQLite vers MongoDB pour le projet DjangoEducation.

### ⚠️ Avertissement
- **Sauvegardez vos données** avant toute manipulation
- La migration prendra environ 30-60 minutes
- MongoDB nécessite un serveur local ou distant
- **Djongo 1.3.6** nécessite Django **< 4.2** (nous utiliserons Django 4.1.13)

### 📂 Fichiers créés pour la migration

```
evaluation_project/
├── migrate_to_mongodb.py          # Script de migration automatique
├── setup_mongodb.ps1               # Installation automatique Windows
├── requirements_mongodb.txt        # Dépendances MongoDB
├── .env.mongodb                    # Configuration MongoDB
├── backend/
│   └── settings_mongodb.py         # Settings Django pour MongoDB
└── MIGRATION_MONGODB_GUIDE.md      # Ce fichier
```

---

## 🎯 Étapes de Migration

### Étape 1 : Installation de MongoDB
### Étape 2 : Installation des dépendances Python
### Étape 3 : Migration des données
### Étape 4 : Configuration Django
### Étape 5 : Tests et validation

---

## 📦 Étape 1 : Installation de MongoDB

### Windows

**1.1 Télécharger MongoDB Community Edition**

Allez sur : https://www.mongodb.com/try/download/community

- Choisissez la version Windows
- Format : MSI
- Version : 7.0 ou supérieure

**1.2 Installer MongoDB**

```bash
# Exécuter le fichier téléchargé
# Choisir "Complete Installation"
# Cocher "Install MongoDB as a Service"
# Cocher "Install MongoDB Compass" (interface graphique)
```

**1.3 Vérifier l'installation**

```powershell
# Ouvrir PowerShell en administrateur
mongod --version

# Résultat attendu:
# db version v7.0.x
# Build Info: ...
```

**1.4 Démarrer MongoDB**

```powershell
# MongoDB démarre automatiquement comme service Windows
# Pour vérifier :
net start MongoDB

# Pour arrêter :
net stop MongoDB

# Pour redémarrer :
net stop MongoDB
net start MongoDB
```

**1.5 Tester la connexion**

```powershell
# Ouvrir le shell MongoDB
mongosh

# Vous devriez voir :
# Current Mongosh Log ID: ...
# Connecting to: mongodb://127.0.0.1:27017/
# test>

# Lister les bases de données
show dbs

# Quitter
exit
```

### MongoDB Compass (Interface Graphique)

Si vous avez installé MongoDB Compass :

1. Ouvrir MongoDB Compass
2. Connexion : `mongodb://localhost:27017`
3. Cliquer sur "Connect"
4. Vous verrez vos bases de données

---

## 🐍 Étape 2 : Installation des Dépendances Python

### Méthode Automatique (Recommandée)

```powershell
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project

# Exécuter le script d'installation
.\setup_mongodb.ps1
```

### Méthode Manuelle

```powershell
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances MongoDB
pip install -r requirements_mongodb.txt
```

**Packages installés :**
- `djongo==1.3.6` - Connecteur Django-MongoDB
- `pymongo==3.12.3` - Driver MongoDB Python
- `dnspython==2.3.0` - Pour MongoDB Atlas (cloud)
- `python-decouple==3.8` - Variables d'environnement

### Vérifier l'installation

```python
python -c "import djongo; print('Djongo version:', djongo.__version__)"
python -c "import pymongo; print('PyMongo version:', pymongo.__version__)"
```

---

## 🔄 Étape 3 : Migration des Données

### 3.1 Sauvegarde SQLite (Sécurité)

```powershell
# Copier la base SQLite
copy db.sqlite3 db.sqlite3.backup

# Créer le dossier de backup
mkdir backup_sqlite -ErrorAction SilentlyContinue
```

### 3.2 Exécuter le script de migration

```powershell
python migrate_to_mongodb.py
```

**Ce script va :**
1. ✅ Sauvegarder toutes les données SQLite en JSON
2. ✅ Se connecter à MongoDB (localhost:27017)
3. ✅ Créer la base `django_education`
4. ✅ Migrer toutes les tables :
   - Users (auth_user)
   - UserProfiles (evaluation_userprofile)
   - Tests (evaluation_test)
   - Questions (evaluation_question)
   - Submissions (evaluation_submission)
   - Results (evaluation_result)
5. ✅ Créer les index pour optimiser les performances
6. ✅ Vérifier que tous les comptages correspondent

**Sortie attendue :**

```
============================================================
🔄 MIGRATION SQLite → MongoDB
============================================================

📦 Sauvegarde des données SQLite...
  ✓ users: 5 enregistrements sauvegardés
  ✓ profiles: 5 enregistrements sauvegardés
  ✓ tests: 50 enregistrements sauvegardés
  ✓ questions: 453 enregistrements sauvegardés
  ✓ submissions: 122 enregistrements sauvegardés
  ✓ results: 122 enregistrements sauvegardés

✅ Sauvegarde terminée dans ./backup_sqlite/

👥 Migration des utilisateurs...
  ✓ 5 utilisateurs migrés

📋 Migration des profils...
  ✓ 5 profils migrés

📝 Migration des tests...
  ✓ 50 tests migrés

❓ Migration des questions...
  ✓ 453 questions migrées

📤 Migration des soumissions...
  ✓ 122 soumissions migrées

📊 Migration des résultats...
  ✓ 122 résultats migrés

🔍 Création des index MongoDB...
  ✓ Index créés avec succès

✅ Vérification de la migration...
  ✓ Users: SQLite=5, MongoDB=5
  ✓ Profiles: SQLite=5, MongoDB=5
  ✓ Tests: SQLite=50, MongoDB=50
  ✓ Questions: SQLite=453, MongoDB=453
  ✓ Submissions: SQLite=122, MongoDB=122
  ✓ Results: SQLite=122, MongoDB=122

🎉 Migration réussie ! Tous les comptages correspondent.

============================================================
✅ MIGRATION TERMINÉE AVEC SUCCÈS !
============================================================

📝 Prochaines étapes :
1. Modifier backend/settings.py pour utiliser MongoDB
2. Redémarrer le serveur Django
3. Tester l'application
4. Si tout fonctionne, vous pouvez supprimer backup_sqlite/
```

### 3.3 Vérifier dans MongoDB Compass

1. Ouvrir MongoDB Compass
2. Base de données : `django_education`
3. Vérifier les collections :
   - `auth_user`
   - `evaluation_userprofile`
   - `evaluation_test`
   - `evaluation_question`
   - `evaluation_submission`
   - `evaluation_result`

---

## ⚙️ Étape 4 : Configuration Django

### 4.1 Remplacer settings.py

**Option 1 : Renommer les fichiers**

```powershell
# Sauvegarder l'ancien settings
move backend\settings.py backend\settings_sqlite.py.backup

# Utiliser le nouveau settings MongoDB
copy backend\settings_mongodb.py backend\settings.py
```

**Option 2 : Modifier manuellement backend/settings.py**

Remplacez la section DATABASES par :

```python
# =============================================================================
# CONFIGURATION MONGODB AVEC DJONGO
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'django_education',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
        },
    }
}
```

### 4.2 Configurer les variables d'environnement (Optionnel)

Créer un fichier `.env` :

```bash
copy .env.mongodb .env
```

Contenu de `.env` :

```env
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB_NAME=django_education
MONGO_USERNAME=
MONGO_PASSWORD=

SECRET_KEY=votre-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## ✅ Étape 5 : Tests et Validation

### 5.1 Redémarrer le serveur

```powershell
python manage.py runserver
```

**Si vous voyez :**
```
System check identified no issues (0 silenced).
October 09, 2025 - 14:30:00
Django version 4.1.13, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
```

✅ **Succès !** Django utilise maintenant MongoDB.

### 5.2 Tester la connexion

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test

# Compter les utilisateurs
print("Users:", User.objects.count())

# Compter les profils
print("Profiles:", UserProfile.objects.count())

# Compter les tests
print("Tests:", Test.objects.count())

# Récupérer un utilisateur
user = User.objects.first()
print("User:", user.username)

# Récupérer son profil
profile = user.profile
print("Profile XP:", profile.total_xp)
```

**Sortie attendue :**
```
Users: 5
Profiles: 5
Tests: 50
User: etudiant1
Profile XP: 1250
```

### 5.3 Tester l'interface web

1. Aller sur http://127.0.0.1:8000/
2. Se connecter avec `etudiant1` / `password123`
3. Vérifier :
   - ✅ Dashboard s'affiche
   - ✅ Tests disponibles
   - ✅ Badges visibles
   - ✅ Points forts et lacunes affichés
   - ✅ Possibilité de passer un test

### 5.4 Tester un nouveau test

1. Passer un test complet
2. Soumettre les réponses
3. Vérifier que le résultat s'affiche
4. Vérifier dans MongoDB Compass que la soumission est enregistrée

---

## 🔧 Dépannage

### Erreur : "No module named 'djongo'"

```powershell
pip uninstall djongo
pip install djongo==1.3.6
```

### Erreur : "Cannot connect to MongoDB"

```powershell
# Vérifier que MongoDB est démarré
net start MongoDB

# Tester manuellement
mongosh mongodb://localhost:27017

# Vérifier le port
netstat -ano | findstr :27017
```

### Erreur : "Authentication failed"

Si vous avez configuré un username/password MongoDB :

```python
# Dans settings.py, ajoutez:
'CLIENT': {
    'host': 'localhost',
    'port': 27017,
    'username': 'votre_username',
    'password': 'votre_password',
    'authSource': 'admin',
    'authMechanism': 'SCRAM-SHA-1',
}
```

### Erreur : "Unsupported Feature"

Certaines fonctionnalités Django ne sont pas supportées par Djongo :

**Non supporté :**
- `select_related()` avec plusieurs niveaux
- `prefetch_related()` complexe
- Certains types d'annotations

**Solution :** Utiliser des requêtes simples ou MongoDB natif via PyMongo.

### Django Admin ne fonctionne pas

Djongo peut avoir des problèmes avec Django Admin. Solutions :

```powershell
# Option 1: Recréer les tables admin
python manage.py migrate --run-syncdb

# Option 2: Utiliser MongoDB Compass pour l'administration
```

---

## 📊 Comparaison SQLite vs MongoDB

| Critère | SQLite | MongoDB |
|---------|---------|---------|
| **Type** | SQL (relationnel) | NoSQL (documents) |
| **Performance** | Bonne (<100k lignes) | Excellente (millions) |
| **Scalabilité** | Limitée | Très bonne |
| **Flexibilité schema** | Rigide | Flexible |
| **Requêtes complexes** | Excellentes (JOIN) | Bonnes ($lookup) |
| **Installation** | Aucune (fichier) | Serveur requis |
| **Backup** | Copier fichier | Export/Import |
| **Production** | Non recommandé | Recommandé |

---

## 🎯 Avantages de MongoDB

### ✅ Pour ce projet

1. **Schema flexible** : Facile d'ajouter de nouveaux champs
2. **Performance** : Plus rapide avec beaucoup de données
3. **JSON natif** : Parfait pour `ai_analysis`, `badges`, `strengths`
4. **Scalabilité** : Peut gérer des millions d'étudiants
5. **Embedded documents** : Évite les JOIN complexes

### 📊 Exemples concrets

**Avant (SQLite avec JOIN) :**
```python
# 3 requêtes SQL
user = User.objects.get(id=1)
profile = user.profile
results = Result.objects.filter(student=user).select_related('test')
```

**Après (MongoDB avec embedding) :**
```python
# 1 requête MongoDB
user = User.objects.get(id=1)
# Profile déjà inclus
# Results avec tests déjà inclus
```

---

## 🚀 Optimisations MongoDB

### Index recommandés (déjà créés par le script)

```javascript
// Dans MongoDB shell
use django_education

// Index pour recherches rapides
db.evaluation_userprofile.createIndex({student_id: 1}, {unique: true})
db.evaluation_result.createIndex({student_id: 1, test_id: 1})
db.evaluation_submission.createIndex({student_id: 1, status: 1})

// Index composites pour requêtes complexes
db.evaluation_test.createIndex({is_active: 1, start_date: 1, end_date: 1})
```

### Requêtes optimisées

```python
# Éviter N+1 queries
results = Result.objects.filter(student_id=student.id).values()

# Utiliser projection pour limiter les champs
User.objects.only('username', 'email')

# Batch insert pour performance
Test.objects.bulk_create([test1, test2, test3])
```

---

## 📚 Ressources

### Documentation officielle
- **Djongo** : https://djongo.readthedocs.io/
- **MongoDB** : https://docs.mongodb.com/
- **PyMongo** : https://pymongo.readthedocs.io/

### Outils utiles
- **MongoDB Compass** : Interface graphique
- **Robo 3T** : Alternative légère
- **MongoDB Atlas** : MongoDB dans le cloud (gratuit jusqu'à 512MB)

### Tutoriels
- [Django avec MongoDB](https://www.djongomapper.com/)
- [MongoDB University](https://university.mongodb.com/) (cours gratuits)

---

## 🔄 Retour en arrière (Roll Back)

Si vous voulez revenir à SQLite :

```powershell
# 1. Arrêter le serveur
# CTRL+C

# 2. Restaurer l'ancien settings.py
copy backend\settings_sqlite.py.backup backend\settings.py

# 3. Restaurer la base SQLite
copy db.sqlite3.backup db.sqlite3

# 4. Redémarrer
python manage.py runserver
```

---

## ✅ Checklist Finale

Avant de mettre en production avec MongoDB :

- [ ] MongoDB installé et démarré
- [ ] Migration réussie (tous les comptages OK)
- [ ] Tests unitaires passent
- [ ] Interface web fonctionne
- [ ] Nouveaux tests peuvent être créés
- [ ] Soumissions enregistrées correctement
- [ ] Résultats affichés correctement
- [ ] Backup SQLite conservé
- [ ] Index MongoDB créés
- [ ] Variables d'environnement configurées
- [ ] Documentation mise à jour

---

## 🎉 Félicitations !

Votre projet utilise maintenant MongoDB ! 🚀

**Prochaines étapes recommandées :**

1. **Surveiller les performances** : MongoDB Compass > Performance tab
2. **Configurer les backups automatiques** : `mongodump`
3. **Optimiser les requêtes** : Utiliser `.explain()` pour analyser
4. **Considérer MongoDB Atlas** pour la production (cloud)

**Support :**
- GitHub Issues du projet
- MongoDB Community Forums
- Djongo GitHub Issues

---

**Dernière mise à jour** : 9 octobre 2025
**Version** : 1.0
