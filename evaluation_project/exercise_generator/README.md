# 🤖 Générateur d'Exercices IA - Documentation

## 📚 Vue d'ensemble

Le **Générateur d'Exercices IA** est un module Django qui permet aux enseignants de générer automatiquement des exercices pédagogiques (QCM, Vrai/Faux, Texte à trous) à partir de documents de cours (texte ou PDF).

### ✨ Fonctionnalités principales

- ✅ **Analyse automatique de documents** (texte brut ou PDF)
- ✅ **Extraction de concepts clés** et idées principales
- ✅ **Génération automatique d'exercices** :
  - QCM (Questions à Choix Multiples)
  - Vrai/Faux
  - Texte à trous
- ✅ **Validation et modération** des exercices par l'enseignant
- ✅ **Création de tests personnalisés** à partir d'exercices sélectionnés
- ✅ **Export vers l'application d'évaluation** existante
- ✅ **100% Local** - Pas d'API externe requise

---

## 🚀 Installation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les packages principaux sont :
- `Django==4.2.16` - Framework web
- `PyPDF2==3.0.1` - Extraction de texte depuis PDF

### 2. Ajouter l'application dans Django

L'application `exercise_generator` est déjà configurée dans `INSTALLED_APPS` du fichier `backend/settings.py` :

```python
INSTALLED_APPS = [
    # ...
    'evaluation',
    'exercise_generator',  # ✅ Générateur d'exercices IA
]
```

### 3. Créer les migrations et la base de données

```bash
python manage.py makemigrations exercise_generator
python manage.py migrate
```

### 4. Créer un superutilisateur (si pas déjà fait)

```bash
python manage.py createsuperuser
```

### 5. Démarrer le serveur

```bash
python manage.py runserver
```

Accédez au générateur : **http://127.0.0.1:8000/generator/**

---

## 📖 Guide d'utilisation

### Pour les Enseignants

#### 1️⃣ **Uploader un document de cours**

1. Connectez-vous avec votre compte enseignant
2. Accédez à `/generator/`
3. Cliquez sur **"Nouveau Document"**
4. Remplissez les informations :
   - Titre du document
   - Matière (ex: Mathématiques, Biologie)
   - Sujet spécifique (ex: Photosynthèse)
   - Niveau (ex: Seconde, Terminale)
5. Choisissez le type :
   - **Texte** : Collez directement votre cours
   - **PDF** : Uploadez un fichier PDF
6. Cliquez sur **"Analyser et Générer"**

#### 2️⃣ **L'IA analyse le document**

L'IA va :
- Extraire le texte (si PDF)
- Identifier les **concepts clés**
- Extraire les **idées principales**
- Détecter les **définitions**
- Repérer les **relations causales**

#### 3️⃣ **Génération automatique d'exercices**

L'IA génère automatiquement :
- **QCM** : Questions avec 4 choix de réponses
- **Vrai/Faux** : Affirmations à valider
- **Texte à trous** : Phrases avec mots manquants

Chaque exercice reçoit un **score de qualité** (0-1) calculé automatiquement.

#### 4️⃣ **Validation des exercices**

1. Consultez les exercices générés
2. Validez ceux qui sont corrects
3. Rejetez ou modifiez ceux qui ne conviennent pas
4. Filtrez par :
   - Type d'exercice
   - Difficulté (Facile/Moyen/Difficile)
   - Score de qualité

#### 5️⃣ **Créer un test personnalisé**

1. Sélectionnez les exercices validés
2. Cliquez sur **"Créer un Test"**
3. Donnez un titre et une description
4. Le test est créé avec :
   - Durée suggérée automatique
   - Distribution des types et difficultés
   - Possibilité d'export vers l'app d'évaluation

#### 6️⃣ **Exporter vers l'évaluation**

1. Depuis la page du test, cliquez sur **"Exporter"**
2. Le test est automatiquement créé dans l'application `evaluation`
3. Les étudiants peuvent maintenant y répondre

---

## 🧠 Comment fonctionne l'IA ?

### Analyse de Documents (`ai_document_analyzer.py`)

L'IA utilise des techniques de **Natural Language Processing (NLP)** :

1. **Nettoyage du texte** : Suppression des caractères inutiles
2. **Tokenisation** : Découpage en mots et phrases
3. **Extraction de mots-clés** : Identification des termes importants (TF-IDF)
4. **Extraction de concepts** : Détection de bigrammes et trigrammes significatifs
5. **Détection de définitions** : Recherche de marqueurs ("est défini comme", "signifie")
6. **Relations causales** : Identification des causes et effets ("parce que", "donc")

### Génération d'Exercices (`ai_exercise_generator.py`)

#### QCM (Choix Multiples)
- Utilise les **définitions** extraites
- Génère 3 **distracteurs** plausibles
- Calcule la **difficulté** selon la complexité

#### Vrai/Faux
- Crée des affirmations **vraies** à partir de phrases importantes
- Génère des affirmations **fausses** par négation ou substitution

#### Texte à Trous
- Sélectionne des **mots-clés** dans des phrases importantes
- Remplace le mot par des underscores `___`
- L'étudiant doit retrouver le mot manquant

### Score de Qualité

Chaque exercice reçoit un score (0-1) basé sur :
- **Clarté de la question**
- **Pertinence de la réponse**
- **Qualité des distracteurs** (pour QCM)
- **Complexité appropriée**

---

## 🗂️ Structure du Module

```
exercise_generator/
├── __init__.py
├── apps.py
├── models.py                      # Modèles de données
├── admin.py                       # Interface admin Django
├── views.py                       # Vues (logique de contrôleur)
├── urls.py                        # Routes URL
├── forms.py                       # Formulaires Django
├── services.py                    # Service principal
├── ai_document_analyzer.py        # Analyseur de documents IA
├── ai_exercise_generator.py       # Générateur d'exercices IA
├── pdf_extractor.py               # Extracteur de texte PDF
└── migrations/                    # Migrations de base de données
```

---

## 💾 Modèles de Données

### `CourseDocument`
Document de cours uploadé par l'enseignant

**Champs principaux :**
- `title` : Titre du document
- `content` : Contenu textuel
- `subject` : Matière
- `topic` : Sujet spécifique
- `key_concepts` : Concepts clés extraits (JSON)
- `processing_status` : Statut du traitement

### `GeneratedExercise`
Exercice généré par l'IA

**Champs principaux :**
- `exercise_type` : mcq / true_false / fill_blank
- `question_text` : Texte de la question
- `options_data` : Options et réponse correcte (JSON)
- `difficulty` : easy / medium / hard
- `quality_score` : Score de qualité (0-1)
- `status` : draft / validated / published / rejected

### `GeneratedTest`
Test créé à partir d'exercices sélectionnés

**Champs principaux :**
- `title` : Titre du test
- `exercises` : ManyToMany vers GeneratedExercise
- `suggested_duration` : Durée suggérée (minutes)
- `evaluation_test_id` : ID du test exporté

### `ExerciseGenerationConfig`
Configuration personnalisée par enseignant

**Champs principaux :**
- `default_exercise_count` : Nombre d'exercices par défaut
- `mcq_percentage` : % de QCM
- `true_false_percentage` : % de Vrai/Faux
- `min_quality_score` : Seuil de qualité minimal

---

## 🔧 Configuration

### Personnaliser la génération

Accédez à `/generator/config/` pour modifier :

1. **Nombre d'exercices** : 5 à 50
2. **Distribution des types** :
   - QCM : 0-100%
   - Vrai/Faux : 0-100%
   - Texte à trous : 0-100%
3. **Distribution des difficultés** :
   - Facile : 0-100%
   - Moyen : 0-100%
   - Difficile : 0-100%
4. **Seuil de qualité** : 0.0 à 1.0
5. **Validation automatique** : Publier auto si haute qualité
6. **Inclure explications** : Oui/Non

---

## 🎯 Cas d'Usage

### Exemple 1 : Cours de Biologie

**Document :**
```
La photosynthèse est le processus par lequel les plantes vertes 
transforment la lumière solaire en énergie chimique. Ce processus 
se déroule dans les chloroplastes et nécessite de l'eau, du CO2 
et de la lumière. Les produits sont le glucose et l'oxygène.
```

**Exercices générés :**

1. **QCM** : Que signifie photosynthèse ?
   - A) Transformation de lumière en énergie ✅
   - B) Respiration des plantes
   - C) Absorption d'eau
   - D) Production de CO2

2. **Vrai/Faux** : La photosynthèse se déroule dans les chloroplastes.
   - Réponse : **Vrai** ✅

3. **Texte à trous** : La photosynthèse nécessite de l'eau, du ___ et de la lumière.
   - Réponse : **CO2** ✅

### Exemple 2 : Cours de Mathématiques

**Document :**
```
Une équation du second degré est de la forme ax² + bx + c = 0, 
où a ≠ 0. Le discriminant Δ = b² - 4ac permet de déterminer 
le nombre de solutions. Si Δ > 0, il y a deux solutions distinctes.
```

**Exercices générés :**

1. **QCM** : Quelle est la forme d'une équation du second degré ?
   - A) ax² + bx + c = 0 ✅
   - B) ax + b = 0
   - C) ax³ + bx² + c = 0
   - D) a/x + b = 0

2. **Vrai/Faux** : Si le discriminant est positif, il y a deux solutions.
   - Réponse : **Vrai** ✅

3. **Texte à trous** : Le discriminant est calculé par Δ = b² - ___.
   - Réponse : **4ac** ✅

---

## 📊 Administration Django

Accédez à `/admin/` pour gérer :

- **Documents de cours** : Voir tous les documents uploadés
- **Exercices générés** : Filtrer, valider, supprimer
- **Tests générés** : Gérer les tests créés
- **Configurations** : Voir les configs par enseignant

---

## 🔒 Sécurité et Permissions

- ✅ **Authentification requise** : Seuls les utilisateurs connectés peuvent accéder
- ✅ **Isolation par enseignant** : Chaque enseignant ne voit que ses propres documents
- ✅ **Validation manuelle** : Les exercices ne sont pas publiés automatiquement
- ✅ **Aucune API externe** : Toutes les données restent locales

---

## 🚧 Limitations Actuelles

1. **Langue** : Optimisé pour le **français** uniquement
2. **PDF** : L'extraction peut varier selon la qualité du PDF
3. **IA basique** : Utilise du NLP simple, pas de deep learning
4. **Distracteurs** : Les mauvaises réponses peuvent parfois manquer de pertinence

---

## 🔮 Améliorations Futures

### À court terme :
- [ ] Support multilingue (anglais, arabe)
- [ ] Édition manuelle des exercices
- [ ] Import/Export de tests en JSON
- [ ] Statistiques de performance des exercices

### À moyen terme :
- [ ] Intégration de modèles NLP avancés (spaCy, BERT)
- [ ] Génération de questions ouvertes
- [ ] Analyse de similarité sémantique
- [ ] Suggestion automatique de cours liés

### À long terme :
- [ ] IA adaptative selon le niveau des étudiants
- [ ] Génération d'explications détaillées
- [ ] Chatbot pédagogique
- [ ] Analyse de progression personnalisée

---

## 🐛 Dépannage

### Erreur : "PyPDF2 n'est pas installé"
```bash
pip install PyPDF2
```

### Les exercices ne sont pas générés
- Vérifiez que le texte contient au moins 50 mots
- Assurez-vous que le contenu est en français
- Consultez les logs dans la page du document

### Le PDF n'est pas extrait correctement
- Utilisez des PDF avec texte sélectionnable (pas des images)
- Essayez d'uploader le texte directement
- Vérifiez le format du PDF

---

## 📞 Support

Pour toute question ou problème :
1. Consultez cette documentation
2. Vérifiez les logs Django (`python manage.py runserver`)
3. Consultez l'interface admin pour les détails

---

## 📜 Licence

Ce module fait partie du projet **EducationIA_Django** développé dans le cadre d'un projet e-learning avec Django.

---

## 👨‍💻 Architecture Technique

### Stack Technologique
- **Backend** : Django 4.2
- **Base de données** : SQLite (par défaut)
- **Extraction PDF** : PyPDF2
- **NLP** : Algorithmes personnalisés (regex, TF-IDF)
- **Frontend** : HTML/CSS/Bootstrap + JavaScript

### Workflow de Traitement

```
Document uploadé
     ↓
Extraction de texte (si PDF)
     ↓
Analyse NLP
  ├─ Extraction de concepts
  ├─ Identification de définitions
  └─ Détection de relations
     ↓
Génération d'exercices
  ├─ QCM (avec distracteurs)
  ├─ Vrai/Faux (avec variations)
  └─ Texte à trous (mots-clés)
     ↓
Calcul de qualité
     ↓
Sauvegarde en base
     ↓
Validation enseignant
     ↓
Création de tests
     ↓
Export vers évaluation
```

---

## 🎓 Exemples de Requêtes API (optionnel)

Si vous activez l'API REST (DRF), voici des exemples :

### Lister les documents
```bash
GET /api/generator/documents/
```

### Créer un document
```bash
POST /api/generator/documents/
{
  "title": "Cours de physique",
  "content": "...",
  "subject": "Physique"
}
```

### Générer des exercices
```bash
POST /api/generator/documents/{id}/generate/
{
  "num_exercises": 15,
  "mcq_percentage": 60
}
```

---

**🎉 Bonne utilisation du Générateur d'Exercices IA ! 🚀**
