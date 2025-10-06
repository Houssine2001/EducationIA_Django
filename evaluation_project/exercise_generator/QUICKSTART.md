# 🚀 GUIDE DE DÉMARRAGE RAPIDE - Générateur d'Exercices IA

## Installation en 5 minutes ⏱️

### 1. Installer les dépendances
```powershell
pip install PyPDF2
```

### 2. Créer les tables en base de données
```powershell
python manage.py makemigrations exercise_generator
python manage.py migrate
```

### 3. Créer un compte enseignant (si nécessaire)
```powershell
python manage.py createsuperuser
```

### 4. Lancer le serveur
```powershell
python manage.py runserver
```

### 5. Accéder au générateur
Ouvrez votre navigateur : **http://127.0.0.1:8000/generator/**

---

## Utilisation Rapide 🎯

### Méthode 1 : Génération Rapide (la plus simple)

1. Allez sur : http://127.0.0.1:8000/generator/quick-generate/
2. Collez un texte de cours (minimum 50 mots)
3. Indiquez la matière
4. Choisissez le nombre d'exercices
5. Cliquez sur "Générer"
6. ✅ Les exercices sont créés en quelques secondes !

### Méthode 2 : Document Complet

1. Allez sur : http://127.0.0.1:8000/generator/documents/new/
2. Remplissez les informations du cours
3. Uploadez un PDF **OU** collez le texte
4. Cliquez sur "Analyser et Générer"
5. Consultez les exercices générés
6. Validez ceux qui vous conviennent
7. Créez un test personnalisé

---

## Exemple de Texte pour Tester 📝

Copiez ce texte pour essayer :

```
La Révolution française est une période de bouleversements sociaux et politiques 
en France qui a duré de 1789 à 1799. Elle commence avec la prise de la Bastille 
le 14 juillet 1789. Les causes principales sont les inégalités sociales, 
la crise économique et l'influence des idées des Lumières.

La société française était divisée en trois ordres : le clergé, la noblesse 
et le tiers-état. Ce dernier représentait 98% de la population mais n'avait 
que très peu de pouvoir politique. La Déclaration des Droits de l'Homme et 
du Citoyen a été adoptée le 26 août 1789.

La Révolution a aboli la monarchie absolue et instauré une république. 
Elle a profondément transformé la société française avec l'abolition des 
privilèges, la séparation des pouvoirs et l'égalité devant la loi.
```

---

## Résultats Attendus ✅

Après génération, vous devriez obtenir environ **10 exercices** :

### QCM (5 exercices)
- "Quand a commencé la Révolution française ?"
- "Quels étaient les trois ordres de la société ?"
- etc.

### Vrai/Faux (3 exercices)
- "La prise de la Bastille a eu lieu le 14 juillet 1789" (Vrai)
- "Le tiers-état représentait 50% de la population" (Faux)
- etc.

### Texte à trous (2 exercices)
- "La Révolution française a duré de 1789 à ___" (1799)
- "La Déclaration des Droits de l'Homme a été adoptée le ___" (26 août 1789)

---

## Accès Admin 👨‍💼

Pour gérer via l'interface admin Django :

1. Connectez-vous : http://127.0.0.1:8000/admin/
2. Sections disponibles :
   - **Documents de cours** : Voir tous les documents
   - **Exercices générés** : Filtrer et gérer
   - **Tests générés** : Consulter les tests
   - **Configurations** : Paramètres enseignants

---

## Commandes Utiles 💻

### Vérifier l'installation
```powershell
python manage.py check exercise_generator
```

### Voir les migrations
```powershell
python manage.py showmigrations exercise_generator
```

### Créer un document via shell Django
```powershell
python manage.py shell
```

```python
from exercise_generator.models import CourseDocument
from django.contrib.auth.models import User

# Récupérer un enseignant
teacher = User.objects.first()

# Créer un document
doc = CourseDocument.objects.create(
    title="Test",
    content="Votre texte ici...",
    subject="Mathématiques",
    teacher=teacher
)

# Générer des exercices
from exercise_generator.services import ExerciseGenerationService
service = ExerciseGenerationService()
result = service.process_document(doc)

print(f"✅ {len(result['exercises'])} exercices générés !")
```

---

## Problèmes Courants 🔧

### Erreur : Module 'exercise_generator' not found
➡️ Vérifiez que l'app est dans `INSTALLED_APPS` de `settings.py`

### Erreur : PyPDF2 not installed
```powershell
pip install PyPDF2
```

### Les exercices ne sont pas générés
➡️ Le texte doit contenir au moins 50 mots significatifs en français

### Erreur 404 sur /generator/
➡️ Vérifiez que les URLs sont incluses dans `backend/urls.py`

---

## Prochaines Étapes 🎓

1. ✅ Testez avec vos propres cours
2. ✅ Configurez vos préférences dans `/generator/config/`
3. ✅ Créez des tests pour vos étudiants
4. ✅ Exportez vers l'application d'évaluation
5. ✅ Consultez le README complet pour les fonctionnalités avancées

---

## Ressources 📚

- **README complet** : `exercise_generator/README.md`
- **Documentation Django** : https://docs.djangoproject.com/
- **Support** : Consultez les logs du serveur Django

---

**🎉 Vous êtes prêt ! Bonne génération d'exercices ! 🚀**
