# 🚀 Guide de Démarrage Rapide

## Premiers Pas avec le Projet

### ✅ Vérifier l'Installation

Le projet est prêt ! Voici comment commencer :

### 1️⃣ Vérifier que MongoDB fonctionne

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl status mongod
```

### 2️⃣ Activer l'environnement virtuel

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3️⃣ Lancer le serveur de développement

```bash
python manage.py runserver
```

Accédez à : **http://127.0.0.1:8000/**

---

## 📝 Commandes Utiles

### Gestion du Projet

```bash
# Vérifier la configuration
python manage.py check

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Accéder au shell Django
python manage.py shell
```

### MongoDB

```bash
# Se connecter à MongoDB (console)
mongosh

# Lister les bases de données
show dbs

# Utiliser la base evaluation_db
use evaluation_db

# Lister les collections
show collections
```

---

## 🎯 Prochaines Étapes Recommandées

### Étape 1 : Créer vos premiers modèles

Dans `evaluation/models.py`, définissez vos modèles de données :

```python
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'students'
    
    def __str__(self):
        return self.name
```

### Étape 2 : Créer vos vues

Dans `evaluation/views.py` :

```python
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Bienvenue dans l'application d'évaluation !")
```

### Étape 3 : Configurer les URLs

Dans `evaluation/urls.py` :

```python
from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    path('', views.index, name='index'),
]
```

Et dans `backend/urls.py`, incluez les URLs de l'application :

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('evaluation/', include('evaluation.urls')),
]
```

### Étape 4 : Tester

```bash
# Lancer le serveur
python manage.py runserver

# Visiter
http://127.0.0.1:8000/evaluation/
```

---

## 🆘 Dépannage

### Erreur : MongoDB connection failed

**Solution** : Vérifiez que MongoDB est démarré
```bash
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

### Erreur : No module named 'djongo'

**Solution** : Installez les dépendances
```bash
pip install -r requirements.txt
```

### Erreur : Port 8000 already in use

**Solution** : Utilisez un autre port
```bash
python manage.py runserver 8080
```

---

## 📚 Ressources Utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation MongoDB](https://docs.mongodb.com/)
- [Documentation Djongo](https://www.djongomapper.com/)
- Architecture du projet : voir `docs/ARCHITECTURE.md`

---

## 🎉 Félicitations !

Votre projet est maintenant prêt pour le développement.

**Prochain objectif** : Implémenter la logique métier et les modules IA ! 🚀
