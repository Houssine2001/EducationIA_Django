# 📚 Système de Matières et Chapitres avec Prédiction IA

## 🎯 Vue d'ensemble

Ce nouveau système permet de:
- **Lister toutes les matières** disponibles (Maths, Physique, Chimie, Biologie...)
- **Afficher les chapitres** de chaque matière
- **Tracker automatiquement les visites** de chapitres
- **Générer des prédictions de réussite** basées sur:
  - Les visites de chapitres
  - Les tests passés
  - La régularité (consistance)
  - L'engagement

---

## 📋 Étapes d'Installation

### 1. Faire les migrations
```bash
cd "C:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project"

# Créer les migrations
python manage.py makemigrations analytics_dashboard

# Appliquer les migrations
python manage.py migrate analytics_dashboard
```

### 2. Initialiser les matières et chapitres
```bash
python manage.py init_subjects
```

Cette commande crée:
- **4 matières**: Mathématiques, Physique, Chimie, Biologie
- **25+ chapitres** au total
- Chaque chapitre avec difficulté, durée, contenu

### 3. Redémarrer le serveur
```bash
python manage.py runserver
```

---

## 🌐 URLs Disponibles

### Pour les Étudiants:

| URL | Description |
|-----|-------------|
| `/analytics/matieres/` | Liste des matières avec progression |
| `/analytics/matieres/<id>/` | Chapitres d'une matière |
| `/analytics/chapitre/<id>/` | Contenu d'un chapitre |
| `/analytics/matieres/<id>/prediction/` | Prédiction détaillée |
| `/analytics/progression/` | Vue d'ensemble globale |

### Pour les Admins:

| URL | Description |
|-----|-------------|
| `/analytics/matieres/` | Gestion des matières |

---

## 🎨 Fonctionnalités

### 1. Liste des Matières

**Vue étudiant:**
- Carte pour chaque matière (icon, couleur)
- Progression: X/Y chapitres visités
- Prédiction de réussite en %
- Niveau de risque (FAIBLE, MOYEN, ÉLEVÉ, CRITIQUE)
- Bouton "Voir les chapitres"

**Données affichées:**
```python
{
    'subject': Subject object,
    'progress': {
        'chapters_visited': 5,
        'chapters_completed': 3,
        'total_chapters': 7,
        'completion_rate': 42.8%,
        'predicted_success_rate': 75.5%,
        'risk_level': 'LOW'
    }
}
```

---

### 2. Liste des Chapitres

Quand un étudiant clique sur une matière, il voit:

**Pour chaque chapitre:**
- ✅ **Statut**: Non visité / Visité / Complété
- 🎯 **Difficulté**: Facile, Moyen, Difficile
- ⏱️ **Durée estimée**: 30-60 min
- 📈 **Progression**: 0% / 50% / 100%

**Prédiction IA (en haut de page):**
```
🎯 Prédiction de Réussite: 85.5%
📊 Confiance: 75%
⚠️ Niveau de risque: FAIBLE
```

**Facteurs affichés:**
- Engagement visites: 80%
- Engagement tests: 75%
- Consistance: 65%
- Chapitres complétés: 5/7

---

### 3. Vue d'un Chapitre

Quand l'étudiant clique sur "Voir le chapitre":

**Tracking automatique:**
- ✅ Temps passé calculé automatiquement
- ✅ Visite enregistrée en base
- ✅ Progression mise à jour
- ✅ Prédiction recalculée

**Actions disponibles:**
- 📖 Lire le contenu
- ✅ Marquer comme terminé
- 📊 Voir sa progression

**Bouton "Marquer comme terminé":**
- Enregistre le chapitre comme complété
- Met à jour la progression
- Recalcule la prédiction
- Affiche un message de félicitations

---

## 🤖 Système de Prédiction IA

### Formule de Calcul

```python
# Score de base
base_score = average_test_score

# Bonus d'engagement
visit_bonus = (chapters_visited / total_chapters) * 10  # Max +10%
test_bonus = (tests_passed / tests_taken) * 10  # Max +10%
consistency_bonus = consistency_score * 5  # Max +5%

# Prédiction finale
predicted_success = base_score + visit_bonus + test_bonus + consistency_bonus
# Limité entre 0 et 100
```

### Facteurs Pris en Compte

1. **Tests (60% du poids)**
   - Moyenne des tests
   - Taux de réussite
   - Meilleur score

2. **Visites (30% du poids)**
   - Nombre de chapitres visités
   - Taux de complétion
   - Temps total passé

3. **Consistance (10% du poids)**
   - Régularité des visites
   - Écart-type entre visites

### Niveau de Risque

| Prédiction | Risque |
|-----------|--------|
| ≥ 70% | FAIBLE (Vert) |
| 50-69% | MOYEN (Orange) |
| 30-49% | ÉLEVÉ (Rouge) |
| < 30% | CRITIQUE (Violet) |

### Confiance

```python
# Basée sur le nombre de données
data_points = total_visits + tests_taken
confidence = min(data_points / 20 * 100, 95)
# Plus de données = plus de confiance
```

---

## 📊 Données Trackées

### ChapterVisit (chaque visite)
```python
{
    'student': User,
    'chapter': Chapter,
    'visited_at': datetime,
    'duration_seconds': int,
    'completed': boolean
}
```

### StudentSubjectProgress (progression globale)
```python
{
    'student': User,
    'subject': Subject,
    'total_visits': 10,
    'chapters_visited': 5,
    'chapters_completed': 3,
    'total_time_minutes': 250,
    'tests_taken': 4,
    'tests_passed': 3,
    'average_test_score': 75.5,
    'predicted_success_rate': 80.0,
    'confidence_level': 70.0,
    'risk_level': 'LOW',
    'engagement_score': 0.75,
    'consistency_score': 0.65
}
```

---

## 🎮 Intégration avec Gamification

Le système est compatible avec le dashboard gamifié existant:

### Défis automatiques
- "Complétez 5 chapitres de Mathématiques"
- "Atteignez 80% dans une matière"
- "Visitez tous les chapitres de Physique"

### Récompenses
- +50 XP par chapitre complété
- +20 coins par visite
- Badge spécial pour 100% dans une matière

---

## 📈 Recommandations IA

Le système génère automatiquement des recommandations:

### Types de recommandations:

1. **CHAPITRES NON VISITÉS** (Priorité: HAUTE)
   - "Vous n'avez pas encore visité 3 chapitres"
   - Liste des chapitres suggérés

2. **AMÉLIORER LES TESTS** (Priorité: CRITIQUE)
   - "Votre moyenne (55%) peut être améliorée"
   - Action: Réviser les chapitres

3. **RÉGULARITÉ** (Priorité: MOYENNE)
   - "Essayez de visiter les chapitres régulièrement"
   - Action: Planifier des sessions d'étude

4. **COMPLÉTION** (Priorité: MOYENNE)
   - "5 chapitres commencés mais non terminés"
   - Action: Terminer les chapitres en cours

---

## 🧪 Tests et Vérification

### Vérifier que tout fonctionne:

```bash
python manage.py shell
```

```python
# 1. Vérifier les matières
from analytics_dashboard.subject_models import Subject, Chapter
print(f"Matières: {Subject.objects.count()}")
print(f"Chapitres: {Chapter.objects.count()}")

# 2. Lister les matières
for subject in Subject.objects.all():
    chapters_count = subject.chapters.count()
    print(f"{subject.icon} {subject.name}: {chapters_count} chapitres")

# 3. Tester une visite
from django.contrib.auth.models import User
from analytics_dashboard.subject_chapter_service import SubjectChapterService

user = User.objects.get(username='etudiant2')
service = SubjectChapterService()

# Récupérer la première matière
subject = Subject.objects.first()
chapter = subject.chapters.first()

# Enregistrer une visite
visit = service.record_chapter_visit(
    student=user,
    chapter=chapter,
    duration_seconds=300,  # 5 minutes
    completed=False
)

# Vérifier la progression
progress = service.get_student_progress(user, subject)
print(f"Visites: {progress.total_visits}")
print(f"Prédiction: {progress.predicted_success_rate}%")
print(f"Confiance: {progress.confidence_level}%")
```

---

## 🎯 Scénario d'Utilisation

### Étudiant visite une matière:

1. **Étape 1**: Va sur `/analytics/matieres/`
   - Voit 4 matières avec ses progressions
   - Mathématiques: 3/7 chapitres (42%)
   - Prédiction: 65% (Risque MOYEN)

2. **Étape 2**: Clique sur "Mathématiques"
   - Redirigé vers `/analytics/matieres/<math_id>/`
   - Voit 7 chapitres avec statuts
   - Voit la prédiction en haut: 65%

3. **Étape 3**: Clique sur "Algèbre de base"
   - Redirigé vers `/analytics/chapitre/<chapter_id>/`
   - **Visite automatiquement enregistrée**
   - Lit le contenu (5 minutes)
   - Clique sur "Marquer comme terminé"

4. **Étape 4**: Retour à la liste des chapitres
   - Le chapitre est maintenant marqué ✅ "Complété"
   - Progression: 4/7 chapitres (57%)
   - **Prédiction recalculée**: 68%
   - Risque: MOYEN → FAIBLE

5. **Étape 5**: Passe un test de Mathématiques
   - Score: 75/100
   - **Prédiction recalculée automatiquement**: 75%
   - Confiance augmente: 60% → 75%

---

## 🔧 Personnalisation

### Ajouter une nouvelle matière:

```python
from analytics_dashboard.subject_models import Subject, Chapter

# Créer la matière
informatique = Subject.objects.create(
    name='Informatique',
    code='INFO',
    description='Programmation et algorithmes',
    icon='💻',
    color='#3b82f6'
)

# Ajouter des chapitres
Chapter.objects.create(
    subject=informatique,
    title='Introduction à Python',
    order=1,
    description='Les bases de Python',
    difficulty='EASY',
    duration_minutes=45,
    content='Contenu du cours...'
)
```

### Modifier les poids de prédiction:

Dans `subject_chapter_service.py`, méthode `update_prediction()`:

```python
# Modifier les bonus
visit_bonus = visit_engagement * 15  # Au lieu de 10
test_bonus = test_engagement * 15    # Au lieu de 10
```

---

## 📞 Points Importants

1. **Les visites sont trackées automatiquement** dès qu'un étudiant ouvre un chapitre
2. **La prédiction est recalculée** après chaque visite ou test
3. **Le temps passé** est calculé automatiquement
4. **Compatible avec le système existant** (analytics, gamification)
5. **Les tests existants** dans `PerformanceTrend` sont pris en compte

---

## 🚀 Lancement Rapide

```bash
# 1. Migrations
python manage.py makemigrations analytics_dashboard
python manage.py migrate analytics_dashboard

# 2. Initialiser les matières
python manage.py init_subjects

# 3. Lancer le serveur
python manage.py runserver

# 4. Accéder à:
# http://127.0.0.1:8000/analytics/matieres/
```

---

## 🎉 Résultat Final

L'étudiant peut maintenant:
- ✅ Voir toutes les matières disponibles
- ✅ Consulter les chapitres de chaque matière
- ✅ Ses visites sont automatiquement trackées
- ✅ Une prédiction de réussite est affichée en temps réel
- ✅ Des recommandations personnalisées sont générées
- ✅ Il peut suivre sa progression globale

**Tout est automatique, en temps réel, et basé sur des données réelles!** 🎯
