# 🚀 Guide de Déploiement EducationIA Django sur Render

**Déploiement simplifié sans Docker - Optimisé pour Render**

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Architecture du Projet](#architecture-du-projet)
3. [Configuration Locale](#configuration-locale)
4. [Déploiement sur Render](#déploiement-sur-render)
5. [Variables d'Environnement](#variables-denvironnement)
6. [Vérification du Déploiement](#vérification-du-déploiement)
7. [Domaine Personnalisé](#domaine-personnalisé)
8. [Debugging et Logs](#debugging-et-logs)
9. [Optimisations](#optimisations)
10. [FAQ et Résolution de Problèmes](#faq-et-résolution-de-problèmes)

---

## ✅ Prérequis

### Comptes nécessaires
- ✅ Compte GitHub (pour héberger le code)
- ✅ Compte Render (gratuit) : https://render.com
- ✅ Compte MongoDB Atlas (gratuit) : https://www.mongodb.com/cloud/atlas

### Outils locaux
- Python 3.11+
- Git
- Éditeur de code (VS Code recommandé)

---

## 🏗️ Architecture du Projet

```
EducationIA_Django/
├── evaluation_project/          # Projet Django principal
│   ├── backend/                 # Configuration Django
│   │   ├── settings.py         # ⚙️ Configuration (Render-ready)
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── evaluation/              # App principale
│   ├── exercise_generator/      # Générateur d'exercices
│   ├── analytics_dashboard/     # Dashboard analytics
│   ├── resources/               # Gestion ressources
│   ├── static/                  # Fichiers statiques
│   ├── staticfiles/            # (Généré par collectstatic)
│   ├── templates/               # Templates Django
│   ├── manage.py
│   └── requirements.txt        # 📦 Dépendances optimisées
├── build.sh                     # 🔨 Script de build Render
├── runtime.txt                  # 🐍 Version Python
├── .env.example                 # Exemple de variables d'env
├── .gitignore
└── README_RENDER.md            # Ce fichier
```

### Points Clés de Configuration

#### 1. **requirements.txt Optimisé**
```
✅ Django + Gunicorn + WhiteNoise
✅ MongoDB (djongo, pymongo, dnspython)
✅ Librairies légères (requests, PyPDF2, etc.)
❌ Librairies lourdes COMMENTÉES (torch, transformers, whisper)
```

**Pourquoi?** Les librairies lourdes (2-4 GB) causent des timeouts et des erreurs de mémoire sur Render. À la place, nous utilisons l'API Hugging Face (gratuite).

#### 2. **settings.py Configuré**
```python
✅ DEBUG via variable d'environnement
✅ ALLOWED_HOSTS avec .onrender.com
✅ WhiteNoise pour servir les static files
✅ MongoDB Atlas via MONGO_URI
✅ SECRET_KEY depuis environnement
```

#### 3. **build.sh**
Script exécuté par Render pour builder l'application :
```bash
1. Installer les dépendances (pip install)
2. Collecter les fichiers statiques (collectstatic)
3. Appliquer les migrations (migrate)
```

---

## 💻 Configuration Locale

### Étape 1: Cloner le Projet

```bash
git clone https://github.com/votre-username/EducationIA_Django.git
cd EducationIA_Django
```

### Étape 2: Créer un Environnement Virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Étape 3: Installer les Dépendances

```bash
cd evaluation_project
pip install -r requirements.txt
```

### Étape 4: Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
DJANGO_SECRET_KEY=your-local-secret-key
DEBUG=1
USE_MONGO=1
MONGO_URI=mongodb+srv://salmamejri17_db_user:IdBS3lUgfmYEyGQ8@cluster.uxsk5qc.mongodb.net/?appName=Cluster
MONGO_DB_NAME=django_education
```

### Étape 5: Appliquer les Migrations

```bash
python manage.py migrate
```

### Étape 6: Créer un Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Étape 7: Collecter les Fichiers Statiques

```bash
python manage.py collectstatic --noinput
```

### Étape 8: Lancer le Serveur Local

```bash
python manage.py runserver
```

Ouvrir http://localhost:8000 dans votre navigateur.

---

## 🌐 Déploiement sur Render

### Étape 1: Préparer le Projet pour GitHub

#### 1.1 Créer un dépôt GitHub

```bash
# Si pas déjà fait
git init
git add .
git commit -m "Initial commit - Projet prêt pour Render"
git branch -M main
git remote add origin https://github.com/votre-username/EducationIA_Django.git
git push -u origin main
```

#### 1.2 Vérifier le .gitignore

Assurez-vous que `.env` est dans `.gitignore` :

```gitignore
# Fichiers sensibles
*.env
.env
__pycache__/
*.pyc
db.sqlite3
staticfiles/
media/
venv/
```

### Étape 2: Créer un Compte Render

1. Aller sur https://render.com
2. S'inscrire avec GitHub
3. Autoriser Render à accéder à vos dépôts

### Étape 3: Créer un Web Service

#### 3.1 Dashboard Render

1. Cliquer sur **"New +"** → **"Web Service"**
2. Sélectionner **"Connect a repository"**
3. Choisir votre dépôt `EducationIA_Django`

#### 3.2 Configuration du Service

Remplir les champs suivants :

| Champ | Valeur |
|-------|--------|
| **Name** | `educationia-django` (ou votre nom) |
| **Region** | `Frankfurt (EU Central)` ou le plus proche |
| **Branch** | `main` |
| **Root Directory** | (vide) |
| **Runtime** | `Python 3` |
| **Build Command** | `bash build.sh` |
| **Start Command** | `cd evaluation_project && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT` |
| **Plan** | `Free` (gratuit) |

#### 3.3 Cliquer sur **"Advanced"**

Ajouter les variables d'environnement (voir section suivante).

### Étape 4: Configuration des Variables d'Environnement

Dans la section **Environment** de Render, ajouter :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `PYTHON_VERSION` | `3.11.0` | Version Python |
| `DJANGO_SECRET_KEY` | `votre-cle-secrete-aleatoire` | Clé secrète Django (générer une nouvelle) |
| `DEBUG` | `0` | Mode production (False) |
| `USE_MONGO` | `1` | Utiliser MongoDB |
| `MONGO_URI` | `mongodb+srv://salmamejri17_db_user:IdBS3lUgfmYEyGQ8@cluster.uxsk5qc.mongodb.net/?appName=Cluster` | URL MongoDB Atlas |
| `MONGO_DB_NAME` | `django_education` | Nom de la base |
| `HUGGINGFACE_API_TOKEN` | `hf_xxxxx` (optionnel) | Token Hugging Face pour IA |

#### Générer une SECRET_KEY Django

```python
# Dans un terminal Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou en ligne : https://djecrety.ir/

### Étape 5: Déployer

1. Cliquer sur **"Create Web Service"**
2. Render va automatiquement :
   - Cloner votre repo
   - Exécuter `build.sh`
   - Installer les dépendances
   - Collecter les static files
   - Appliquer les migrations
   - Démarrer Gunicorn

3. Attendre 5-10 minutes (première fois)

### Étape 6: Accéder à l'Application

URL générée : `https://educationia-django.onrender.com`

---

## 🔐 Variables d'Environnement

### Variables Obligatoires

```env
DJANGO_SECRET_KEY=xxxxx     # Clé secrète unique et aléatoire
DEBUG=0                      # 0=Production, 1=Development
USE_MONGO=1                  # 1=MongoDB, 0=SQLite
MONGO_URI=mongodb+srv://...  # URL complète MongoDB Atlas
MONGO_DB_NAME=django_education
```

### Variables Optionnelles

```env
HUGGINGFACE_API_TOKEN=hf_xxxxx  # Pour analyse IA avec Hugging Face
```

### Obtenir un Token Hugging Face (Gratuit)

1. Créer un compte sur https://huggingface.co
2. Aller dans Settings → Access Tokens
3. Créer un token avec permissions "Read"
4. Copier le token (commence par `hf_`)

---

## ✅ Vérification du Déploiement

### 1. Vérifier le Build

Dans Render Dashboard → Logs, vous devriez voir :

```
✅ Build terminé avec succès!
✅ Migrations appliquées
✅ Static files collectés
✅ Gunicorn démarré
```

### 2. Tester l'Application

Ouvrir votre URL Render dans un navigateur :

```
https://educationia-django.onrender.com
```

### 3. Vérifier les Static Files

Les fichiers CSS/JS doivent se charger correctement grâce à WhiteNoise.

### 4. Tester l'Admin Django

```
https://educationia-django.onrender.com/admin/
```

Si vous n'avez pas encore de superuser, créez-en un via le Shell Render :

```bash
# Dans Render Dashboard → Shell
cd evaluation_project
python manage.py createsuperuser
```

### 5. Vérifier MongoDB

Dans les logs, vous devriez voir :

```
🔧 USE_MONGO: True
🔧 MONGO_DB_NAME: django_education
✅ Connected to MongoDB Atlas
```

---

## 🌍 Domaine Personnalisé

### Option 1: Utiliser un Sous-domaine Render (Gratuit)

Par défaut, vous obtenez : `https://votre-app.onrender.com`

### Option 2: Domaine Personnalisé (Plan Payant)

Si vous avez un domaine (ex: `educationia.com`) :

1. Aller dans Render Dashboard → Settings → Custom Domain
2. Ajouter votre domaine
3. Configurer les DNS records chez votre registrar :

```
Type: CNAME
Name: www
Value: votre-app.onrender.com
```

4. Render générera automatiquement un certificat SSL

---

## 🐛 Debugging et Logs

### Voir les Logs en Temps Réel

1. Render Dashboard → Votre Service
2. Onglet **"Logs"**
3. Activer **"Live Tail"**

### Logs Importants

```bash
# Build logs (pendant le déploiement)
📦 Installation des dépendances...
📂 Collecte des fichiers statiques...
🗄️ Application des migrations...

# Runtime logs (application running)
🔧 Django DEBUG mode: False
🔧 USE_MONGO: True
✅ Connected to MongoDB Atlas
[INFO] Gunicorn listening at: http://0.0.0.0:10000
```

### Erreurs Courantes

#### 1. **Erreur 502 Bad Gateway**

**Cause**: Build échoué ou Gunicorn n'a pas démarré

**Solution**:
```bash
# Vérifier les logs de build
# Vérifier que build.sh s'exécute correctement
# Vérifier la commande Start: gunicorn backend.wsgi:application
```

#### 2. **Static Files Non Chargés**

**Cause**: collectstatic pas exécuté ou WhiteNoise mal configuré

**Solution**:
```python
# Dans settings.py, vérifier:
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Doit être après SecurityMiddleware
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 3. **MongoDB Connection Failed**

**Cause**: MONGO_URI invalide ou MongoDB Atlas pas configuré

**Solution**:
```bash
# Vérifier que MONGO_URI contient bien:
# - srv:// (pas juste mongodb://)
# - Username et password corrects
# - ?appName=Cluster à la fin

# Vérifier dans MongoDB Atlas:
# - IP Whitelist = 0.0.0.0/0 (autoriser toutes les IPs)
# - User créé avec droits readWrite
```

#### 4. **Module Not Found Error**

**Cause**: Dépendance manquante dans requirements.txt

**Solution**:
```bash
# Ajouter la dépendance dans requirements.txt
# Commit et push sur GitHub
# Render va rebuild automatiquement
```

#### 5. **Memory Limit Exceeded**

**Cause**: Tentative d'installer torch/transformers (trop lourd)

**Solution**:
```bash
# Vérifier que requirements.txt a bien ces libs COMMENTÉES:
# torch>=2.1.0
# transformers>=4.35.0
# openai-whisper>=20231117

# Utiliser à la place l'API Hugging Face (gratuite)
```

### Shell Interactif Render

Pour exécuter des commandes Django sur le serveur :

1. Render Dashboard → Votre Service → **"Shell"**
2. Exécuter :

```bash
cd evaluation_project
python manage.py shell

# Exemples de commandes:
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## ⚡ Optimisations

### 1. Performance

#### WhiteNoise (Static Files)

```python
# settings.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Avantages :
- Compression Gzip automatique
- Cache HTTP long terme
- Pas besoin de CDN pour small apps

#### Gunicorn Workers

```bash
# Start Command optimisée
gunicorn backend.wsgi:application --workers 2 --threads 4 --timeout 60
```

- Workers = 2x CPU cores (Render Free = 1 CPU → 2 workers max)
- Threads = 4 par worker pour I/O concurrence

### 2. Database

#### Index MongoDB

Pour les requêtes fréquentes, créer des index :

```python
# Dans Django shell
from evaluation.models import Result
Result.objects.create_index([('student', 1), ('created_at', -1)])
```

#### Connection Pooling

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'CLIENT': {
            'host': MONGO_URI,
            'maxPoolSize': 50,
            'minPoolSize': 10,
        }
    }
}
```

### 3. Caching

Ajouter Redis pour cache (plan payant Render) :

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}
```

---

## 📊 Monitoring

### Render Dashboard

- **Metrics**: CPU, Memory, Bandwidth
- **Logs**: Temps réel et historique
- **Events**: Deployments, crashes, restarts

### Logs Personnalisés

```python
# Dans votre code Django
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Test passé avec succès")
logger.error("❌ Erreur lors de l'analyse IA")
```

Ces logs apparaîtront dans Render Logs.

---

## 🔄 Mises à Jour et Redéploiement

### Déploiement Automatique

Render redéploie automatiquement à chaque push sur `main` :

```bash
git add .
git commit -m "Ajout de nouvelles fonctionnalités"
git push origin main
```

Render détectera le push et relancera le build.

### Déploiement Manuel

Dans Render Dashboard :
1. Aller dans votre service
2. Cliquer sur **"Manual Deploy"** → **"Deploy latest commit"**

### Rollback

Si un déploiement cause des problèmes :

1. Render Dashboard → **"Events"**
2. Trouver le déploiement stable précédent
3. Cliquer sur **"Rollback to this deploy"**

---

## ❓ FAQ et Résolution de Problèmes

### Q1: Combien coûte Render Free Plan?

**R**: Gratuit avec limitations :
- 750 heures/mois (suffisant pour 1 app)
- 512 MB RAM
- Temps de build: 15 min max
- L'app se met en veille après 15 min d'inactivité (redémarre en ~30s)

### Q2: Comment éviter que l'app se mette en veille?

**R**: 
- **Plan Starter (7$/mois)**: Pas de mise en veille
- **Gratuit**: Utiliser un service de ping externe (ex: UptimeRobot)

### Q3: Puis-je utiliser SQLite au lieu de MongoDB?

**R**: Oui, mais **NON RECOMMANDÉ** sur Render car :
- Le disque est éphémère (données perdues à chaque redéploiement)
- Utiliser MongoDB Atlas (gratuit) ou PostgreSQL (Render propose une DB gratuite)

### Q4: Les librairies IA (torch, transformers) sont commentées. Comment faire de l'IA?

**R**: Utiliser les **APIs externes gratuites** :
- **Hugging Face Inference API** (gratuite) : voir `ai_concept_analyzer.py`
- **OpenAI API** (payant mais puissant)
- **AssemblyAI** (transcription audio)

Exemple dans le code :

```python
# ai_concept_analyzer.py
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

response = requests.post(API_URL, headers=headers, json={
    "inputs": "Analyser les performances de l'étudiant...",
})
```

### Q5: Comment débugger une erreur en production?

**R**: 
1. Activer temporairement DEBUG :
   ```env
   DEBUG=1  # Dans Render Environment Variables
   ```
   **ATTENTION**: Remettre à `0` après debug!

2. Voir les logs détaillés :
   ```bash
   # Render Dashboard → Logs → Live Tail
   ```

3. Utiliser le Shell :
   ```bash
   # Render Dashboard → Shell
   cd evaluation_project
   python manage.py shell
   ```

### Q6: Comment sécuriser davantage l'application?

**R**:
```python
# settings.py (en production)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Q7: Render Free Plan suffit-il pour mon projet?

**R**: Oui si :
- ✅ Trafic faible/moyen (< 1000 users/jour)
- ✅ Pas besoin de disponibilité 24/7
- ✅ Temps de réponse ~30s OK après veille

Non si :
- ❌ Trafic élevé (> 5000 users/jour)
- ❌ Besoin de disponibilité critique
- ❌ Calculs lourds (ML models locaux)

→ Dans ce cas : **Render Starter Plan (7$/mois)**

---

## 📚 Ressources Utiles

### Documentation

- **Render**: https://render.com/docs
- **Django**: https://docs.djangoproject.com
- **MongoDB Atlas**: https://www.mongodb.com/docs/atlas
- **Hugging Face API**: https://huggingface.co/docs/api-inference

### Tutoriels

- Déployer Django sur Render : https://render.com/docs/deploy-django
- WhiteNoise : https://whitenoise.evans.io
- Djongo : https://nesdis.github.io/djongo

### Support

- **Render Community**: https://community.render.com
- **Render Status**: https://status.render.com

---

## ✅ Checklist Finale

Avant de déployer, vérifier :

- [ ] `requirements.txt` optimisé (librairies lourdes commentées)
- [ ] `settings.py` configuré (DEBUG=0, ALLOWED_HOSTS, WhiteNoise)
- [ ] `build.sh` exécutable et fonctionnel
- [ ] `.env.example` créé (sans données sensibles)
- [ ] `.gitignore` contient `.env` et fichiers sensibles
- [ ] MongoDB Atlas configuré (IP whitelist = 0.0.0.0/0)
- [ ] Variables d'environnement ajoutées dans Render
- [ ] Commit et push sur GitHub
- [ ] Service Render créé et configuré
- [ ] Build réussi (vérifier les logs)
- [ ] Application accessible via URL Render
- [ ] Static files chargés correctement
- [ ] Admin Django accessible
- [ ] Tests fonctionnels passés

---

## 🎉 Félicitations !

Votre application Django est maintenant déployée sur Render !

### Prochaines Étapes

1. **Créer un superuser** (via Shell Render)
2. **Ajouter des données de test**
3. **Configurer un domaine personnalisé** (optionnel)
4. **Monitorer les performances**
5. **Optimiser selon les besoins**

### Support

Si vous rencontrez des problèmes, consultez :
- Les logs Render (Dashboard → Logs)
- La documentation officielle
- Le code dans `evaluation_project/`

---

**Bon déploiement ! 🚀**

---

*Dernière mise à jour : 29 octobre 2025*
