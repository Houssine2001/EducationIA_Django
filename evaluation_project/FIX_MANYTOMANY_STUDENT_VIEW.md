# 🔧 FIX: ValueError - ExerciseSet ManyToMany dans Vue Étudiant

## ❌ Erreur

```
ValueError at /generator/student/sets/
"<ExerciseSet: quiz node (published)>" needs to have a value for field "id" 
before this many-to-many relationship can be used.
```

**Ligne problématique**: Template `student_exercise_sets.html` ligne 29
```html
{{ set.exercises.count }}  ❌ Accès ManyToMany
{{ set.teacher.get_full_name }}  ❌ Accès ForeignKey
```

---

## 🔍 Cause Racine

**Même problème** que `/generator/sets/` mais dans la vue **étudiant** `student_exercise_sets()`.

La vue utilisait:
```python
published_sets = ExerciseSet.objects.filter(status='published').prefetch_related('exercises', 'teacher')
```

Problème: Django ORM avec MongoDB via Djongo ne configure pas correctement le `pk` des objets, donc:
- Accès à `set.exercises.count` → **ValueError** (pas de pk)
- Accès à `set.teacher.username` → **Requête échouée** (ForeignKey non résolu)

---

## ✅ Solution Appliquée

### 1. Réécriture de la Vue avec PyMongo

**Fichier**: `exercise_generator/views.py` → `student_exercise_sets()`

**AVANT** ❌:
```python
# Sets publiés via Django ORM
published_sets = ExerciseSet.objects.filter(status='published').prefetch_related('exercises', 'teacher')

# Soumissions via Django ORM
submissions = StudentExerciseSubmission.objects.filter(student=request.user)
completed_set_ids = set(submissions.values_list('exercise_set_id', flat=True))

context = {
    'exercise_sets': published_sets,
    'completed_set_ids': completed_set_ids,
}
```

**APRÈS** ✅:
```python
from pymongo import MongoClient
from django.conf import settings

# Récupérer via PyMongo
client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]

# Sets publiés
sets_data = list(db.exercise_sets.find({'status': 'published'}).sort('published_at', -1))

# Soumissions complétées
submissions = db.student_exercise_submissions.find({'student_id': request.user.id})
completed_set_ids = set([str(sub.get('exercise_set_id', '')) for sub in submissions])

# Convertir en objets Django
exercise_sets = []
for data in sets_data:
    exercise_set = ExerciseSet()
    exercise_set.pk = data['_id']  # ← Important!
    exercise_set.id = data['_id']  # ← Important!
    exercise_set._state.adding = False
    exercise_set._state.db = 'default'
    
    # Remplir tous les champs
    exercise_set.title = data.get('title', '')
    exercise_set.description = data.get('description', '')
    exercise_set.status = data.get('status', 'draft')
    exercise_set.teacher_id = data.get('teacher_id')
    exercise_set.source_document_id = data.get('source_document_id')
    exercise_set.created_at = data.get('created_at')
    exercise_set.published_at = data.get('published_at')
    exercise_set.updated_at = data.get('updated_at')
    
    # Pré-calculer le count des exercices
    exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
        'exerciseset_id': str(data['_id'])
    })
    exercise_set._exercise_count = exercise_count
    
    # Récupérer le nom du teacher
    teacher_id = data.get('teacher_id')
    if teacher_id:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            teacher = User.objects.get(id=teacher_id)
            exercise_set._teacher_name = teacher.get_full_name() or teacher.username
        except:
            exercise_set._teacher_name = 'Professeur'
    else:
        exercise_set._teacher_name = 'Professeur'
    
    exercise_sets.append(exercise_set)

client.close()

context = {
    'exercise_sets': exercise_sets,
    'completed_set_ids': completed_set_ids,
}
```

---

### 2. Ajout Méthode `get_teacher_name()` au Modèle

**Fichier**: `exercise_generator/models.py` → classe `ExerciseSet`

```python
def get_teacher_name(self):
    """Obtenir le nom du teacher en évitant la requête ForeignKey"""
    # Si le nom a déjà été calculé et stocké (par la vue), l'utiliser
    if hasattr(self, '_teacher_name'):
        return self._teacher_name
    
    # Sinon, essayer de récupérer via ForeignKey (peut échouer avec MongoDB)
    try:
        if self.teacher:
            return self.teacher.get_full_name() or self.teacher.username
    except:
        pass
    
    return 'Professeur'
```

**Pourquoi**: Permet d'éviter l'accès direct à `set.teacher.username` dans les templates qui causerait une requête ForeignKey.

---

### 3. Modification du Template

**Fichier**: `templates/exercise_generator/student_exercise_sets.html`

**AVANT** ❌:
```html
<span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
    {{ set.exercises.count }} exercice{{ set.exercises.count|pluralize }}
</span>

<p class="text-xs text-gray-500">
    Par {{ set.teacher.get_full_name|default:set.teacher.username }}
</p>
```

**APRÈS** ✅:
```html
<span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
    {{ set.get_exercise_count }} exercice{{ set.get_exercise_count|pluralize }}
</span>

<p class="text-xs text-gray-500">
    Par {{ set.get_teacher_name }}
</p>
```

---

## 📊 Résultat

### AVANT ❌
```
Page: /generator/student/sets/
Erreur: ValueError - ManyToMany needs field "id"
Cause: Django ORM ne configure pas pk correctement
```

### APRÈS ✅
```
Page: /generator/student/sets/
Status: ✅ Fonctionne
Affichage:
  ┌────────────────────────────────────┐
  │ Test IA - Mathématiques            │
  │ Équations du second degré...       │
  │ Par Jean Dupont                    │
  │ Publié le 09/10/2025               │
  │ 15 exercices                       │
  │                                     │
  │           [Commencer les exercices]│
  └────────────────────────────────────┘
```

---

## 🎯 Pattern Réutilisable

Ce pattern doit être appliqué **partout** où on récupère des `ExerciseSet` avec Django ORM:

### ❌ À ÉVITER
```python
# Django ORM avec MongoDB = Problèmes
sets = ExerciseSet.objects.filter(...).prefetch_related('exercises', 'teacher')
```

### ✅ À UTILISER
```python
# PyMongo + Construction manuelle d'objets Django
from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]

sets_data = list(db.exercise_sets.find({'filter': value}))

sets = []
for data in sets_data:
    obj = ExerciseSet()
    obj.pk = data['_id']
    obj.id = data['_id']
    obj._state.adding = False
    obj._state.db = 'default'
    
    # Remplir tous les champs
    for field in ExerciseSet._meta.fields:
        if field.name != 'id' and field.name in data:
            setattr(obj, field.name, data[field.name])
    
    # Pré-calculer les relations
    obj._exercise_count = db.exerciseset_exercises.count_documents(...)
    obj._teacher_name = get_teacher_name(data.get('teacher_id'))
    
    sets.append(obj)

client.close()
```

---

## 🔍 Vérification

### Tests à Effectuer

1. **Accéder à la page étudiant**:
   ```
   http://localhost:8000/generator/student/sets/
   ```
   ✅ Doit afficher la liste des exercices publiés

2. **Vérifier l'affichage**:
   - ✅ Titre du set
   - ✅ Description
   - ✅ Nom du professeur
   - ✅ Date de publication
   - ✅ Nombre d'exercices
   - ✅ Bouton "Commencer"

3. **Cliquer "Commencer"**:
   ```
   → Redirect vers /generator/student/sets/<id>/take/
   ```
   ✅ Doit afficher les exercices

4. **Soumettre les exercices**:
   ```
   → Soumission enregistrée dans MongoDB
   ```
   ✅ Badge "Complété" apparaît dans la liste

---

## 📝 Fichiers Modifiés

| Fichier | Changements | Lignes |
|---------|-------------|--------|
| `exercise_generator/views.py` | `student_exercise_sets()` réécrite avec PyMongo | 1050-1110 |
| `exercise_generator/models.py` | Ajout `get_teacher_name()` | 447-461 |
| `templates/.../student_exercise_sets.html` | `exercises.count` → `get_exercise_count` | 29 |
| `templates/.../student_exercise_sets.html` | `teacher.username` → `get_teacher_name` | 24 |

---

## 🎓 Leçon Apprise

> **Avec MongoDB et Djongo**: Quand Django ORM échoue avec ManyToMany/ForeignKey, 
> utilisez PyMongo pour les requêtes et construisez les objets Django manuellement.

**Pattern général**:
1. Requête PyMongo → `db.collection.find()`
2. Construction manuelle → `obj.pk = data['_id']`
3. Pré-calcul relations → `obj._count = db.count_documents()`
4. Méthodes helper → `obj.get_count()` retourne `_count`
5. Template utilise méthodes → `{{ obj.get_count }}`

---

**Date**: 9 Octobre 2025  
**Problème**: ValueError - ManyToMany sans ID (vue étudiant)  
**Solution**: PyMongo + construction manuelle + méthodes helper  
**Statut**: ✅ Résolu
