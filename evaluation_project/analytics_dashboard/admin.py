from django.contrib import admin
from .models import (
    StudentAnalytics, PerformanceTrend, ClassroomAnalytics, 
    PredictionModel, AnalyticsReport, SubjectAnalytics, 
    SubjectVisit, SubjectTestResult, SubjectQuiz
)


@admin.register(StudentAnalytics)
class StudentAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 
        'student_email', 
        'total_exercises', 
        'completed_exercises', 
        'average_score',
        'success_rate',
        'updated_at'
    ]
    list_filter = [
        'created_at',
        'updated_at'
    ]
    search_fields = ['student_name', 'student_email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PerformanceTrend)
class PerformanceTrendAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'subject',
        'score', 
        'date'
    ]
    list_filter = [
        'date',
        'subject'
    ]
    search_fields = ['student__username', 'subject']
    readonly_fields = ['date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(ClassroomAnalytics)
class ClassroomAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'class_name',
        'teacher', 
        'students_count',
        'average_performance'
    ]
    search_fields = ['class_name', 'teacher__username']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher')


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'prediction_type', 
        'prediction_value',
        'confidence',
        'created_at'
    ]
    list_filter = [
        'prediction_type',
        'created_at'
    ]
    search_fields = ['student__username', 'prediction_type']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'generated_by', 
        'created_at'
    ]
    list_filter = [
        'created_at'
    ]
    search_fields = ['title', 'generated_by__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')


@admin.register(SubjectAnalytics)
class SubjectAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'subject_name',
        'subject_code',
        'total_visits',
        'tests_taken',
        'average_test_score',
        'predicted_success_probability',
        'risk_level',
        'updated_at'
    ]
    list_filter = [
        'subject_name',
        'risk_level',
        'improvement_trend',
        'created_at',
        'updated_at'
    ]
    search_fields = ['user__username', 'subject_name', 'subject_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'subject_name', 'subject_code')
        }),
        ('Métriques de visite', {
            'fields': ('total_visits', 'total_time_spent', 'last_visit', 'visit_frequency')
        }),
        ('Métriques de test', {
            'fields': ('tests_taken', 'tests_passed', 'average_test_score', 'best_score', 'worst_score', 'last_test_date', 'first_test_date')
        }),
        ('Prédictions IA', {
            'fields': ('predicted_success_probability', 'risk_level', 'prediction_confidence', 'improvement_trend')
        }),
        ('Données JSON', {
            'fields': ('prediction_factors', 'recommended_actions'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SubjectVisit)
class SubjectVisitAdmin(admin.ModelAdmin):
    list_display = [
        'subject_analytics',
        'visit_date',
        'duration_minutes',
        'pages_viewed',
        'interaction_score'
    ]
    list_filter = [
        'visit_date',
        'subject_analytics__subject_name'
    ]
    search_fields = ['subject_analytics__subject_name', 'subject_analytics__user__username']
    readonly_fields = ['visit_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject_analytics__user')


@admin.register(SubjectTestResult)
class SubjectTestResultAdmin(admin.ModelAdmin):
    list_display = [
        'subject_analytics',
        'test_name',
        'test_date',
        'score',
        'max_score',
        'passed',
        'time_spent',
        'attempts'
    ]
    list_filter = [
        'test_date',
        'passed',
        'subject_analytics__subject_name'
    ]
    search_fields = ['test_name', 'subject_analytics__subject_name', 'subject_analytics__user__username']
    readonly_fields = ['test_date']
    
    fieldsets = (
        ('Informations du test', {
            'fields': ('subject_analytics', 'test_name', 'test_date')
        }),
        ('Résultats', {
            'fields': ('score', 'max_score', 'passed', 'time_spent', 'attempts')
        }),
        ('Données du quiz', {
            'fields': ('quiz_data',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject_analytics__user')


@admin.register(SubjectQuiz)
class SubjectQuizAdmin(admin.ModelAdmin):
    list_display = [
        'subject_name',
        'difficulty_level',
        'created_at'
    ]
    list_filter = [
        'subject_name',
        'difficulty_level',
        'created_at'
    ]
    search_fields = ['subject_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Informations du quiz', {
            'fields': ('subject_name', 'difficulty_level', 'created_at')
        }),
        ('Questions', {
            'fields': ('questions',),
            'description': 'Format JSON des questions et réponses'
        })
    )


# Configuration de l'admin
admin.site.site_header = "Administration Analytics IA"
admin.site.site_title = "Analytics IA Admin"
admin.site.index_title = "Gestion des Analytics"

# Personnalisation des groupes d'admin
class AnalyticsAdminConfig:
    """Configuration pour grouper les modèles dans l'admin"""
    
    @staticmethod
    def get_app_list(self, request, app_label=None):
        """Personnalise l'ordre des modèles dans l'admin"""
        app_list = super().get_app_list(request, app_label)
        
        if app_label == 'analytics_dashboard':
            # Réorganiser l'ordre des modèles
            model_order = [
                'SubjectAnalytics',
                'SubjectVisit', 
                'SubjectTestResult',
                'SubjectQuiz',
                'StudentAnalytics',
                'PerformanceTrend',
                'ClassroomAnalytics',
                'PredictionModel',
                'AnalyticsReport'
            ]
            
            for app in app_list:
                if app['app_label'] == 'analytics_dashboard':
                    # Trier selon l'ordre défini
                    app['models'].sort(
                        key=lambda x: model_order.index(x['object_name']) 
                        if x['object_name'] in model_order else 999
                    )
        
        return app_list


# Actions personnalisées pour l'admin
def recalculate_predictions(modeladmin, request, queryset):
    """Action pour recalculer les prédictions IA"""
    from .subject_services import AISubjectAnalyticsService
    service = AISubjectAnalyticsService()
    
    count = 0
    for analytics in queryset:
        try:
            service._calculate_ai_predictions(analytics)
            analytics.save()
            count += 1
        except Exception as e:
            pass
    
    modeladmin.message_user(
        request, 
        f"Prédictions recalculées pour {count} éléments."
    )

recalculate_predictions.short_description = "Recalculer les prédictions IA"

# Ajouter l'action aux admins appropriés
SubjectAnalyticsAdmin.actions = [recalculate_predictions]


def export_analytics_csv(modeladmin, request, queryset):
    """Action pour exporter les analytics en CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'
    
    writer = csv.writer(response)
    
    # Headers
    writer.writerow([
        'Utilisateur', 'Matière', 'Visites', 'Tests', 'Score Moyen', 
        'Prédiction', 'Niveau de Risque', 'Dernière Mise à Jour'
    ])
    
    # Data
    for analytics in queryset:
        writer.writerow([
            analytics.user.username,
            analytics.subject_name,
            analytics.total_visits,
            analytics.tests_taken,
            analytics.average_test_score,
            analytics.predicted_success_probability,
            analytics.risk_level,
            analytics.updated_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response

export_analytics_csv.short_description = "Exporter en CSV"

# Ajouter l'action d'export
SubjectAnalyticsAdmin.actions.append(export_analytics_csv)