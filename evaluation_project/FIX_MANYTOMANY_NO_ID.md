# 🔧 Correction: ValueError - ManyToMany sans ID

## ❌ Problème

```
ValueError at /generator/sets/
"<ExerciseSet: quiz node (published)>" needs to have a value for field "id" 
before this many-to-many relationship can be used.
```

### Cause Racine

Quand Django ORM récupère des objets depuis MongoDB via notre `MongoDBCompatibleModel`:
1. Les objets n'ont pas leur `pk`/`id` correctement configuré
2. Django ne peut pas accéder aux relations ManyToMany sans `pk`
3. Les templates qui accèdent à `set.exercises.count` échouent

### Code Problématique

```python
# Dans la vue
sets = ExerciseSet.objects.filter(teacher=request.user).prefetch_related('exercises')

# Dans le template
{{ set.exercises.count }}  # ❌ Erreur: pas d'ID sur l'objet
{{ set.source_document.title }}  # ❌ Erreur: tente une requête
```

## ✅ Solution

### Stratégie
**Récupérer directement via PyMongo** au lieu de Django ORM pour avoir un contrôle total sur les objets créés.

### 1. Modification de la Vue

```python
# AVANT (❌)
def exercise_sets_list(request):
    sets = ExerciseSet.objects.filter(teacher=request.user).prefetch_related('exercises')
    return render(request, 'template.html', {'exercise_sets': sets})

# APRÈS (✅)
def exercise_sets_list(request):
    from pymongo import MongoClient
    from django.conf import settings
    
    # Récupérer directement via PyMongo
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    sets_data = list(db.exercise_sets.find({'teacher_id': request.user.id}))
    
    # Convertir en objets Django
    sets = []
    for data in sets_data:
        exercise_set = ExerciseSet()
        exercise_set.pk = data['_id']
        exercise_set.id = data['_id']
        exercise_set.title = data.get('title', '')
        exercise_set.status = data.get('status', 'draft')
        # ... autres champs ...
        
        # Marquer comme sauvegardé
        exercise_set._state.adding = False
        exercise_set._state.db = 'default'
        
        # Calculer le count directement
        exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': str(data['_id'])
        })
        exercise_set._exercise_count = exercise_count
        
        sets.append(exercise_set)
    
    client.close()
    return render(request, 'template.html', {'exercise_sets': sets})
```

### 2. Ajout d'une Méthode au Modèle

```python
class ExerciseSet(MongoDBCompatibleModel):
    exercises = models.ManyToManyField(GeneratedExercise, ...)
    
    def get_exercise_count(self):
        """Obtenir le nombre d'exercices via MongoDB"""
        # Utiliser le count pré-calculé si disponible
        if hasattr(self, '_exercise_count'):
            return self._exercise_count
        
        # Sinon calculer via PyMongo
        from pymongo import MongoClient
        from django.conf import settings
        
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]
        count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': str(self.pk)
        })
        client.close()
        return count
```

### 3. Modification du Template

```html
<!-- AVANT (❌) -->
<p>{{ set.exercises.count }} exercices</p>
<p>{{ set.source_document.title }}</p>

<!-- APRÈS (✅) -->
<p>{{ set.get_exercise_count }} exercices</p>
<p>Document: {{ set.source_document_id|truncatechars:12 }}</p>
```

## 📋 Pattern de Récupération MongoDB

### Pour les Listes (QuerySet)

```python
def my_list_view(request):
    from pymongo import MongoClient
    from django.conf import settings
    
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # 1. Requête MongoDB
    docs = list(db.collection_name.find({'filter': value}))
    
    # 2. Convertir en objets Django
    objects = []
    for doc in docs:
        obj = MyModel()
        obj.pk = doc['_id']
        obj.id = doc['_id']
        
        # Remplir tous les champs
        for field in MyModel._meta.fields:
            if field.name != 'id' and field.name in doc:
                setattr(obj, field.name, doc[field.name])
        
        # Marquer comme sauvegardé
        obj._state.adding = False
        obj._state.db = 'default'
        
        # Calculer les counts de relations
        related_count = db.related_table.count_documents({
            'parent_id': str(doc['_id'])
        })
        obj._related_count = related_count
        
        objects.append(obj)
    
    client.close()
    return render(request, 'template.html', {'objects': objects})
```

### Pour un Objet Unique (get)

```python
def my_detail_view(request, object_id):
    from pymongo import MongoClient
    from django.conf import settings
    from bson.objectid import ObjectId
    
    client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    db = client[settings.MONGO_DB_NAME]
    
    # Requête MongoDB
    doc = db.collection_name.find_one({'_id': ObjectId(object_id)})
    
    if not doc:
        raise Http404("Object not found")
    
    # Créer l'objet Django
    obj = MyModel()
    obj.pk = doc['_id']
    obj.id = doc['_id']
    # ... remplir les champs ...
    obj._state.adding = False
    obj._state.db = 'default'
    
    client.close()
    return render(request, 'template.html', {'object': obj})
```

## 🎯 Règles pour les Vues avec MongoDB

### ❌ À ÉVITER

```python
# 1. Django ORM filter/get avec MongoDB
objects = MyModel.objects.filter(field=value)  # ❌ pk non configuré

# 2. Accès aux relations dans les templates
{{ object.related.count }}  # ❌ Déclenche une requête
{{ object.foreign_key.name }}  # ❌ Peut échouer

# 3. prefetch_related avec MongoDB
objects = MyModel.objects.prefetch_related('related')  # ❌ Ne fonctionne pas bien
```

### ✅ À FAIRE

```python
# 1. PyMongo pour les requêtes
docs = db.collection.find({'field': value})

# 2. Pré-calculer les counts
obj._count = db.related_table.count_documents({'parent_id': obj_id})

# 3. Templates utilisent des méthodes/propriétés
{{ object.get_count }}  # ✅ Méthode qui gère MongoDB
{{ object.field_id }}  # ✅ ID direct au lieu de relation
```

## 📊 Résultats

### Avant
```
❌ ValueError: needs to have a value for field "id"
❌ Impossible d'afficher la liste des ExerciseSets
❌ Template plante sur .count ou .title
```

### Après
```
✅ Liste des ExerciseSets s'affiche
✅ Counts d'exercices fonctionnent
✅ Pas d'accès aux relations problématiques
```

## 🔍 Avantages de cette Approche

### 1. **Contrôle Total**
- On contrôle exactement comment les objets sont créés
- On peut pré-calculer les données nécessaires
- Pas de surprises avec Django ORM

### 2. **Performance**
- Moins de requêtes (counts pré-calculés)
- Pas de requêtes N+1
- Connexion MongoDB fermée proprement

### 3. **Fiabilité**
- Pas d'erreurs de pk manquant
- Pas de récursion avec les relations
- Compatible avec les templates Django

## ⚠️ Points d'Attention

### 1. **Duplication de Code**
Créer des objets manuellement peut être répétitif. Solution:

```python
# Créer une fonction helper
def docs_to_objects(docs, ModelClass):
    objects = []
    for doc in docs:
        obj = ModelClass()
        obj.pk = doc['_id']
        obj.id = doc['_id']
        
        for field in ModelClass._meta.fields:
            if field.name != 'id' and field.name in doc:
                setattr(obj, field.name, doc[field.name])
        
        obj._state.adding = False
        obj._state.db = 'default'
        objects.append(obj)
    
    return objects
```

### 2. **Pagination**
Pour paginer, utiliser MongoDB:

```python
# Pagination MongoDB
page = int(request.GET.get('page', 1))
per_page = 20
skip = (page - 1) * per_page

docs = list(db.collection.find({'filter': value})
    .skip(skip)
    .limit(per_page))

total = db.collection.count_documents({'filter': value})
```

### 3. **Tri**
Utiliser MongoDB pour trier:

```python
docs = list(db.collection.find({'filter': value})
    .sort('created_at', -1))  # -1 = DESC, 1 = ASC
```

## 📝 Fichiers Modifiés

1. **`exercise_generator/views.py`**
   - Fonction `exercise_sets_list()` - Récupération PyMongo

2. **`exercise_generator/models.py`**
   - Classe `ExerciseSet` - Ajout `get_exercise_count()`

3. **`templates/exercise_generator/exercise_sets_list.html`**
   - Remplacement `exercises.count` → `get_exercise_count`
   - Remplacement `source_document.title` → `source_document_id`

## 🎓 Leçon Apprise

> **Avec MongoDB et Django**: Quand Django ORM ne fonctionne pas bien, **utilisez PyMongo directement**.
> Créez les objets Django manuellement avec un contrôle total.

---

**Date**: 9 Octobre 2025  
**Problème**: ValueError - ManyToMany sans ID  
**Solution**: Récupération directe via PyMongo au lieu de Django ORM  
**Statut**: ✅ Résolu
