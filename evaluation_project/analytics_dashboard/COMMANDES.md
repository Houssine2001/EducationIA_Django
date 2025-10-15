# Commandes Analytics Dashboard

## 🚀 Commandes de Base

### Migrations
```bash
# Créer les migrations
python manage.py makemigrations analytics_dashboard

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations analytics_dashboard
```

### Gestion des Données
```bash
# Actualiser tous les analytics
python manage.py refresh_analytics

# Actualiser un étudiant spécifique
python manage.py refresh_analytics --student-id 123

# Calculer les prédictions pour tous
python manage.py generate_predictions

# Nettoyer les anciennes données
python manage.py cleanup_analytics --days 30
```

### Rapports
```bash
# Générer rapport de classe
python manage.py generate_class_report --teacher-id 456

# Exporter analytics en CSV
python manage.py export_analytics --format csv

# Générer rapports automatiques
python manage.py auto_reports --weekly
```

### Maintenance
```bash
# Vérifier l'intégrité des données
python manage.py check_analytics_integrity

# Recalculer tous les scores de risque
python manage.py recalculate_risks

# Optimiser les modèles IA
python manage.py optimize_models
```

### Debug et Tests
```bash
# Mode debug analytics
python manage.py runserver --settings=backend.settings_debug

# Tester les prédictions
python manage.py test_predictions --sample-size 10

# Valider les algorithmes
python manage.py validate_algorithms
```

## 📊 APIs et Tests

### Tests des APIs
```bash
# Test API performance
curl http://127.0.0.1:8000/analytics/api/student-performance/1/

# Test API overview
curl http://127.0.0.1:8000/analytics/api/class-overview/

# Test génération rapport
curl -X POST http://127.0.0.1:8000/analytics/api/generate-report/
```

### Tests unitaires
```bash
# Lancer tous les tests
python manage.py test analytics_dashboard

# Tests spécifiques
python manage.py test analytics_dashboard.tests.test_services
python manage.py test analytics_dashboard.tests.test_predictions
python manage.py test analytics_dashboard.tests.test_models
```

## 🔧 Utilitaires

### Import/Export
```bash
# Importer données existantes
python manage.py import_legacy_data --file data.json

# Exporter pour backup
python manage.py export_analytics --backup

# Synchroniser avec système externe
python manage.py sync_external_data
```

### Monitoring
```bash
# Statistiques d'utilisation
python manage.py analytics_stats

# Performance des prédictions
python manage.py prediction_accuracy

# Rapport de santé du système
python manage.py health_check
```