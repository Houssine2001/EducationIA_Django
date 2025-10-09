# 🚀 GUIDE RAPIDE - EducationIA MongoDB

## 📋 COMMANDES ESSENTIELLES

### Démarrer le Système

```bash
# 1. Démarrer MongoDB (si pas déjà actif)
mongod --dbpath "C:\data\db"

# 2. Démarrer Django
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python manage.py runserver
```

### Comptes de Test

| Username | Password | Role |
|----------|----------|------|
| prof1 | pass123 | Professeur |
| etudiant1 | password123 | Étudiant |
| etudiant2 | password123 | Étudiant |
| etudiant3 | password123 | Étudiant |

### URLs Importantes

```
Page d'accueil: http://127.0.0.1:8000/
Login: http://127.0.0.1:8000/evaluation/login/
Dashboard: http://127.0.0.1:8000/evaluation/dashboard/
Tests: http://127.0.0.1:8000/evaluation/tests/
```

---

## 🧪 TESTS RAPIDES

### Test 1: Vérifier MongoDB
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python -c "import pymongo; client = pymongo.MongoClient('localhost', 27017); db = client['django_education']; print(f'Tests: {db.evaluation_test.count_documents({})}'); print(f'Users: {db.auth_user.count_documents({})}');"
```

**Résultat attendu:**
```
Tests: 50
Users: 4
```

### Test 2: Vérifier Authentification
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python test_final_quick.py
```

**Résultat attendu:**
```
1. Prof1:
   OK - ID:32, Role:teacher

2. Etudiant1:
   OK - ID:42, Role:student, XP:1654

3. Tests:
   Total:50, Manual:50, IA:0
```

### Test 3: Vérifier IDs MongoDB
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python -c "import pymongo; client = pymongo.MongoClient('localhost', 27017); db = client['django_education']; user = db.auth_user.find_one({'username': 'prof1'}); print(f'_id={user[\"_id\"]}, id={user.get(\"id\", \"MISSING\")}')"
```

**Résultat attendu:**
```
_id=32, id=32
```

---

## 🔧 SCRIPTS DE RÉPARATION

### Réparer les IDs MongoDB
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python fix_mongodb_ids.py
```

### Réparer les Roles
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python fix_roles.py
```

### Test Système Complet
```bash
cd C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project
python test_systeme_complet.py
```

---

## ⚠️ EN CAS DE PROBLÈME

### Problème: Serveur ne démarre pas
```bash
# Vérifier que MongoDB est actif
mongosh
# Si erreur de connexion, démarrer MongoDB:
mongod --dbpath "C:\data\db"
```

### Problème: "Cannot use MongoClient after close"
```bash
# Vérifier settings.py:
# DATABASES['default']['CONN_MAX_AGE'] = None
# DATABASES['default']['CLIENT']['socketTimeoutMS'] = None
```

### Problème: Authentification échoue
```bash
# 1. Vérifier les mots de passe
python test_auth_prof1.py

# 2. Vérifier que le middleware est actif
# Le log doit montrer:
# ✅ Signal update_last_login désactivé (Fix Djongo)
```

### Problème: Test.objects.all() retourne 0
```bash
# Vérifier les noms de tables dans models.py
# Doivent correspondre aux collections MongoDB:
# - evaluation_test
# - evaluation_userprofile
# - evaluation_question
# - evaluation_submission
# - evaluation_result
```

---

## 📊 STRUCTURE MONGODB

### Collections Principales

```
django_education/
├── auth_user (4 docs)
├── evaluation_userprofile (4 docs)
├── evaluation_test (50 docs)
├── evaluation_question (592 docs)
├── evaluation_submission (122 docs)
└── evaluation_result (122 docs)
```

### Exemple de Document Test

```json
{
  "_id": 147,
  "id": 147,
  "title": "Test Géographie #50",
  "description": "Test de niveau intermédiaire en Géographie",
  "subject": "Géographie",
  "topic": "Chapitre 7",
  "source_type": "manual",
  "difficulty": "hard",
  "duration": 30,
  "passing_score": 70.0,
  "total_points": 100.0,
  "status": "published",
  "created_at": ISODate("2025-10-06T19:19:35.338Z")
}
```

---

## 🎯 FONCTIONNALITÉS VALIDÉES

- ✅ Connexion MongoDB stable
- ✅ Authentification prof1 / pass123
- ✅ Authentification etudiant1 / password123
- ✅ Requêtes ORM (Test.objects.all(), filter, etc.)
- ✅ Relations ForeignKey (user.profile)
- ✅ Affichage badges 👔 Manuel / 🤖 IA
- ✅ Dashboard XP et niveaux
- ✅ Middleware Djongo fix actif

## 🔄 FONCTIONNALITÉS À TESTER

- ⏳ Login via navigateur Web
- ⏳ Création de test manuel par professeur
- ⏳ Génération de test par IA
- ⏳ Passage de test par étudiant
- ⏳ Calcul automatique des lacunes/points forts
- ⏳ Recommandations IA personnalisées

---

## 📝 NOTES

### Middleware DjongoFix
Le middleware `DjongoFixMiddleware` **DOIT** être le **PREMIER** dans `MIDDLEWARE` de `settings.py`:

```python
MIDDLEWARE = [
    'backend.djongo_fix_middleware.DjongoFixMiddleware',  # ⭐ PREMIER!
    'django.middleware.security.SecurityMiddleware',
    # ... reste des middlewares
]
```

### Champ ID MongoDB
Tous les documents doivent avoir `id` = `_id`:

```python
# Si id manquant, exécuter:
python fix_mongodb_ids.py
```

### Logs Serveur
Le serveur doit afficher au démarrage:

```
✅ Signal update_last_login désactivé (Fix Djongo)
Starting development server at http://127.0.0.1:8000/
```

Si ce message n'apparaît pas, le middleware n'est pas actif!

---

**Date**: 9 Octobre 2025
**Version**: 1.0 MongoDB
**Status**: ✅ Opérationnel
