# 🚀 GUIDE DE DÉPLOIEMENT - RENDER + MONGODB ATLAS

## 📋 PRÉREQUIS

### 1. Compte MongoDB Atlas
- ✅ Votre base de données MongoDB est déjà déployée sur Atlas
- 📝 Vous avez le **Connection String** (format: `mongodb+srv://...`)

### 2. Compte Render
- Créez un compte gratuit sur [render.com](https://render.com)
- Préparez votre repository Git (GitHub, GitLab, ou Bitbucket)

---

## 🔧 ÉTAPE 1: PRÉPARER MONGODB ATLAS

### 1.1 Récupérer le Connection String

1. Connectez-vous à [MongoDB Atlas](https://cloud.mongodb.com)
2. Sélectionnez votre cluster
3. Cliquez sur **"Connect"**
4. Choisissez **"Connect your application"**
5. Copiez le **Connection String** (ressemble à):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### 1.2 Configurer l'accès réseau

1. Dans MongoDB Atlas, allez dans **"Network Access"**
2. Cliquez sur **"Add IP Address"**
3. Sélectionnez **"Allow Access from Anywhere"** (0.0.0.0/0)
   > ⚠️ Pour la production, restreignez aux IPs de Render
4. Cliquez sur **"Confirm"**

### 1.3 Créer un utilisateur de base de données

1. Allez dans **"Database Access"**
2. Cliquez sur **"Add New Database User"**
3. Choisissez **"Password"** comme méthode d'authentification
4. Définissez un username et un mot de passe **FORT**
5. Donnez les permissions **"Read and write to any database"**
6. Cliquez sur **"Add User"**

---

## 🌐 ÉTAPE 2: PRÉPARER LE CODE POUR LE DÉPLOIEMENT

### 2.1 Vérifier les fichiers créés

Assurez-vous que ces fichiers existent dans votre projet:

- ✅ `build.sh` - Script de build pour Render
- ✅ `render.yaml` - Configuration Infrastructure as Code
- ✅ `requirements.txt` - Dépendances Python (avec `whitenoise`)
- ✅ `.env.production` - Template des variables d'environnement
- ✅ `backend/settings.py` - Configuré pour production

### 2.2 Créer un fichier `.gitignore` (si absent)

Créez un fichier `.gitignore` à la racine du projet:

```gitignore
# Environment variables
.env
.env.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
db.sqlite3
*.log

# Django
staticfiles/
media/
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### 2.3 Pousser le code sur Git

```bash
git init
git add .
git commit -m "Configuration pour déploiement Render"
git branch -M main
git remote add origin https://github.com/votre-username/votre-repo.git
git push -u origin main
```

---

## 🎯 ÉTAPE 3: DÉPLOYER SUR RENDER

### 3.1 Créer un nouveau Web Service

1. Connectez-vous à [Render Dashboard](https://dashboard.render.com)
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repository Git
4. Sélectionnez le repository de votre projet

### 3.2 Configurer le service

Remplissez les informations suivantes:

| Champ | Valeur |
|-------|--------|
| **Name** | `educatia-django` (ou votre nom) |
| **Region** | `Frankfurt` (Europe) ou proche de vous |
| **Branch** | `main` |
| **Root Directory** | (vide si à la racine) |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn backend.wsgi:application` |

### 3.3 Sélectionner le plan

- **Free**: Gratuit, mais se met en veille après 15 min d'inactivité
- **Starter**: $7/mois, toujours actif

Pour commencer, choisissez **Free**.

---

## 🔐 ÉTAPE 4: CONFIGURER LES VARIABLES D'ENVIRONNEMENT

### 4.1 Générer une SECRET_KEY

Sur votre machine locale, exécutez:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiez la clé générée.

### 4.2 Ajouter les variables d'environnement dans Render

1. Dans la page de configuration de votre service, scrollez vers **"Environment Variables"**
2. Ajoutez les variables suivantes:

| Key | Value | Exemple |
|-----|-------|---------|
| `SECRET_KEY` | Votre clé générée | `django-insecure-xyz123...` |
| `DEBUG` | `False` | `False` |
| `ALLOWED_HOSTS` | Votre domaine Render | `educatia-django.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | URLs avec https:// | `https://educatia-django.onrender.com` |
| `MONGODB_URI` | Connection String Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/...` |
| `MONGODB_NAME` | Nom de votre base | `django_education_prod` |

### 4.3 Important pour ALLOWED_HOSTS et CSRF_TRUSTED_ORIGINS

- **ALLOWED_HOSTS**: Séparez par des **virgules SANS espaces**
  ```
  educatia-django.onrender.com,www.votre-domaine.com
  ```

- **CSRF_TRUSTED_ORIGINS**: Incluez **https://** et séparez par des virgules
  ```
  https://educatia-django.onrender.com,https://www.votre-domaine.com
  ```

### 4.4 Tester le Connection String MongoDB

Avant de déployer, assurez-vous que:
1. Le **username** et **password** sont corrects
2. Les caractères spéciaux dans le mot de passe sont encodés en URL:
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`
   - etc.

---

## 🚀 ÉTAPE 5: LANCER LE DÉPLOIEMENT

### 5.1 Démarrer le build

1. Cliquez sur **"Create Web Service"**
2. Render va automatiquement:
   - Cloner votre repository
   - Exécuter `build.sh`
   - Installer les dépendances
   - Collecter les fichiers statiques
   - Démarrer Gunicorn

### 5.2 Suivre les logs

1. Allez dans l'onglet **"Logs"**
2. Surveillez le processus de build
3. Attendez le message: **"Your service is live 🎉"**

### 5.3 Vérifier le déploiement

1. Cliquez sur l'URL de votre service (ex: `https://educatia-django.onrender.com`)
2. Vous devriez voir votre application Django

---

## ✅ ÉTAPE 6: VÉRIFICATIONS POST-DÉPLOIEMENT

### 6.1 Créer un superutilisateur

Dans le **Shell** de Render:

1. Allez dans l'onglet **"Shell"**
2. Cliquez sur **"Launch Shell"**
3. Exécutez:
   ```bash
   python manage.py createsuperuser
   ```

### 6.2 Tester l'admin Django

1. Allez sur `https://votre-app.onrender.com/admin/`
2. Connectez-vous avec le superutilisateur
3. Vérifiez que vous pouvez accéder aux modèles

### 6.3 Vérifier la connexion MongoDB

Dans le Shell Render:

```bash
python manage.py shell
```

Puis:

```python
from pymongo import MongoClient
from django.conf import settings
import os

# Tester la connexion
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client[os.getenv('MONGODB_NAME')]
print("Collections:", db.list_collection_names())
```

---

## 🔄 ÉTAPE 7: MISES À JOUR AUTOMATIQUES

### 7.1 Auto-deploy activé

Render redéploie automatiquement quand vous poussez sur Git:

```bash
# Faire des modifications
git add .
git commit -m "Nouvelles fonctionnalités"
git push origin main
```

### 7.2 Déploiement manuel

Si vous désactivez l'auto-deploy:
1. Allez dans **"Manual Deploy"**
2. Sélectionnez la branche
3. Cliquez sur **"Deploy"**

---

## 🐛 DÉPANNAGE

### Problème: "Application failed to start"

**Solution**:
1. Vérifiez les logs dans Render
2. Assurez-vous que toutes les variables d'environnement sont définies
3. Vérifiez que `MONGODB_URI` est correct

### Problème: "DisallowedHost at /"

**Solution**:
1. Vérifiez `ALLOWED_HOSTS` dans les variables d'environnement
2. Assurez-vous d'utiliser le bon domaine (avec `.onrender.com`)

### Problème: "CSRF verification failed"

**Solution**:
1. Ajoutez `https://votre-app.onrender.com` à `CSRF_TRUSTED_ORIGINS`
2. Incluez bien `https://` au début

### Problème: "Cannot connect to MongoDB"

**Solution**:
1. Vérifiez que l'IP `0.0.0.0/0` est autorisée dans MongoDB Atlas
2. Vérifiez que le username/password sont corrects
3. Vérifiez que les caractères spéciaux sont encodés

### Problème: "Static files not found"

**Solution**:
1. Vérifiez que `whitenoise` est installé
2. Vérifiez que `collectstatic` s'exécute dans `build.sh`
3. Relancez le déploiement

---

## 📊 SURVEILLANCE ET MAINTENANCE

### Logs en temps réel

```bash
# Dans le dashboard Render, onglet "Logs"
# Filtrez par niveau: Info, Warning, Error
```

### Métriques

- **CPU Usage**: Surveillez dans "Metrics"
- **Memory Usage**: Vérifiez que vous restez sous 512MB (plan Free)
- **Bandwidth**: Render affiche l'utilisation réseau

### Sauvegardes MongoDB Atlas

1. Allez dans **"Backup"** dans MongoDB Atlas
2. Configurez des snapshots automatiques
3. Testez la restauration régulièrement

---

## 🔒 SÉCURITÉ EN PRODUCTION

### Checklist de sécurité

- ✅ `DEBUG = False`
- ✅ `SECRET_KEY` unique et complexe
- ✅ `ALLOWED_HOSTS` restreint à votre domaine
- ✅ `CSRF_TRUSTED_ORIGINS` configuré
- ✅ HTTPS activé (automatique avec Render)
- ✅ Connexion MongoDB avec authentification
- ✅ Variables sensibles dans Environment Variables (pas dans le code)

### Recommandations

1. **Changez le SECRET_KEY** régulièrement
2. **Restreignez les IPs MongoDB** aux serveurs Render uniquement
3. **Activez 2FA** sur MongoDB Atlas et Render
4. **Surveillez les logs** pour détecter les activités suspectes
5. **Mettez à jour** Django et les dépendances régulièrement

---

## 💰 COÛTS

### Plan Free Render
- **0€/mois**
- 750 heures/mois
- Se met en veille après 15 min
- Redémarre au premier accès (30s)

### Plan Starter Render
- **$7/mois**
- Toujours actif
- Meilleure performance

### MongoDB Atlas (Free Tier)
- **0€/mois**
- 512 MB de stockage
- Suffisant pour débuter
- Connexions limitées

---

## 🎓 RESSOURCES SUPPLÉMENTAIRES

- [Documentation Render](https://render.com/docs)
- [Documentation Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

---

## ✨ FÉLICITATIONS !

Votre application Django est maintenant déployée en production sur Render avec MongoDB Atlas ! 🎉

Pour toute question, consultez les logs ou la documentation.

**Bon déploiement ! 🚀**
