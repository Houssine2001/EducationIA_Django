# 🚀 FICHIERS DE DÉPLOIEMENT RENDER

Ce dossier contient tous les fichiers nécessaires pour déployer votre projet Django sur Render avec MongoDB Atlas.

## 📁 FICHIERS CRÉÉS

### Configuration de déploiement

| Fichier | Description |
|---------|-------------|
| `build.sh` | Script de build exécuté par Render pour installer les dépendances et collecter les fichiers statiques |
| `render.yaml` | Configuration Infrastructure as Code pour Render (optionnel mais recommandé) |
| `runtime.txt` | Spécifie la version de Python à utiliser (3.11.0) |
| `requirements.txt` | Dépendances Python (déjà existant, modifié pour ajouter whitenoise) |

### Configuration Django

| Fichier | Description |
|---------|-------------|
| `backend/settings.py` | Configuré pour production (DEBUG, ALLOWED_HOSTS, MongoDB Atlas, WhiteNoise) |

### Variables d'environnement

| Fichier | Description |
|---------|-------------|
| `.env.example` | Template pour développement local (déjà existant) |
| `.env.development` | Configuration pour développement local |
| `.env.production` | Template des variables d'environnement pour Render (NE PAS COMMITER AVEC VRAIES VALEURS) |

### Outils

| Fichier | Description |
|---------|-------------|
| `generate_secret_key.py` | Script Python pour générer une SECRET_KEY Django sécurisée |

### Documentation

| Fichier | Description |
|---------|-------------|
| `GUIDE_DEPLOIEMENT_RENDER.md` | Guide complet et détaillé du déploiement (15+ pages) |
| `DEPLOIEMENT_RAPIDE.md` | Résumé rapide en 7 étapes |
| `CHECKLIST_DEPLOIEMENT.md` | Checklist de vérification pour le déploiement |
| `README_DEPLOIEMENT.md` | Ce fichier - Vue d'ensemble |

### Sécurité

| Fichier | Description |
|---------|-------------|
| `.gitignore` | Configuré pour ne pas commiter les fichiers sensibles (.env, logs, etc.) |

---

## 🎯 PAR OÙ COMMENCER ?

### Pour un déploiement rapide (30 minutes):
➡️ Lisez **`DEPLOIEMENT_RAPIDE.md`**

### Pour comprendre tous les détails:
➡️ Lisez **`GUIDE_DEPLOIEMENT_RENDER.md`**

### Pour suivre votre progression:
➡️ Utilisez **`CHECKLIST_DEPLOIEMENT.md`**

---

## 📋 PRÉREQUIS

Avant de déployer, assurez-vous d'avoir:

✅ **MongoDB Atlas**:
- Compte créé
- Cluster actif
- Connection String récupéré
- Network Access configuré (0.0.0.0/0)
- Utilisateur de base de données créé

✅ **Git**:
- Code poussé sur GitHub/GitLab/Bitbucket
- `.gitignore` configuré correctement

✅ **Render**:
- Compte créé sur render.com
- Prêt à connecter votre repository

---

## 🚀 DÉPLOIEMENT EN 7 ÉTAPES

### 1️⃣ Préparer MongoDB Atlas
```
Connection String + Network Access + User
```

### 2️⃣ Pousser le code sur Git
```powershell
git add .
git commit -m "Configuration déploiement"
git push origin main
```

### 3️⃣ Générer SECRET_KEY
```powershell
python generate_secret_key.py
```

### 4️⃣ Créer le service Render
```
Dashboard Render → New Web Service → Configurer
```

### 5️⃣ Ajouter les variables d'environnement
```
SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, MONGODB_URI, etc.
```

### 6️⃣ Lancer le déploiement
```
Create Web Service → Attendre le build (10 min)
```

### 7️⃣ Créer un superutilisateur
```bash
python manage.py createsuperuser
```

---

## 🔧 VARIABLES D'ENVIRONNEMENT REQUISES

À configurer dans Render Dashboard → Environment:

| Variable | Exemple | Obligatoire |
|----------|---------|-------------|
| `SECRET_KEY` | `django-insecure-xyz...` | ✅ Oui |
| `DEBUG` | `False` | ✅ Oui |
| `ALLOWED_HOSTS` | `votre-app.onrender.com` | ✅ Oui |
| `CSRF_TRUSTED_ORIGINS` | `https://votre-app.onrender.com` | ✅ Oui |
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster...` | ✅ Oui |
| `MONGODB_NAME` | `django_education_prod` | ✅ Oui |

---

## 📊 ARCHITECTURE

```
Render (Web Service)
    ↓
Django + Gunicorn
    ↓
WhiteNoise (Fichiers statiques)
    ↓
MongoDB Atlas (Base de données)
```

### Technologies utilisées:
- **Serveur**: Gunicorn (WSGI)
- **Fichiers statiques**: WhiteNoise
- **Base de données**: MongoDB Atlas (Cloud)
- **Framework**: Django 4.2.16
- **Déploiement**: Render

---

## 🐛 DÉPANNAGE

### Problème: Application failed to start
**Solution**: Vérifiez les logs Render + variables d'environnement

### Problème: DisallowedHost
**Solution**: Vérifiez `ALLOWED_HOSTS` (sans espaces, avec domaine Render)

### Problème: CSRF failed
**Solution**: `CSRF_TRUSTED_ORIGINS` doit avoir `https://`

### Problème: Can't connect to MongoDB
**Solution**: 
- Vérifiez `MONGODB_URI`
- Vérifiez Network Access dans MongoDB Atlas
- Encodez les caractères spéciaux dans le mot de passe

### Problème: Static files 404
**Solution**: 
- Vérifiez que `whitenoise` est installé
- Relancez le build

---

## 📚 RESSOURCES

- **Render**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **MongoDB Atlas**: https://docs.atlas.mongodb.com/
- **WhiteNoise**: http://whitenoise.evans.io/

---

## 💰 COÛTS

### Plan Free (Recommandé pour débuter)
- **Render**: 0€/mois (750h/mois, veille après 15 min)
- **MongoDB Atlas**: 0€/mois (512 MB, Free Tier)
- **Total**: 0€/mois 🎉

### Plan Starter (Pour production)
- **Render**: $7/mois (toujours actif, meilleure performance)
- **MongoDB Atlas**: 0€/mois (ou payant selon besoins)
- **Total**: $7+/mois

---

## 🔒 SÉCURITÉ

### ✅ Checklist de sécurité:
- [x] `DEBUG = False` en production
- [x] `SECRET_KEY` unique et forte
- [x] `ALLOWED_HOSTS` restreint
- [x] CSRF protection activée
- [x] HTTPS automatique (Render)
- [x] Variables sensibles hors du code
- [x] `.env` dans `.gitignore`
- [x] MongoDB avec authentification

---

## 🔄 MISES À JOUR

Pour déployer une nouvelle version:

```powershell
# Faire vos modifications
git add .
git commit -m "Description des changements"
git push origin main
```

Render redéploie automatiquement ! 🚀

---

## ✅ APRÈS LE DÉPLOIEMENT

### À tester:
- [ ] Page d'accueil accessible
- [ ] Admin Django fonctionnel
- [ ] Connexion utilisateurs OK
- [ ] Données sauvegardées dans MongoDB
- [ ] Fichiers statiques chargés
- [ ] Aucune erreur dans les logs

### À surveiller:
- **Logs Render**: Erreurs et performances
- **MongoDB Atlas**: Connexions et stockage
- **Métriques Render**: CPU et RAM

---

## 📞 SUPPORT

En cas de problème:

1. **Consultez les logs Render** (onglet Logs)
2. **Vérifiez la checklist** (`CHECKLIST_DEPLOIEMENT.md`)
3. **Relisez le guide** (`GUIDE_DEPLOIEMENT_RENDER.md`)
4. **Testez la connexion MongoDB** depuis le Shell Render

---

## ✨ STRUCTURE DU PROJET

```
evaluation_project/
│
├── 📄 build.sh                    # Script de build Render
├── 📄 render.yaml                 # Config Infrastructure as Code
├── 📄 runtime.txt                 # Version Python (3.11.0)
├── 📄 requirements.txt            # Dépendances Python
├── 📄 manage.py                   # Script Django
│
├── 🔧 backend/
│   ├── settings.py                # Config Django (production ready)
│   ├── wsgi.py                    # Point d'entrée WSGI
│   └── urls.py                    # Routes principales
│
├── 📱 evaluation/                 # App principale
├── 📱 exercise_generator/         # Générateur IA
├── 📱 analytics_dashboard/        # Dashboard analytics
├── 📱 resources/                  # Ressources pédagogiques
│
├── 📁 static/                     # Fichiers statiques (dev)
├── 📁 staticfiles/                # Fichiers collectés (prod)
├── 📁 media/                      # Uploads utilisateurs
├── 📁 logs/                       # Logs Django
│
├── 🔐 .env.example                # Template env local
├── 🔐 .env.development            # Config dev
├── 🔐 .env.production             # Template env prod
├── 🚫 .gitignore                  # Fichiers ignorés par Git
│
├── 🔑 generate_secret_key.py      # Générateur SECRET_KEY
│
└── 📚 Documentation/
    ├── GUIDE_DEPLOIEMENT_RENDER.md       # Guide complet
    ├── DEPLOIEMENT_RAPIDE.md             # Résumé 7 étapes
    ├── CHECKLIST_DEPLOIEMENT.md          # Checklist
    └── README_DEPLOIEMENT.md             # Ce fichier
```

---

## 🎉 CONCLUSION

Tous les fichiers nécessaires ont été créés et configurés.

**Suivez simplement le guide `DEPLOIEMENT_RAPIDE.md` pour déployer en 30 minutes !**

Bon déploiement ! 🚀

---

**Créé le**: Octobre 2025
**Version**: 1.0
**Plateforme**: Render + MongoDB Atlas
**Framework**: Django 4.2.16
