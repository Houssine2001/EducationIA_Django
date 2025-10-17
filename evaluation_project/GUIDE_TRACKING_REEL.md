# 🎯 Guide: Tracking Réel des Visites et Tests

## 📋 Objectif
Ce guide explique comment activer le système de tracking réel pour que:
- Les visites de cours soient enregistrées automatiquement
- Les tests passés soient trackés en temps réel
- Les prédictions IA soient basées sur des données réelles

## 🔧 1. Entraîner le Modèle de Prédiction IA

### Commande
```bash
python manage.py train_prediction_model
```

### Ce que fait cette commande:
- Met à jour les analytics de tous les étudiants
- Génère des prédictions basées sur les vraies données
- Calcule les tendances, engagement et consistance
- Affiche des statistiques détaillées

### Exemple de sortie:
```
🤖 Démarrage de l'entraînement du modèle...
📊 15 étudiants trouvés
📈 Mise à jour des analytics...
  ✅ etudiant2 - Analytics mis à jour
✅ 15/15 analytics mis à jour

🔮 Génération des prédictions...
  ✅ etudiant2: Prédiction=80.0% | Confiance=75.0% | Tests=10
✅ 15/15 prédictions générées

🎉 Entraînement terminé!
```

## 📊 2. Activer le Tracking des Visites de Cours

### Option A: Middleware Automatique (Recommandé)

Ajoutez ce code dans `backend/middleware.py`:

```python
from analytics_dashboard.tracking_service import StudentTrackingService
from django.urls import resolve

class CourseVisitTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.tracking_service = StudentTrackingService()
    
    def __call__(self, request):
        # Avant la vue
        if request.user.is_authenticated and not request.user.is_staff:
            # Détecter si c'est une visite de cours
            url_name = resolve(request.path_info).url_name
            
            if url_name in ['subject_overview', 'course_detail', 'lesson_view']:
                # Extraire le nom du cours depuis l'URL ou les paramètres
                course_name = request.GET.get('subject', 'Cours')
                
                # Enregistrer la visite
                self.tracking_service.record_course_visit(
                    student=request.user,
                    course_name=course_name
                )
        
        response = self.get_response(request)
        return response
```

Puis activez-le dans `backend/settings.py`:
```python
MIDDLEWARE = [
    ...
    'backend.middleware.CourseVisitTrackingMiddleware',  # Ajouter ici
]
```

### Option B: Tracking Manuel dans les Vues

Dans vos vues de cours, ajoutez:

```python
from analytics_dashboard.tracking_service import StudentTrackingService
from analytics_dashboard.subject_services import SubjectTrackingService

def course_view(request, subject_name):
    # Votre logique existante...
    
    # Ajouter le tracking
    if request.user.is_authenticated:
        tracking_service = SubjectTrackingService()
        tracking_service.track_subject_visit(
            student=request.user,
            subject_name=subject_name,
            duration_minutes=None  # Sera calculé automatiquement
        )
    
    return render(request, 'course_template.html', context)
```

## ✅ 3. Activer le Tracking des Tests

### Modifier la Vue de Soumission de Test

Dans `evaluation/views.py`, dans la fonction qui gère la soumission:

```python
from analytics_dashboard.tracking_service import StudentTrackingService

def submit_test(request, test_id):
    # ... votre logique existante de soumission ...
    
    # Calculer le score
    score = calculate_score(submission)  # Votre fonction de calcul
    
    # Enregistrer dans le système de tracking
    if request.user.is_authenticated:
        tracking_service = StudentTrackingService()
        tracking_service.record_test_completion(
            student=request.user,
            test_name=test.title,
            score=score,
            subject=test.subject  # Nom de la matière
        )
    
    # ... reste de votre code ...
```

## 🔄 4. Mettre à Jour Automatiquement les Analytics

### Signal Django (Recommandé)

Créez `analytics_dashboard/signals.py` (déjà créé):

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from evaluation.models import Submission, Result
from .tracking_service import StudentTrackingService

@receiver(post_save, sender=Result)
def update_analytics_on_test_completion(sender, instance, created, **kwargs):
    \"\"\"
    Met à jour les analytics quand un étudiant termine un test
    \"\"\"
    if created and instance.student:
        tracking_service = StudentTrackingService()
        tracking_service.record_test_completion(
            student=instance.student,
            test_name=instance.test.title,
            score=instance.score_percentage,
            subject=getattr(instance.test, 'subject', 'General')
        )
```

Activez les signals dans `analytics_dashboard/apps.py`:

```python
class AnalyticsDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics_dashboard'
    
    def ready(self):
        import analytics_dashboard.signals  # Importer les signals
```

## 📈 5. Vérifier que Tout Fonctionne

### Test 1: Vérifier les Prédictions
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from analytics_dashboard.models import PredictionModel

# Voir toutes les prédictions
for pred in PredictionModel.objects.all():
    print(f"{pred.student.username}: {pred.prediction_value}% (confiance: {pred.confidence}%)")
```

### Test 2: Vérifier les Visites
```python
from analytics_dashboard.models import SubjectVisit

# Voir les visites récentes
visits = SubjectVisit.objects.order_by('-visited_at')[:10]
for visit in visits:
    print(f"{visit.subject_analytics.student.username} - {visit.subject_analytics.subject_name} - {visit.visited_at}")
```

### Test 3: Vérifier les Performances
```python
from analytics_dashboard.models import PerformanceTrend

# Voir les performances récentes
trends = PerformanceTrend.objects.order_by('-date')[:10]
for trend in trends:
    print(f"{trend.student.username} - {trend.subject}: {trend.score}%")
```

## 🎮 6. Intégration avec la Gamification

Le système de gamification utilise automatiquement ces données pour:
- ✅ Générer des défis personnalisés basés sur les matières faibles
- ✅ Calculer l'engagement via les visites de cours
- ✅ Attribuer des récompenses selon les tests passés
- ✅ Mettre à jour le classement en temps réel

### Mettre à Jour un Défi après un Test

Dans votre vue de soumission de test, ajoutez:

```python
from analytics_dashboard.services import ChallengeService

def submit_test(request, test_id):
    # ... code existant ...
    
    # Mettre à jour les défis actifs
    if request.user.is_authenticated:
        challenge_service = ChallengeService()
        
        # Récupérer les défis actifs de l'étudiant
        active_challenges = Challenge.objects.filter(
            student=request.user,
            status='ACTIVE'
        )
        
        for challenge in active_challenges:
            # Si le test est dans la matière du défi
            if test.subject == challenge.target_data.get('subject'):
                # Mettre à jour la progression
                challenge_service.update_challenge_progress(
                    challenge=challenge,
                    exercises_completed=1,
                    current_score=score
                )
    
    # ... reste du code ...
```

## 📊 7. Dashboard en Temps Réel

Vous pouvez maintenant consulter:

- **`/analytics/`** - Dashboard IA avec prédictions réelles
- **`/analytics/subjects/`** - Analytics par matière
- **`/analytics/evolution/`** - Évolution des étudiants
- **`/analytics/gamified/`** - Dashboard gamifié avec défis

## 🔧 8. Commandes Utiles

### Actualiser toutes les analytics
```bash
python manage.py refresh_analytics
```

### Entraîner le modèle IA
```bash
python manage.py train_prediction_model
```

### Générer des données de test
```bash
python manage.py generate_test_data
```

### Initialiser la gamification
```bash
python manage.py init_gamification
```

## ⚠️ Résolution des Problèmes

### Les prédictions sont à 0%
```bash
# Vérifier si des tests existent
python manage.py shell
>>> from analytics_dashboard.models import PerformanceTrend
>>> PerformanceTrend.objects.count()
```

Si 0, les étudiants doivent passer des tests d'abord.

### Les visites ne sont pas enregistrées
- Vérifiez que le middleware est activé
- Vérifiez que l'utilisateur n'est pas staff
- Vérifiez les logs Django pour les erreurs

### Les défis ne se mettent pas à jour
- Assurez-vous que `update_challenge_progress()` est appelé
- Vérifiez que la matière correspond (`challenge.target_data['subject']`)
- Vérifiez que le défi est ACTIVE

## 📝 Notes Importantes

1. **Données Réelles uniquement**: Le système utilise maintenant uniquement des données réelles, pas de génération fictive
2. **Performance**: Le calcul des analytics est optimisé avec des agrégations Django
3. **Djongo**: Attention aux `.count()` sur les querysets limités - utilisez `len(list())`
4. **ObjectId**: MongoDB utilise `ObjectId`, pensez à convertir dans les vues

## 🎉 Résultat Final

Après configuration:
- ✅ Chaque visite de cours est trackée automatiquement
- ✅ Chaque test passé met à jour les analytics
- ✅ Les prédictions IA sont basées sur vraies données
- ✅ Les défis de gamification se mettent à jour automatiquement
- ✅ Le classement est en temps réel
- ✅ Les badges sont attribués selon les performances réelles
