# 🔧 Corrections Djongo: Problèmes de Requêtes SQL

## ❌ Problème: DatabaseError avec WHERE NOT

```
DatabaseError at /teacher/students/
'NoneType' object has no attribute 'negate'
FAILED SQL: ... WHERE NOT "auth_user"."is_staff" ...
```

### Cause
Djongo (version 1.3.6) a des difficultés à parser certaines requêtes SQL complexes, notamment:
- `WHERE NOT` (négation)
- `.exclude()` dans certains cas
- Jointures avec conditions négatives

## ✅ Solutions Appliquées

### 1. **Remplacement de `user__is_staff=False`**
**Fichier**: `evaluation/views.py` - fonction `students_list()`

#### Avant (❌ Causait l'erreur)
```python
students_profiles = UserProfile.objects.filter(
    user__is_staff=False  # Djongo génère WHERE NOT → erreur
).select_related('user')
```

#### Après (✅ Fonctionne)
```python
students_profiles = UserProfile.objects.filter(
    role='student'  # Utilise un champ direct au lieu d'une négation
).select_related('user')
```

**Pourquoi ça marche?**
- Pas de négation SQL (`WHERE NOT`)
- Requête simple sur un champ du modèle UserProfile
- Compatible avec le parser Djongo

### 2. **Remplacement de `.exclude()`**
**Fichier**: `evaluation/analytics.py` - classe `StudentAnalytics`

#### Avant (❌ Potentiellement problématique)
```python
submissions = Submission.objects.filter(
    student=self.user,
    status='completed'
).exclude(submitted_at__isnull=True)  # exclude() → WHERE NOT
```

#### Après (✅ Fonctionne)
```python
submissions = Submission.objects.filter(
    student=self.user,
    status='completed',
    submitted_at__isnull=False  # Filtre positif au lieu de négation
)
```

## 📋 Règles pour Éviter les Erreurs Djongo

### ❌ À ÉVITER

```python
# 1. Négations sur des champs de relations
.filter(user__is_staff=False)
.filter(user__is_active=False)

# 2. exclude() avec des conditions complexes
.exclude(field__isnull=True)
.exclude(relation__field=value)

# 3. Négations multiples
.exclude(a=True).exclude(b=False)
```

### ✅ À UTILISER

```python
# 1. Filtres positifs sur le modèle principal
.filter(role='student')  # Au lieu de user__is_staff=False
.filter(is_active=True)   # Au lieu de is_active__ne=False

# 2. Inversions de conditions isnull
.filter(field__isnull=False)  # Au lieu de exclude(field__isnull=True)

# 3. Filtrage en Python si nécessaire
all_profiles = UserProfile.objects.all()
students = [p for p in all_profiles if not p.user.is_staff]
```

## 🔍 Patterns de Remplacement

| ❌ Problématique | ✅ Solution |
|-----------------|------------|
| `user__is_staff=False` | `role='student'` |
| `.exclude(field__isnull=True)` | `.filter(field__isnull=False)` |
| `.exclude(status='draft')` | `.filter(status__in=['published', 'active'])` |
| `user__is_active=False` | Ajouter un champ `is_active` direct |

## 🚀 Comment Détecter ces Problèmes

### 1. Regarder les Logs Django
```
FAILED SQL: SELECT ... WHERE NOT ...
'NoneType' object has no attribute 'negate'
```

### 2. Chercher dans le Code
```bash
# Rechercher les patterns problématiques
grep -r "\.exclude(" *.py
grep -r "=False" *.py | grep "filter"
grep -r "__ne=" *.py
```

### 3. Tester les Requêtes
```python
# Dans le shell Django
python manage.py shell

# Tester la requête
from evaluation.models import UserProfile
students = UserProfile.objects.filter(user__is_staff=False)
list(students)  # Si erreur → problème Djongo
```

## 📊 Impact des Corrections

### Avant
```
❌ DatabaseError sur /teacher/students/
❌ Requêtes avec WHERE NOT échouent
❌ .exclude() cause des erreurs
```

### Après
```
✅ Page /teacher/students/ fonctionne
✅ Toutes les requêtes utilisent des filtres positifs
✅ Compatible avec Djongo 1.3.6
```

## 🎯 Recommandations Générales

### 1. **Conception du Modèle**
Ajoutez des champs directs au lieu de dépendre de relations:

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, ...)
    role = models.CharField(...)  # 'student', 'teacher'
    
    # Au lieu de toujours vérifier user.is_staff
    # Utilisez profile.role == 'student'
```

### 2. **Requêtes Simples**
Préférez les requêtes simples aux jointures complexes:

```python
# ✅ BON
profiles = UserProfile.objects.filter(role='student')

# ❌ À ÉVITER
profiles = UserProfile.objects.filter(
    user__is_staff=False,
    user__is_active=True
).exclude(user__groups__name='admin')
```

### 3. **Filtrage Python**
Pour les cas complexes, récupérez les données puis filtrez en Python:

```python
# Récupérer toutes les données
all_profiles = list(UserProfile.objects.all())

# Filtrer en Python
students = [
    p for p in all_profiles 
    if not p.user.is_staff and p.user.is_active
]
```

## 📝 Fichiers Modifiés

1. **`evaluation/views.py`**
   - Fonction `students_list()` ligne 1254
   - Changement: `user__is_staff=False` → `role='student'`

2. **`evaluation/analytics.py`**
   - Classe `StudentAnalytics` ligne 147
   - Changement: `.exclude(submitted_at__isnull=True)` → `.filter(submitted_at__isnull=False)`

## ⚠️ Notes sur Djongo

Djongo est un wrapper qui traduit les requêtes SQL de Django ORM en requêtes MongoDB. Il a des limitations:

- **Version 1.3.6** : Ancienne, bugs connus avec WHERE NOT
- **Alternative** : Utiliser PyMongo directement pour les requêtes complexes
- **Migration** : Considérer MongoDB Motor ou utiliser SQLite pour l'authentification

## 🔗 Ressources

- [Issue Djongo - WHERE NOT](https://github.com/nesdis/djongo/issues/...)
- [Django QuerySet exclude()](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#exclude)
- Documentation MongoDB: Éviter les anti-patterns

---

**Conclusion**: Avec Djongo, privilégiez toujours les **filtres positifs** (`field=value`) aux **négations** (`field__ne=value`, `exclude()`).
