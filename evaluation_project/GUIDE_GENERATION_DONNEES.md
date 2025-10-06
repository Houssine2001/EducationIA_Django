# 🚀 Guide Rapide - Génération de Données de Test

## 📋 Résumé

Commande Django pour générer automatiquement des étudiants, tests et résultats réalistes afin de tester les interfaces (dashboard, mes tests, badges, etc.).

---

## ⚡ Utilisation Rapide

### 1. Générer des données par défaut (3 étudiants, 15 tests)
```bash
python manage.py generate_test_data
```

### 2. Générer avec paramètres personnalisés
```bash
# 5 étudiants et 20 tests
python manage.py generate_test_data --students 5 --tests 20

# 10 étudiants et 50 tests
python manage.py generate_test_data --students 10 --tests 50
```

### 3. Nettoyer et régénérer
```bash
python manage.py generate_test_data --clear --students 3 --tests 15
```

**⚠️ ATTENTION**: `--clear` supprime TOUTES les données de test existantes !

---

## 👥 Comptes Étudiants Générés

Tous les étudiants ont le même mot de passe: **`password123`**

| Username | Email | Password |
|----------|-------|----------|
| etudiant1 | etudiant1@example.com | password123 |
| etudiant2 | etudiant2@example.com | password123 |
| etudiant3 | etudiant3@example.com | password123 |
| ... | ... | ... |

---

## 📊 Données Générées

### Tests
- **Matières**: Mathématiques, Physique, Chimie, Informatique, Français, Anglais, Histoire, Géographie
- **Questions**: 8-15 questions par test
- **Options**: 3-5 options par question (1 correcte)
- **Durée**: 30, 45, 60 ou 90 minutes
- **Note de passage**: 50%, 60% ou 70%

### Soumissions
- Chaque étudiant fait entre 10 et tous les tests disponibles
- 1 à 3 tentatives par test
- Dates réparties sur les 30 derniers jours
- Taux de réussite: ~70% (réaliste)

### Résultats
- Scores calculés automatiquement
- Points forts et lacunes générés selon les performances
- XP et niveaux mis à jour
- Historique de progression

---

## 🎯 Cas d'Utilisation

### Tester l'interface "Mes Tests"
```bash
# Générer beaucoup de tests pour voir la pagination
python manage.py generate_test_data --tests 30
```

### Tester les Points Forts
```bash
# Générer plusieurs étudiants avec beaucoup de tests
python manage.py generate_test_data --students 5 --tests 25
```

### Tester le Dashboard
```bash
# Données minimales
python manage.py generate_test_data --students 1 --tests 10
```

### Tester la Performance
```bash
# Beaucoup de données
python manage.py generate_test_data --students 20 --tests 50
```

---

## 📝 Exemple de Session Complète

```bash
# 1. Nettoyer les anciennes données
python manage.py generate_test_data --clear

# 2. Générer des données de test
python manage.py generate_test_data --students 3 --tests 20

# 3. Lancer le serveur
python manage.py runserver

# 4. Se connecter
# URL: http://localhost:8000/login/
# Username: etudiant1
# Password: password123

# 5. Explorer les interfaces
# Dashboard: http://localhost:8000/
# Mes Tests: http://localhost:8000/my-tests/
# Mes Badges: http://localhost:8000/my-badges/
# Progression: http://localhost:8000/progress/
```

---

## ✅ Vérification

Après génération, vérifiez que:

1. **Étudiants créés**
   ```python
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(username__startswith='etudiant').count()
   3  # Doit correspondre au nombre demandé
   ```

2. **Tests créés**
   ```python
   >>> from evaluation.models import Test
   >>> Test.objects.count()
   20  # Doit correspondre au nombre demandé
   ```

3. **Résultats générés**
   ```python
   >>> from evaluation.models import Result
   >>> Result.objects.count()
   # Variable selon les tentatives (généralement 30-100)
   ```

4. **Profils mis à jour**
   ```python
   >>> from evaluation.models import UserProfile
   >>> profile = UserProfile.objects.filter(user__username='etudiant1').first()
   >>> profile.total_tests_taken
   # Nombre de tests complétés
   >>> profile.average_score
   # Score moyen (généralement 60-80)
   >>> profile.strengths
   # Liste des points forts
   >>> profile.weaknesses
   # Liste des lacunes
   ```

---

## 🔧 Options de la Commande

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `--students` | int | 3 | Nombre d'étudiants à créer |
| `--tests` | int | 15 | Nombre de tests à créer |
| `--clear` | flag | false | Supprime les données existantes avant génération |

---

## 📊 Statistiques Générées

Pour chaque étudiant:
- ✅ ID étudiant unique (STU1000, STU1001, ...)
- ✅ Niveau scolaire (1ère, Terminale, Licence 1/2)
- ✅ Spécialisation (Sciences, Lettres, Informatique, Économie)
- ✅ Total de tests passés
- ✅ Score moyen calculé
- ✅ XP et niveau
- ✅ Points forts (3-5 items)
- ✅ Lacunes (1-3 items)

---

## 🎨 Distribution des Scores

Les scores générés suivent une distribution réaliste:

- **70% de bonnes réponses** en moyenne
- **Variation**: 40-100% selon les matières et tentatives
- **Amélioration**: Les tentatives ultérieures ont généralement de meilleurs scores
- **Progression**: Scores répartis sur 30 jours pour montrer l'évolution

---

## 💡 Conseils

1. **Première utilisation**: Commencez avec les valeurs par défaut
   ```bash
   python manage.py generate_test_data
   ```

2. **Test de charge**: Utilisez `--clear` pour repartir de zéro
   ```bash
   python manage.py generate_test_data --clear --students 10 --tests 50
   ```

3. **Développement**: Gardez des données minimales
   ```bash
   python manage.py generate_test_data --students 2 --tests 10
   ```

4. **Démonstration**: Générez beaucoup de données pour impressionner
   ```bash
   python manage.py generate_test_data --students 20 --tests 100
   ```

---

## 🐛 Dépannage

### Erreur: "No module named 'evaluation.management'"
```bash
# Vérifiez la structure des dossiers
evaluation/
  management/
    __init__.py
    commands/
      __init__.py
      generate_test_data.py
```

### Erreur: "Command 'generate_test_data' not found"
```bash
# Vérifiez que les fichiers __init__.py existent
# Redémarrez le shell Python
```

### Les données ne s'affichent pas
```bash
# Vérifiez que vous êtes connecté avec un compte étudiant
# Username: etudiant1
# Password: password123
```

---

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs avec `python manage.py check`
2. Vérifiez les données dans l'admin Django
3. Consultez le fichier `CORRECTIONS_SESSION_2.md` pour plus de détails

---

**Créé le**: 6 Octobre 2025  
**Version**: 1.0
