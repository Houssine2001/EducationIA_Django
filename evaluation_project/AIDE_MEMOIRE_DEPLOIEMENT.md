# 📝 AIDE-MÉMOIRE DÉPLOIEMENT RENDER

## 🔑 COMMANDES IMPORTANTES

### Vérifier la configuration avant déploiement
```powershell
python verifier_deploiement.py
```

### Générer une SECRET_KEY
```powershell
python generate_secret_key.py
```

### Script automatisé (Windows)
```powershell
.\deployer.ps1
```

### Pousser le code sur Git
```powershell
git add .
git commit -m "Configuration déploiement Render"
git push origin main
```

---

## 🌐 VARIABLES D'ENVIRONNEMENT RENDER

À copier/coller dans Render Dashboard → Environment:

```
SECRET_KEY=<généré-avec-generate_secret_key.py>
DEBUG=False
ALLOWED_HOSTS=votre-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://votre-app.onrender.com
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_NAME=django_education_prod
```

**⚠️ Remplacez**:
- `votre-app` → nom de votre service Render
- `username`, `password`, `cluster` → vos identifiants MongoDB Atlas

**💡 Encodage des caractères spéciaux dans le mot de passe**:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`

---

## 🔧 CONFIGURATION RENDER

### Informations du service

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `educatia-django` (ou votre choix) |
| **Region** | `Frankfurt` (Europe) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn backend.wsgi:application` |

### Build Command détaillé
```bash
./build.sh
```

Le script `build.sh` fait:
1. Installe les dépendances (`pip install -r requirements.txt`)
2. Collecte les fichiers statiques (`collectstatic`)
3. Crée le dossier logs

### Start Command détaillé
```bash
gunicorn backend.wsgi:application
```

Options complètes (si besoin):
```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

---

## 🗄️ MONGODB ATLAS

### Connection String
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### Network Access
```
IP: 0.0.0.0/0
Description: Allow from anywhere
```

Pour plus de sécurité (IPs Render):
```
35.174.0.0/16
52.44.0.0/15
54.80.0.0/13
```

### Database User
```
Username: <votre-username>
Password: <mot-de-passe-fort>
Permissions: Read and write to any database
```

---

## 🐚 COMMANDES SHELL RENDER

### Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### Vérifier la connexion MongoDB
```bash
python manage.py shell
```
```python
from pymongo import MongoClient
import os
client = MongoClient(os.getenv('MONGODB_URI'))
print(client.server_info())
print(client.list_database_names())
```

### Collecter les fichiers statiques manuellement
```bash
python manage.py collectstatic --noinput
```

### Lister les apps Django
```bash
python manage.py showmigrations
```

### Tester une route
```bash
python manage.py check
```

---

## 🔍 VÉRIFICATIONS POST-DÉPLOIEMENT

### URLs à tester

✅ Page d'accueil:
```
https://votre-app.onrender.com/
```

✅ Admin Django:
```
https://votre-app.onrender.com/admin/
```

✅ Page de connexion:
```
https://votre-app.onrender.com/accounts/login/
```

### Vérifier les logs
Dans Render Dashboard:
1. Sélectionner votre service
2. Onglet **"Logs"**
3. Filtrer par niveau: Info, Warning, Error

### Vérifier les métriques
Dans Render Dashboard:
1. Sélectionner votre service
2. Onglet **"Metrics"**
3. Surveiller: CPU, RAM, Bandwidth

---

## 🐛 ERREURS FRÉQUENTES

### DisallowedHost at /
```
Solution: Vérifier ALLOWED_HOSTS dans Environment Variables
```

### CSRF verification failed
```
Solution: Vérifier CSRF_TRUSTED_ORIGINS (doit avoir https://)
```

### Can't connect to MongoDB
```
Solutions:
1. Vérifier MONGODB_URI
2. Vérifier Network Access dans MongoDB Atlas
3. Encoder les caractères spéciaux du mot de passe
```

### Static files not found (404)
```
Solutions:
1. Vérifier que whitenoise est installé
2. Relancer le build
3. Vérifier STATIC_ROOT dans settings.py
```

### Application Error / 500
```
Solutions:
1. Consulter les logs Render
2. Vérifier toutes les variables d'environnement
3. Tester localement avec: gunicorn backend.wsgi:application
```

---

## 📊 COMMANDES GIT

### Initialiser un repository
```powershell
git init
git add .
git commit -m "Initial commit"
```

### Ajouter un remote
```powershell
git remote add origin https://github.com/username/repo.git
git branch -M main
git push -u origin main
```

### Pousser des changements
```powershell
git add .
git commit -m "Description des changements"
git push origin main
```

### Vérifier le statut
```powershell
git status
git log --oneline
```

### Créer une branche
```powershell
git checkout -b feature/nouvelle-fonctionnalite
git push -u origin feature/nouvelle-fonctionnalite
```

---

## 🔐 SÉCURITÉ

### Générer une SECRET_KEY sécurisée
```powershell
python generate_secret_key.py
```

Ou dans Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Vérifier que .env n'est pas tracké
```powershell
git status --ignored
```

### Liste des fichiers à NE JAMAIS commiter
```
.env
.env.local
.env.production.local
*.log
db.sqlite3
media/
logs/
```

---

## 📦 DÉPENDANCES PRINCIPALES

```txt
Django==4.2.16          # Framework web
gunicorn>=21.2.0        # Serveur WSGI production
whitenoise>=6.5.0       # Fichiers statiques
djongo==1.3.7           # ORM MongoDB
pymongo==4.15.2         # Driver MongoDB
dnspython==2.8.0        # Résolution DNS (pour MongoDB Atlas)
```

---

## 🌍 URLS IMPORTANTES

### Render
- Dashboard: https://dashboard.render.com
- Documentation: https://render.com/docs
- Status: https://status.render.com

### MongoDB Atlas
- Dashboard: https://cloud.mongodb.com
- Documentation: https://docs.atlas.mongodb.com
- Connection Troubleshooting: https://docs.atlas.mongodb.com/troubleshoot-connection/

### Django
- Documentation: https://docs.djangoproject.com
- Deployment Checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

---

## 💰 COÛTS

### Render Free Tier
```
Prix: 0€/mois
Limite: 750 heures/mois
RAM: 512 MB
Veille: Après 15 min d'inactivité
Redémarrage: ~30 secondes
```

### Render Starter
```
Prix: $7/mois
RAM: 512 MB
Toujours actif: Oui
Auto-scaling: Non
```

### MongoDB Atlas Free Tier (M0)
```
Prix: 0€/mois
Stockage: 512 MB
RAM partagée: 512 MB
Backup: Pas de snapshots automatiques
Idéal pour: Développement et petits projets
```

---

## 📚 DOCUMENTATION PROJET

| Fichier | Usage |
|---------|-------|
| `DEPLOIEMENT_RAPIDE.md` | **Commencer ici** - Guide en 7 étapes |
| `GUIDE_DEPLOIEMENT_RENDER.md` | Guide complet détaillé |
| `CHECKLIST_DEPLOIEMENT.md` | Checklist de vérification |
| `README_DEPLOIEMENT.md` | Vue d'ensemble |
| `RESUME_DEPLOIEMENT.md` | Récapitulatif de la config |
| `AIDE_MEMOIRE_DEPLOIEMENT.md` | **Ce fichier** - Commandes rapides |

---

## 🚀 WORKFLOW DE DÉPLOIEMENT

```
1. ✅ Vérifier config          → python verifier_deploiement.py
2. 🔑 Générer SECRET_KEY       → python generate_secret_key.py
3. 📝 Commiter                 → git add . && git commit -m "..."
4. ⬆️  Pousser sur Git         → git push origin main
5. 🌐 Créer service Render     → dashboard.render.com
6. ⚙️  Variables d'env         → Ajouter dans Environment
7. 🚀 Déployer                 → Create Web Service
8. 👤 Créer superuser          → Shell Render
9. ✅ Tester                   → Vérifier l'application
10. 📊 Monitorer               → Logs + Metrics
```

---

## 🎯 CHECKLIST RAPIDE

Avant de déployer:
- [ ] `build.sh` créé et exécutable
- [ ] `requirements.txt` à jour (whitenoise)
- [ ] `settings.py` configuré pour production
- [ ] `.gitignore` protège les fichiers sensibles
- [ ] Code poussé sur Git
- [ ] MongoDB Atlas configuré (Network Access)
- [ ] Connection String MongoDB récupéré
- [ ] SECRET_KEY générée
- [ ] Documentation lue

Pendant le déploiement:
- [ ] Service Render créé
- [ ] Build/Start commands configurés
- [ ] Variables d'environnement ajoutées
- [ ] Déploiement lancé
- [ ] Logs surveillés

Après le déploiement:
- [ ] Superutilisateur créé
- [ ] Admin Django accessible
- [ ] Connexion fonctionnelle
- [ ] Données MongoDB OK
- [ ] Fichiers statiques OK
- [ ] Aucune erreur dans les logs

---

## 💡 ASTUCES

### Développement local avec MongoDB Atlas
```env
# Dans .env
MONGODB_URI=mongodb+srv://...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Tester Gunicorn localement
```powershell
gunicorn backend.wsgi:application
# Accéder à: http://localhost:8000
```

### Forcer un redéploiement Render
Dans Dashboard → Manual Deploy → Deploy latest commit

### Voir les variables d'environnement (Shell Render)
```bash
env | grep MONGODB
env | grep DEBUG
```

### Vérifier la version Python (Shell Render)
```bash
python --version
```

---

## 🆘 SUPPORT

En cas de blocage:
1. Consultez les **logs Render** en priorité
2. Vérifiez la **checklist** (`CHECKLIST_DEPLOIEMENT.md`)
3. Relisez le **guide complet** (`GUIDE_DEPLOIEMENT_RENDER.md`)
4. Testez la connexion **MongoDB** depuis le Shell

---

**Dernière mise à jour**: Octobre 2025
**Bon déploiement ! 🚀**
