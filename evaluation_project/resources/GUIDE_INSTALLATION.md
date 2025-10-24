# 📖 Guide d'Installation - Module Resources

## ✅ Configuration Complète

### 1. Le module est déjà configuré dans votre projet !

Voici ce qui a été fait :

#### ✔️ `backend/settings.py` - App ajoutée
```python
INSTALLED_APPS = [
    # ... autres apps
    'resources',  # ✅ Ajouté
]
```

#### ✔️ `backend/urls.py` - URLs configurées
```python
urlpatterns = [
    # ... autres URLs
    path('resources/', include('resources.urls')),  # ✅ Ajouté
]
```

#### ✔️ `templates/base.html` - Lien dans la sidebar ajouté
Le bouton "📖 Mes Ressources IA" a été ajouté dans la navigation.

---

## 🚀 Étapes de Démarrage

### 1. Créer les migrations

```powershell
python manage.py makemigrations resources
python manage.py migrate
```

### 2. Lancer le serveur

```powershell
python manage.py runserver
```

### 3. Accéder au module

Ouvrez votre navigateur : **http://127.0.0.1:8000/resources/**

---

## 📦 Dépendances à installer (optionnel pour IA)

Pour activer les fonctionnalités IA complètes :

```powershell
# Dépendances minimales (déjà installées probablement)
pip install Pillow

# Pour IA - Résumés automatiques (optionnel)
pip install transformers torch

# Pour PDF (optionnel)
pip install PyPDF2 pdfplumber

# Pour Word (optionnel)
pip install python-docx

# Pour vidéos (optionnel - nécessite FFmpeg installé)
pip install openai-whisper ffmpeg-python
```

**Note :** Les fonctionnalités de base fonctionnent SANS ces dépendances. Les résumés IA ne seront générés que si les bibliothèques sont installées.

---

## 🎯 Fonctionnalités Disponibles

### Sans dépendances IA :
- ✅ Upload de fichiers
- ✅ Organisation et gestion des ressources
- ✅ Tags et catégorisation
- ✅ Partage de ressources
- ✅ Statistiques et suivi

### Avec dépendances IA :
- ✨ Extraction automatique de texte (PDF, vidéos, Word)
- 🤖 Génération de résumés par IA
- 📊 Analyse de contenu

---

## 🔧 Dépannage

### Problème : "No module named 'resources'"
➡️ Vérifiez que `'resources'` est bien dans `INSTALLED_APPS`

### Problème : "resources is not a registered namespace"
➡️ Vérifiez que `path('resources/', include('resources.urls'))` est dans `backend/urls.py`

### Problème : Erreur lors de l'upload
➡️ Vérifiez les permissions du dossier `media/`

### Problème : Résumé IA non généré
➡️ C'est normal si les bibliothèques IA ne sont pas installées. Le module fonctionne quand même !

---

## 📂 Structure du Module

```
resources/
├── models.py          # Modèles de données
├── views.py           # Vues et logique
├── forms.py           # Formulaires
├── urls.py            # Routes
├── admin.py           # Interface admin
├── ai_services.py     # Services IA (optionnel)
└── apps.py            # Configuration

templates/resources/   # Templates Tailwind CSS
├── dashboard.html
├── upload.html
├── detail.html
├── edit.html
└── shared.html
```

---

## 🎨 Design

Le module utilise **Tailwind CSS** pour correspondre au style de votre plateforme :
- Design moderne et responsive
- Animations fluides
- Palette de couleurs harmonieuse
- Icons Font Awesome

---

## 📝 Utilisation

1. **Connectez-vous** à votre compte
2. Cliquez sur **"📖 Mes Ressources IA"** dans la sidebar
3. Cliquez sur **"Ajouter une ressource"**
4. Uploadez votre fichier (PDF, vidéo, texte)
5. Le résumé sera généré automatiquement (si les libs IA sont installées)

---

## 💡 Conseils

- **Premiers tests** : Commencez avec de petits fichiers PDF
- **Performance** : La première génération de résumé peut prendre 1-2 minutes (téléchargement des modèles IA)
- **Production** : Pensez à configurer un stockage externe pour les fichiers (AWS S3, etc.)

---

## ✨ Prêt à utiliser !

Le module est maintenant configuré et prêt à l'emploi. Lancez simplement :

```powershell
python manage.py runserver
```

Et accédez à **http://127.0.0.1:8000/resources/**

---

**Développé avec ❤️ pour EduIA Platform**
