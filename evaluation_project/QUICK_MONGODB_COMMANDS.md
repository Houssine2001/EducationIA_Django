# 🚀 COMMANDES RAPIDES - Migration MongoDB

## Installation complète (une seule commande)

```powershell
.\setup_mongodb.ps1
```

---

## Commandes individuelles

### 1. Installer MongoDB (Windows)

Télécharger: https://www.mongodb.com/try/download/community

### 2. Démarrer/Arrêter MongoDB

```powershell
# Démarrer
net start MongoDB

# Arrêter  
net stop MongoDB

# Vérifier le statut
sc query MongoDB
```

### 3. Installer les dépendances Python

```powershell
pip install -r requirements_mongodb.txt
```

### 4. Migrer les données

```powershell
python migrate_to_mongodb.py
```

### 5. Configurer Django

```powershell
# Option A: Copier le fichier de configuration
copy backend\settings_mongodb.py backend\settings.py

# Option B: Modifier manuellement backend/settings.py
# Voir MIGRATION_MONGODB_GUIDE.md
```

### 6. Démarrer le serveur

```powershell
python manage.py runserver
```

---

## Commandes MongoDB utiles

### Shell MongoDB

```powershell
# Ouvrir le shell
mongosh

# Se connecter à la base
use django_education

# Lister les collections
show collections

# Compter les documents
db.auth_user.countDocuments()
db.evaluation_userprofile.countDocuments()
db.evaluation_test.countDocuments()

# Afficher un document
db.auth_user.findOne()
db.evaluation_userprofile.findOne()

# Afficher tous les utilisateurs
db.auth_user.find().pretty()

# Quitter
exit
```

### Backup et Restore

```powershell
# Backup complet
mongodump --db django_education --out backup_mongo/

# Restore complet
mongorestore --db django_education backup_mongo/django_education/

# Export d'une collection en JSON
mongoexport --db django_education --collection auth_user --out users.json

# Import d'une collection
mongoimport --db django_education --collection auth_user --file users.json
```

---

## Dépannage rapide

### MongoDB ne démarre pas

```powershell
# Vérifier le service
sc query MongoDB

# Recréer le service
mongod --install --serviceName "MongoDB" --serviceDisplayName "MongoDB" --dbpath "C:\Program Files\MongoDB\Server\7.0\data"

# Démarrer
net start MongoDB
```

### Port 27017 déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :27017

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur "Cannot connect to MongoDB"

```powershell
# Vérifier que MongoDB écoute
netstat -an | findstr :27017

# Tester avec mongosh
mongosh mongodb://localhost:27017

# Vérifier les logs
type "C:\Program Files\MongoDB\Server\7.0\log\mongod.log"
```

### Django ne trouve pas Djongo

```powershell
# Réinstaller
pip uninstall djongo pymongo
pip install djongo==1.3.6 pymongo==3.12.3
```

---

## Tester la migration

```powershell
# Shell Django
python manage.py shell
```

```python
# Dans le shell Python
from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test, Question

# Compter
print("Users:", User.objects.count())
print("Profiles:", UserProfile.objects.count()) 
print("Tests:", Test.objects.count())
print("Questions:", Question.objects.count())

# Tester une requête
user = User.objects.first()
print("User:", user.username)
print("Profile:", user.profile)
print("XP:", user.profile.total_xp)
```

---

## Rollback vers SQLite

```powershell
# 1. Arrêter le serveur (CTRL+C)

# 2. Restaurer settings
copy backend\settings_sqlite.py.backup backend\settings.py

# 3. Restaurer la base
copy db.sqlite3.backup db.sqlite3

# 4. Redémarrer
python manage.py runserver
```

---

## Liens rapides

- **MongoDB Compass**: Interface graphique
  - Connexion: `mongodb://localhost:27017`
  
- **Documentation complète**: `MIGRATION_MONGODB_GUIDE.md`
  
- **Support MongoDB**: https://www.mongodb.com/community/forums

---

## Checklist migration

- [ ] MongoDB installé
- [ ] Service MongoDB démarré
- [ ] Dépendances Python installées
- [ ] Script de migration exécuté
- [ ] Settings.py configuré
- [ ] Serveur Django redémarré
- [ ] Tests passent
- [ ] Interface web fonctionne
- [ ] Backup SQLite conservé

---

**Date**: 9 octobre 2025
**Projet**: DjangoEducation - Migration MongoDB
