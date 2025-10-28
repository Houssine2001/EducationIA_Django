# 🔧 Correction des IDs des Resources

## Problème
Les resources créées dans MongoDB (Docker) n'ont pas de champ `id` entier, seulement `_id` (ObjectId).
Les URLs Django attendent un entier : `resources/<int:resource_id>/`

## Solution

### 1. Dans Docker, exécuter la commande de correction

```bash
# Entrer dans le container
docker exec -it educationia_django-web-1 bash

# Exécuter la commande Django
python manage.py fix_resource_ids
```

### 2. Vérifier que ça fonctionne

```bash
# Dans le container Django shell
python manage.py shell

# Vérifier les IDs
from resources.models import Resource
Resource.objects.filter(id__isnull=True).count()  # Devrait être 0

# Afficher toutes les resources avec leurs IDs
for r in Resource.objects.all()[:5]:
    print(f"ID: {r.id} | Titre: {r.title}")
```

## Changements appliqués

### 1. Modèle `Resource` (`resources/models.py`)
- ✅ Ajout d'un champ `id` explicite : `id = models.AutoField(primary_key=True)`
- ✅ Méthode `save()` modifiée pour auto-générer un ID si manquant

### 2. Commande Django (`resources/management/commands/fix_resource_ids.py`)
- ✅ Commande Django pour attribuer des IDs aux resources existantes
- ✅ Usage : `python manage.py fix_resource_ids`

### 3. Template (`dashboard.html`)
- ✅ Utilise `resource.id` qui sera toujours défini

## Prévention

Désormais, chaque nouvelle resource créée aura automatiquement un ID entier généré dans la méthode `save()`.

## Alternative rapide (si la commande ne fonctionne pas)

```bash
# Dans le container
python manage.py shell

# Exécuter ce code
from resources.models import Resource
resources = Resource.objects.filter(id__isnull=True)
max_id = Resource.objects.filter(id__isnull=False).order_by('-id').first()
next_id = (max_id.id + 1) if max_id else 1

for r in resources:
    r.id = next_id
    r.save(update_fields=['id'])
    print(f"✓ {r.title} -> ID {next_id}")
    next_id += 1
```
