"""
Commande pour entraîner le modèle de prédiction IA avec les vraies données
Usage: python manage.py train_prediction_model
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_dashboard.services import PredictionService, AnalyticsService
from analytics_dashboard.models import StudentAnalytics, PerformanceTrend
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Entraîne le modèle de prédiction IA avec les données réelles des étudiants'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Démarrage de l\'entraînement du modèle de prédiction IA...'))
        
        prediction_service = PredictionService()
        analytics_service = AnalyticsService()
        
        # 1. Récupérer tous les étudiants
        students = User.objects.filter(groups__name='Etudiants')
        total_students = students.count()
        
        if total_students == 0:
            self.stdout.write(self.style.WARNING('⚠️  Aucun étudiant trouvé dans le groupe "Etudiants"'))
            return
        
        self.stdout.write(f'📊 {total_students} étudiants trouvés')
        
        # 2. Mettre à jour les analytics de chaque étudiant
        self.stdout.write('\n📈 Mise à jour des analytics...')
        updated_count = 0
        
        for student in students:
            try:
                analytics_service.update_student_analytics(student)
                updated_count += 1
                self.stdout.write(f'  ✅ {student.username} - Analytics mis à jour')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {student.username} - Erreur: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {updated_count}/{total_students} analytics mis à jour'))
        
        # 3. Générer les prédictions pour chaque étudiant
        self.stdout.write('\n🔮 Génération des prédictions...')
        predictions_count = 0
        
        for student in students:
            try:
                prediction = prediction_service.generate_real_prediction(student)
                
                # Afficher les détails de la prédiction
                if isinstance(prediction, dict):
                    predicted_score = prediction.get('predicted_score', 0)
                    confidence = prediction.get('confidence_level', 0)
                    based_on_tests = prediction.get('based_on_tests', 0)
                    
                    self.stdout.write(
                        f'  ✅ {student.username}: '
                        f'Prédiction={predicted_score}% | '
                        f'Confiance={confidence}% | '
                        f'Tests={based_on_tests}'
                    )
                    predictions_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  {student.username}: Format de prédiction inattendu'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {student.username} - Erreur: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {predictions_count}/{total_students} prédictions générées'))
        
        # 4. Statistiques globales
        self.stdout.write('\n📊 Statistiques globales:')
        
        analytics_with_data = StudentAnalytics.objects.filter(
            total_exercises__gt=0
        ).count()
        
        trends_count = PerformanceTrend.objects.count()
        
        self.stdout.write(f'  • Étudiants avec données: {analytics_with_data}')
        self.stdout.write(f'  • Total de tendances de performance: {trends_count}')
        
        # 5. Afficher quelques prédictions détaillées
        self.stdout.write('\n🎯 Exemples de prédictions:')
        
        from analytics_dashboard.models import PredictionModel
        recent_predictions = PredictionModel.objects.filter(
            prediction_type='overall_performance'
        ).order_by('-created_at')[:5]
        
        for pred in recent_predictions:
            raw_data = pred.raw_data
            self.stdout.write(
                f'\n  👤 {pred.student.username}:'
            )
            self.stdout.write(f'     Score prédit: {pred.prediction_value}%')
            self.stdout.write(f'     Confiance: {pred.confidence}%')
            self.stdout.write(f'     Basé sur: {raw_data.get("based_on_tests", 0)} tests')
            self.stdout.write(f'     Moyenne actuelle: {raw_data.get("current_average", 0)}')
            self.stdout.write(f'     Tendance: {raw_data.get("trend", 0):.2f}')
            self.stdout.write(f'     Engagement: {raw_data.get("engagement", 0):.2f}')
            self.stdout.write(f'     Consistance: {raw_data.get("consistency", 0):.2f}')
        
        self.stdout.write(self.style.SUCCESS('\n\n🎉 Entraînement du modèle terminé avec succès!'))
        self.stdout.write('💡 Le modèle utilisera maintenant ces prédictions pour tous les étudiants')
