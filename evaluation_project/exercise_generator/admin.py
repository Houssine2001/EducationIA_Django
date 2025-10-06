"""
Configuration de l'interface admin pour le générateur d'exercices
"""
from django.contrib import admin
from .models import (
    CourseDocument, 
    GeneratedExercise, 
    GeneratedTest, 
    ExerciseGenerationConfig
)


@admin.register(CourseDocument)
class CourseDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'topic', 'teacher', 'processing_status', 'word_count', 'created_at']
    list_filter = ['processing_status', 'subject', 'document_type', 'created_at']
    search_fields = ['title', 'subject', 'topic', 'content']
    readonly_fields = ['word_count', 'sentence_count', 'key_concepts', 'main_topics', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'teacher', 'subject', 'topic', 'level')
        }),
        ('Contenu', {
            'fields': ('document_type', 'content', 'file_path')
        }),
        ('Analyse IA', {
            'fields': ('key_concepts', 'main_topics', 'summary', 'word_count', 'sentence_count')
        }),
        ('Traitement', {
            'fields': ('processing_status', 'processing_log')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedExercise)
class GeneratedExerciseAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'exercise_type', 'concept', 'difficulty', 'quality_score', 'status', 'created_at']
    list_filter = ['exercise_type', 'difficulty', 'status', 'created_at']
    search_fields = ['question_text', 'concept', 'topic']
    readonly_fields = ['quality_score', 'times_used', 'average_success_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Exercice', {
            'fields': ('source_document', 'exercise_type', 'question_text', 'options_data', 'explanation')
        }),
        ('Classification', {
            'fields': ('concept', 'topic', 'difficulty', 'quality_score')
        }),
        ('Source', {
            'fields': ('source_sentence',)
        }),
        ('Validation', {
            'fields': ('status', 'validated_by', 'validation_notes')
        }),
        ('Statistiques', {
            'fields': ('times_used', 'average_success_rate')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(GeneratedTest)
class GeneratedTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_document', 'teacher', 'exercise_count', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['exercises']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'source_document', 'teacher')
        }),
        ('Exercices', {
            'fields': ('exercises',)
        }),
        ('Configuration', {
            'fields': ('difficulty_distribution', 'type_distribution', 'suggested_duration')
        }),
        ('Publication', {
            'fields': ('is_published', 'evaluation_test_id')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def exercise_count(self, obj):
        return obj.exercises.count()
    exercise_count.short_description = 'Nombre d\'exercices'


@admin.register(ExerciseGenerationConfig)
class ExerciseGenerationConfigAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'default_exercise_count', 'min_quality_score', 'auto_validate']
    search_fields = ['teacher__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Enseignant', {
            'fields': ('teacher',)
        }),
        ('Paramètres généraux', {
            'fields': ('default_exercise_count', 'min_quality_score', 'auto_validate', 'include_explanations')
        }),
        ('Distribution des types', {
            'fields': ('mcq_percentage', 'true_false_percentage', 'fill_blank_percentage')
        }),
        ('Distribution des difficultés', {
            'fields': ('easy_percentage', 'medium_percentage', 'hard_percentage')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
