# 🔧 Correction: RecursionError dans __str__() avec MongoDB

## ❌ Problème

```
RecursionError at /generator/sets/
maximum recursion depth exceeded
Exception Location: django/db/models/fields/related_descriptors.py, line 588, in __get__
```

### Cause Racine

La méthode `__str__()` de certains modèles tentait d'accéder à des relations ManyToMany ou ForeignKey, ce qui déclenchait:

1. Django essaie de représenter l'objet → appelle `__str__()`
2. `__str__()` essaie d'accéder à `self.exercises.count()`
3. Django ORM a besoin de représenter l'objet pour l'erreur → appelle `__str__()`
4. **Boucle infinie** → RecursionError

### Exemple de Code Problématique

```python
class ExerciseSet(MongoDBCompatibleModel):
    exercises = models.ManyToManyField(GeneratedExercise, ...)
    
    def __str__(self):
        # ❌ PROBLÈME: Accède à une relation ManyToMany
        return f"{self.title} - {self.exercises.count()} exercices ({self.status})"
```

## ✅ Solution

### Principe
**Ne JAMAIS accéder à des relations dans `__str__()`** car cela peut déclencher des requêtes Django ORM.

### Corrections Appliquées

#### 1. ExerciseSet
```python
# AVANT (❌)
def __str__(self):
    return f"{self.title} - {self.exercises.count()} exercices ({self.status})"

# APRÈS (✅)
def __str__(self):
    # Éviter self.exercises.count() car ça cause une récursion infinie
    # avec notre système MongoDB personnalisé
    return f"{self.title} ({self.status})"
```

#### 2. GeneratedTest
```python
# AVANT (❌)
def __str__(self):
    return f"{self.title} - {self.exercises.count()} exercices"

# APRÈS (✅)
def __str__(self):
    # Éviter self.exercises.count() pour éviter la récursion
    return f"{self.title}"
```

#### 3. StudentExerciseSubmission
```python
# AVANT (❌)
def __str__(self):
    return f"{self.student.username} - {self.exercise_set.title} ({self.score}%)"

# APRÈS (✅)
def __str__(self):
    # Éviter les requêtes qui peuvent causer la récursion
    try:
        student_name = self.student.username if hasattr(self, 'student') else 'Unknown'
        set_title = self.exercise_set.title if hasattr(self, 'exercise_set') else 'Unknown'
        return f"{student_name} - {set_title} ({self.score}%)"
    except:
        return f"Submission {self.pk}"
```

## 📋 Règles pour __str__() avec MongoDB/Djongo

### ❌ À ÉVITER

```python
# 1. Accès à ManyToMany
def __str__(self):
    return f"{self.title} - {self.related.count()}"

# 2. Accès à ForeignKey sans protection
def __str__(self):
    return f"{self.related_object.name}"

# 3. Requêtes complexes
def __str__(self):
    return f"{self.title} - {self.related.filter(...).count()}"
```

### ✅ À FAIRE

```python
# 1. Utiliser seulement les champs directs
def __str__(self):
    return f"{self.title} ({self.status})"

# 2. Utiliser try/except pour les ForeignKey si nécessaire
def __str__(self):
    try:
        name = self.fk_object.name if hasattr(self, 'fk_object') else 'Unknown'
        return f"{self.title} - {name}"
    except:
        return f"{self.title}"

# 3. Fallback sur pk si problème
def __str__(self):
    try:
        return f"{self.title}"
    except:
        return f"Object {self.pk}"
```

## 🎯 Patterns Sûrs

### Pattern 1: Champs Directs Uniquement
```python
class MyModel(MongoDBCompatibleModel):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.title} ({self.status})"  # ✅ Safe
```

### Pattern 2: Try/Except pour Relations
```python
class MyModel(MongoDBCompatibleModel):
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, ...)
    
    def __str__(self):
        try:
            owner_name = self.owner.username if self.owner else 'No owner'
            return f"{self.title} - {owner_name}"
        except:
            return self.title  # ✅ Fallback safe
```

### Pattern 3: Propriété Séparée pour l'Affichage
```python
class ExerciseSet(MongoDBCompatibleModel):
    title = models.CharField(max_length=200)
    exercises = models.ManyToManyField(GeneratedExercise)
    
    def __str__(self):
        return self.title  # ✅ Simple et sûr
    
    @property
    def display_name(self):
        # ✅ Utilisé dans les templates/vues quand on a déjà les données
        return f"{self.title} - {self.exercises.count()} exercices"
```

## 📊 Résultats

### Avant
```
❌ RecursionError lors de l'accès à /generator/sets/
❌ Impossible d'afficher la liste des ExerciseSets
❌ Erreur dans les templates lors du rendu
```

### Après
```
✅ Page /generator/sets/ s'affiche correctement
✅ Pas de récursion dans __str__()
✅ Représentation string simple et rapide
```

## 🔍 Debugging

### Comment Identifier le Problème

1. **Regarder la Stack Trace**
```python
# Si vous voyez cette répétition:
exercise_generator/models.py, line 436, in __str__
    return f"{self.title} - {self.exercises.count()} exercices"
django/db/models/fields/related_descriptors.py, line 588, in __get__
exercise_generator/models.py, line 436, in __str__  # ← Répété!
```

2. **Tester dans le Shell**
```python
python manage.py shell

from exercise_generator.models import ExerciseSet
obj = ExerciseSet.objects.first()
print(obj)  # Si RecursionError → problème dans __str__()
```

3. **Vérifier les Accès à Relations**
```python
# Dans __str__(), chercher:
- self.related_field.count()
- self.foreign_key.attribute
- self.many_to_many.all()
```

## ⚠️ Recommandations Générales

### Pour Tous les Modèles Django avec MongoDB

1. **Gardez __str__() Simple**
   - Utilisez seulement des champs directs (CharField, IntegerField, etc.)
   - Pas de `.count()`, `.all()`, `.filter()`

2. **Créez des Propriétés pour l'Affichage Complexe**
   - Utilisez `@property` pour les informations qui nécessitent des requêtes
   - Appelez ces propriétés explicitement dans les vues/templates

3. **Utilisez try/except pour les ForeignKey**
   - Protection contre les objets non chargés
   - Fallback sur une valeur simple

4. **Testez Toujours**
   - Testez `print(obj)` dans le shell après chaque modification de `__str__()`
   - Vérifiez que ça n'appelle pas de requêtes DB

## 📝 Fichiers Modifiés

**exercise_generator/models.py**
- Ligne 436: `ExerciseSet.__str__()` - Supprimé `.exercises.count()`
- Ligne 337: `GeneratedTest.__str__()` - Supprimé `.exercises.count()`
- Ligne 493: `StudentExerciseSubmission.__str__()` - Ajouté try/except

## 🎓 Leçon Apprise

> **Règle d'Or**: Les méthodes `__str__()` doivent être **instantanées** et **sans effets de bord**.
> Avec MongoDB/Djongo, évitez TOUT accès à des relations pour prévenir les récursions infinies.

---

**Date**: 9 Octobre 2025  
**Problème**: RecursionError dans __str__()  
**Solution**: Simplification des __str__() pour éviter les accès aux relations  
**Statut**: ✅ Résolu
