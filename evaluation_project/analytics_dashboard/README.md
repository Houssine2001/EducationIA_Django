# Analytics Dashboard - Module d'Analyse et de Prédiction

## 📊 Description
Module d'analytics avancé pour le suivi et l'analyse des performances étudiantes avec prédictions IA et génération de rapports.

## 🎯 Fonctionnalités Principales

### 1. Tableau de Bord Analytics
- Vue d'ensemble des performances étudiantes
- Métriques de performance en temps réel
- Indicateurs de risque d'échec
- Tendances d'apprentissage

### 2. Prédictions IA
- Évaluation automatique des risques d'échec
- Prédictions de performance future
- Recommandations personnalisées
- Alertes précoces pour les étudiants en difficulté

### 3. Analytics Individuels
- Profil détaillé de chaque étudiant
- Historique des performances
- Analyse comportementale
- Tendances d'apprentissage personnalisées

### 4. Analytics de Classe
- Vue d'ensemble de la classe
- Comparaisons entre étudiants
- Statistiques collectives
- Identification des tendances de groupe

### 5. Génération de Rapports
- Rapports exportables en PDF/Excel
- Graphiques dynamiques
- Résumés textuels automatiques
- Recommandations d'amélioration

## 🚀 Installation et Configuration

### 1. Installation des dépendances
```bash
pip install pandas numpy scikit-learn matplotlib seaborn plotly
pip install openpyxl reportlab
```

### 2. Migrations
```bash
python manage.py makemigrations analytics_dashboard
python manage.py migrate
```

### 3. Configuration dans settings.py
Ajouter 'analytics_dashboard' dans INSTALLED_APPS

## 📋 Utilisation

### URLs principales
- `/analytics/` - Dashboard principal
- `/analytics/student/<id>/` - Analytics étudiant
- `/analytics/classroom/` - Analytics classe
- `/analytics/risk-assessment/` - Évaluation des risques
- `/analytics/reports/` - Gestion des rapports

### APIs disponibles
- `/analytics/api/student-performance/<id>/` - Données performance
- `/analytics/api/class-overview/` - Vue d'ensemble classe
- `/analytics/api/risk-distribution/` - Répartition des risques

## 🔧 Services Disponibles

### AnalyticsService
- `update_student_analytics(student)` - Mise à jour analytics
- `get_overview_data()` - Données d'overview
- `update_classroom_analytics(teacher)` - Analytics classe

### PredictionService  
- `predict_student_risk(student)` - Prédiction risque
- `generate_recommendations(student)` - Recommandations

### ReportService
- `generate_student_report(student)` - Rapport étudiant
- `generate_class_report(teacher)` - Rapport classe

## 📊 Métriques Calculées

### Performance
- Taux de réussite
- Score moyen
- Nombre d'exercices complétés
- Vitesse d'apprentissage

### Comportement
- Score d'engagement
- Régularité d'activité
- Adaptation à la difficulté
- Temps passé

### Prédictions
- Niveau de risque (LOW/MEDIUM/HIGH/CRITICAL)
- Probabilité de réussite
- Score de risque d'échec
- Recommandations IA

## 🛠️ Commandes de gestion

### Actualiser les analytics
```bash
python manage.py refresh_analytics
```

### Générer les prédictions
```bash
python manage.py generate_predictions
```

### Nettoyer les anciennes données
```bash
python manage.py cleanup_analytics
```

## 📈 Algorithmes IA Utilisés

### Random Forest
- Classification des niveaux de risque
- Prédiction des performances futures
- Identification des patterns d'apprentissage

### Régression Linéaire
- Calcul des tendances
- Prédiction des scores futurs
- Analyse de la progression

### Clustering
- Groupement d'étudiants similaires
- Identification des profils d'apprentissage
- Recommandations personnalisées

## 🔒 Sécurité et Permissions

### Rôles d'accès
- **Administrateur**: Accès complet
- **Enseignant**: Analytics de sa classe
- **Étudiant**: Ses propres analytics (lecture seule)

### Protection des données
- Anonymisation des données sensibles
- Chiffrement des prédictions
- Audit trail des accès

## 📝 Logs et Debug

### Logs disponibles
- Analytics calculations
- Prediction generations  
- Report generations
- API calls

### Debug mode
```python
ANALYTICS_DEBUG = True  # dans settings.py
```

## 🤝 Intégration avec les autres modules

### Avec evaluation
- Récupération des soumissions
- Calcul des scores
- Suivi des progrès

### Avec exercise_generator
- Analytics des tests IA
- Performance sur exercices générés
- Adaptation aux difficultés

## 📞 Support et Maintenance

### Maintenance régulière
- Nettoyage des anciennes prédictions
- Recalcul des analytics
- Optimisation des algorithmes

### Monitoring
- Performance des prédictions
- Temps de calcul
- Utilisation mémoire

## 🔄 Mises à jour et Evolution

### Version actuelle: 1.0.0
### Prochaines fonctionnalités:
- Deep Learning pour prédictions
- Analytics temps réel
- Dashboard mobile
- Intégration LMS

---

📧 **Contact**: Équipe EducationIA
🌐 **Documentation**: `/analytics/docs/`