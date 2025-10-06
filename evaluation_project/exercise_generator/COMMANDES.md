# 🚀 COMMANDES DE DÉMARRAGE RAPIDE

## Installation Initiale (À faire une seule fois)

```powershell
# 1. Installer PyPDF2
pip install PyPDF2

# 2. Créer les tables de base de données
python manage.py makemigrations exercise_generator
python manage.py migrate

# 3. Créer un superutilisateur (si pas déjà fait)
python manage.py createsuperuser
```

## Démarrage Normal

```powershell
# Lancer le serveur Django
python manage.py runserver
```

Puis ouvrez dans votre navigateur :
- **http://127.0.0.1:8000/generator/**

## Ou Utiliser le Script Automatique

```powershell
# Tout en un (Windows PowerShell)
.\start_generator.ps1
```

---

## URLs Importantes

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | http://127.0.0.1:8000/generator/ | Tableau de bord principal |
| Génération Rapide | http://127.0.0.1:8000/generator/quick-generate/ | Génération instantanée |
| Nouveau Document | http://127.0.0.1:8000/generator/documents/new/ | Uploader un document |
| Liste Exercices | http://127.0.0.1:8000/generator/exercises/ | Tous les exercices |
| Configuration | http://127.0.0.1:8000/generator/config/ | Paramètres |
| Admin Django | http://127.0.0.1:8000/admin/ | Interface d'administration |

---

## Test Rapide (Copier-Coller)

### 1. Accédez à la génération rapide
http://127.0.0.1:8000/generator/quick-generate/

### 2. Collez ce texte :

```
La photosynthèse est le processus par lequel les plantes vertes transforment 
la lumière solaire en énergie chimique. Ce processus se déroule dans les 
chloroplastes, organites spécialisés présents dans les cellules végétales. 
La photosynthèse nécessite trois éléments essentiels : l'eau, le dioxyde de 
carbone (CO2) et la lumière. Les produits de cette réaction sont le glucose, 
qui sert de source d'énergie pour la plante, et l'oxygène, qui est libéré 
dans l'atmosphère. Ce processus est vital pour la vie sur Terre car il 
produit l'oxygène que nous respirons et constitue la base de la chaîne 
alimentaire. Les plantes utilisent la chlorophylle, un pigment vert, pour 
capter l'énergie lumineuse du soleil.
```

### 3. Remplissez :
- **Matière** : Biologie
- **Nombre d'exercices** : 10

### 4. Cliquez sur "Générer"

✅ **Résultat** : 10 exercices générés en quelques secondes !

---

## Commandes Utiles

### Vérification
```powershell
# Vérifier l'installation du module
python manage.py check exercise_generator

# Voir les migrations
python manage.py showmigrations exercise_generator

# Vérifier si PyPDF2 est installé
python -c "import PyPDF2; print('✅ PyPDF2 OK')"
```

### Base de Données
```powershell
# Créer les tables
python manage.py migrate

# Backup de la base
python manage.py dumpdata exercise_generator > backup_generator.json

# Restaurer le backup
python manage.py loaddata backup_generator.json

# Réinitialiser les migrations (ATTENTION : perte de données)
python manage.py migrate exercise_generator zero
python manage.py migrate exercise_generator
```

### Shell Django
```powershell
python manage.py shell
```

Puis dans le shell :
```python
# Test de génération
from exercise_generator.services import ExerciseGenerationService
from exercise_generator.models import CourseDocument
from django.contrib.auth.models import User

# Créer un document de test
teacher = User.objects.first()
doc = CourseDocument.objects.create(
    title="Test Photosynthèse",
    content="La photosynthèse est le processus...",  # Votre texte complet ici
    subject="Biologie",
    teacher=teacher
)

# Générer les exercices
service = ExerciseGenerationService()
result = service.process_document(doc)

# Afficher les résultats
print(f"✅ {len(result['exercises'])} exercices générés!")
for ex in result['exercises'][:3]:
    print(f"- {ex['type']}: {ex['question'][:50]}...")
```

---

## Résolution de Problèmes

### Erreur : "No module named 'exercise_generator'"
```powershell
# Vérifiez que l'app est dans INSTALLED_APPS
python manage.py check
```

### Erreur : "PyPDF2 not found"
```powershell
pip install PyPDF2
```

### Erreur : "Table doesn't exist"
```powershell
python manage.py migrate exercise_generator
```

### Erreur 404 sur /generator/
```powershell
# Vérifiez que les URLs sont incluses
python manage.py shell
>>> from django.urls import get_resolver
>>> print(get_resolver().url_patterns)
```

### Aucun exercice généré
- Le texte doit contenir au moins **50 mots**
- Le texte doit être en **français**
- Consultez les **logs** du document dans l'admin

---

## Workflow Complet

```
1. Démarrer le serveur
   python manage.py runserver

2. Se connecter
   http://127.0.0.1:8000/admin/

3. Accéder au générateur
   http://127.0.0.1:8000/generator/

4. Créer un document
   - Nouveau Document
   - Remplir le formulaire
   - Coller le texte ou uploader PDF

5. Attendre la génération (5-10 secondes)

6. Consulter les exercices générés

7. Valider les exercices
   - Marquer comme "Validé"

8. Créer un test
   - Sélectionner les exercices
   - Donner un titre

9. Exporter vers l'évaluation
   - Bouton "Exporter"

10. ✅ Test disponible pour les étudiants !
```

---

## Scripts de Maintenance

### Nettoyer les exercices de faible qualité
```python
# Dans le shell Django
from exercise_generator.models import GeneratedExercise

# Supprimer les exercices de score < 0.5
low_quality = GeneratedExercise.objects.filter(quality_score__lt=0.5)
count = low_quality.count()
low_quality.delete()
print(f"✅ {count} exercices supprimés")
```

### Statistiques globales
```python
from exercise_generator.models import CourseDocument, GeneratedExercise

print(f"Documents : {CourseDocument.objects.count()}")
print(f"Exercices : {GeneratedExercise.objects.count()}")
print(f"Validés : {GeneratedExercise.objects.filter(status='validated').count()}")
print(f"QCM : {GeneratedExercise.objects.filter(exercise_type='mcq').count()}")
print(f"Vrai/Faux : {GeneratedExercise.objects.filter(exercise_type='true_false').count()}")
```

---

## Fichiers de Configuration

### Modifier les pourcentages par défaut
Éditez `exercise_generator/services.py`, ligne ~120 :

```python
config = {
    'total_exercises': 10,
    'mcq_percentage': 50,        # Modifier ici
    'true_false_percentage': 30,  # Modifier ici
    'fill_blank_percentage': 20,  # Modifier ici
    # ...
}
```

Ou utilisez la **page de configuration** :
http://127.0.0.1:8000/generator/config/

---

## Documentation

| Fichier | Contenu |
|---------|---------|
| `README.md` | Documentation complète (30 pages) |
| `QUICKSTART.md` | Guide de démarrage (5 pages) |
| `PROJET_COMPLETE.md` | Récapitulatif du projet |
| `COMMANDES.md` | Ce fichier |

---

## Support

- 📖 **Documentation** : Lisez les fichiers README
- 🔍 **Logs** : Consultez la console Django
- 🛠️ **Admin** : Vérifiez l'interface admin
- 💬 **Shell** : Testez avec le shell Django

---

**✅ Tout est prêt ! Commencez à générer vos exercices ! 🚀**
