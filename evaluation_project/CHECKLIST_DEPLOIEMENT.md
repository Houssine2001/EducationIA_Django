# 🚀 CHECKLIST DE DÉPLOIEMENT RENDER

## ✅ AVANT LE DÉPLOIEMENT

### Préparation MongoDB Atlas
- [ ] Compte MongoDB Atlas créé
- [ ] Cluster MongoDB créé et actif
- [ ] Connection String récupéré
- [ ] Network Access configuré (0.0.0.0/0 ou IPs Render)
- [ ] Utilisateur de base de données créé avec permissions

### Préparation du code
- [ ] Fichier `build.sh` créé et exécutable
- [ ] Fichier `render.yaml` configuré
- [ ] `requirements.txt` contient `whitenoise` et `gunicorn`
- [ ] `settings.py` configuré pour production (DEBUG, ALLOWED_HOSTS, etc.)
- [ ] `.gitignore` mis à jour (ne pas commiter .env)
- [ ] Code poussé sur Git (GitHub, GitLab, Bitbucket)

### Compte Render
- [ ] Compte Render créé
- [ ] Repository Git connecté

---

## 🔧 CONFIGURATION RENDER

### Création du service
- [ ] Nouveau Web Service créé
- [ ] Repository sélectionné
- [ ] Branche `main` sélectionnée
- [ ] Runtime: Python 3
- [ ] Build Command: `./build.sh`
- [ ] Start Command: `gunicorn backend.wsgi:application`
- [ ] Plan choisi (Free ou Starter)

### Variables d'environnement
Ajoutez ces variables dans "Environment" de Render:

- [ ] `SECRET_KEY` - Clé générée avec `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] `DEBUG` - Valeur: `False`
- [ ] `ALLOWED_HOSTS` - Valeur: `votre-app.onrender.com` (votre domaine Render)
- [ ] `CSRF_TRUSTED_ORIGINS` - Valeur: `https://votre-app.onrender.com`
- [ ] `MONGODB_URI` - Valeur: Connection String de MongoDB Atlas
- [ ] `MONGODB_NAME` - Valeur: Nom de votre base de données

⚠️ **IMPORTANT**: 
- Pas d'espaces dans les listes séparées par virgules
- CSRF_TRUSTED_ORIGINS doit inclure `https://`
- Encodez les caractères spéciaux dans MONGODB_URI

---

## 🚀 DÉPLOIEMENT

### Lancement
- [ ] Cliquer sur "Create Web Service"
- [ ] Attendre la fin du build (5-10 minutes)
- [ ] Vérifier les logs pour des erreurs
- [ ] Application accessible via l'URL Render

### Vérifications
- [ ] Page d'accueil charge correctement
- [ ] Admin Django accessible (`/admin/`)
- [ ] Connexion à MongoDB fonctionnelle
- [ ] Fichiers statiques chargés correctement
- [ ] Aucune erreur 500 ou 404

---

## ✅ POST-DÉPLOIEMENT

### Administration
- [ ] Créer un superutilisateur via Shell Render
- [ ] Se connecter à l'admin Django
- [ ] Vérifier les modèles de données

### Tests fonctionnels
- [ ] Inscription d'un utilisateur
- [ ] Connexion d'un utilisateur
- [ ] Création de contenu (test)
- [ ] Navigation entre les pages

### Monitoring
- [ ] Logs configurés et accessibles
- [ ] Métriques Render vérifiées (CPU, RAM)
- [ ] MongoDB Atlas - surveiller les connexions

---

## 🔒 SÉCURITÉ

### Checklist de sécurité finale
- [ ] DEBUG = False en production
- [ ] SECRET_KEY unique et forte
- [ ] ALLOWED_HOSTS restreint au domaine
- [ ] CSRF protection activée
- [ ] HTTPS activé (automatique sur Render)
- [ ] Variables sensibles dans Environment (pas dans le code)
- [ ] .env et .env.production.local dans .gitignore
- [ ] MongoDB accessible uniquement aux IPs autorisées

---

## 📝 COMMANDES UTILES

### Générer SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Créer un superutilisateur (Shell Render)
```bash
python manage.py createsuperuser
```

### Tester la connexion MongoDB (Shell Render)
```bash
python manage.py shell
```
```python
from pymongo import MongoClient
import os
client = MongoClient(os.getenv('MONGODB_URI'))
print(client.list_database_names())
```

### Vérifier les fichiers statiques
```bash
python manage.py collectstatic --dry-run
```

---

## 🐛 DÉPANNAGE RAPIDE

### Erreur: DisallowedHost
➡️ Vérifiez `ALLOWED_HOSTS` dans les variables d'environnement

### Erreur: CSRF failed
➡️ Ajoutez `https://` dans `CSRF_TRUSTED_ORIGINS`

### Erreur: Can't connect to MongoDB
➡️ Vérifiez `MONGODB_URI` et les Network Access dans Atlas

### Erreur: Static files 404
➡️ Vérifiez que `whitenoise` est installé et dans MIDDLEWARE

### Application en veille (plan Free)
➡️ Normal après 15 min d'inactivité - redémarre automatiquement

---

## 📚 RESSOURCES

- Guide complet: `GUIDE_DEPLOIEMENT_RENDER.md`
- Documentation Render: https://render.com/docs
- MongoDB Atlas: https://docs.atlas.mongodb.com

---

## ✨ STATUT DU DÉPLOIEMENT

**Date**: _______________

**URL Production**: _______________

**Status**: [ ] En cours [ ] Déployé [ ] Erreur

**Notes**:
_______________________________________
_______________________________________
_______________________________________
