from django.contrib import admin
from .models import StudentAnalytics, ClassroomAnalytics, AnalyticsReport, PredictionModel, PerformanceTrend


@admin.register(StudentAnalytics)
class StudentAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 
        'student_email', 
        'success_rate', 
        'average_score', 
        'risk_level',
        'engagement_score',
        'last_activity'
    ]
    list_filter = [
        'risk_level', 
        'created_at',
        'last_activity'
    ]
    search_fields = [
        'student_name', 
        'student_email', 
        'user__username'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at'
    ]
    fieldsets = (
        ('Informations Étudiant', {
            'fields': ('user', 'student_name', 'student_email')
        }),
        ('Métriques de Performance', {
            'fields': (
                'total_exercises', 
                'completed_exercises', 
                'average_score', 
                'success_rate'
            )
        }),
        ('Analyse Comportementale', {
            'fields': (
                'learning_velocity',
                'consistency_score', 
                'engagement_score',
                'participation_rate'
            )
        }),
        ('Prédictions IA', {
            'fields': (
                'risk_level',
                'predicted_success_probability',
                'failure_risk_score'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'last_activity',
                'created_at', 
                'updated_at'
            )
        })
    )


@admin.register(ClassroomAnalytics)
class ClassroomAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'classroom_name',
        'teacher',
        'total_students',
        'average_class_score',
        'improvement_trend',
        'updated_at'
    ]
    list_filter = [
        'improvement_trend',
        'created_at'
    ]
    search_fields = [
        'classroom_name',
        'teacher__username'
    ]
    readonly_fields = [
        'created_at',
        'updated_at'
    ]


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'report_type',
        'generated_by',
        'status',
        'created_at'  # Utiliser created_at au lieu de generated_at
    ]
    list_filter = [
        'report_type',
        'status',
        'created_at'  # Utiliser created_at au lieu de generated_at
    ]
    search_fields = [
        'title',
        'generated_by__username'
    ]
    readonly_fields = [
        'created_at'  # Retirer generated_at qui n'existe pas
    ]
    fieldsets = (
        ('Informations Rapport', {
            'fields': ('title', 'report_type', 'generated_by', 'status')
        }),
        ('Données', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',)
        })
    )


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'prediction_type',
        'predicted_outcome',
        'confidence_score',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'prediction_type',
        'is_active',
        'created_at'  # Retirer algorithm_used qui n'existe pas
    ]
    search_fields = [
        'student__username',
        'predicted_outcome'
    ]
    readonly_fields = [
        'created_at'
    ]
    fieldsets = (
        ('Prédiction', {
            'fields': (
                'student', 
                'prediction_type', 
                'predicted_outcome', 
                'confidence_score'
            )
        }),
        ('Données', {
            'fields': ('prediction_data',),
            'classes': ('collapse',)
        }),
        ('État', {
            'fields': ('is_active', 'created_at')
        })
    )


@admin.register(PerformanceTrend)
class PerformanceTrendAdmin(admin.ModelAdmin):
    list_display = [
        'student_analytics',
        'date',
        'score',
        'exercises_completed',
        'difficulty_level'
    ]
    list_filter = [
        'date',
        'difficulty_level'
    ]
    search_fields = [
        'student_analytics__student_name'
    ]
    date_hierarchy = 'date'