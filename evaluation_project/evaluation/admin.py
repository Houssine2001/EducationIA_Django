"""
Configuration de l'interface d'administration Django
pour le système d'évaluation
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Test, Question, Submission, Result


# ============================================
# Admin pour UserProfile
# ============================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Interface admin pour les profils utilisateurs
    """
    list_display = [
        'user', 'student_id', 'class_level', 'total_tests_taken', 
        'average_score', 'is_active', 'created_at'
    ]
    list_filter = ['class_level', 'is_active', 'created_at', 'specialization']
    search_fields = ['user__username', 'user__email', 'student_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations Utilisateur', {
            'fields': ('user', 'student_id', 'date_of_birth', 'phone_number')
        }),
        ('Informations Académiques', {
            'fields': ('class_level', 'specialization')
        }),
        ('Statistiques', {
            'fields': ('total_tests_taken', 'average_score', 'total_study_time')
        }),
        ('Analyse de Performance', {
            'fields': ('strengths', 'weaknesses', 'learning_style'),
            'classes': ('collapse',)
        }),
        ('Recommandations IA', {
            'fields': ('ai_recommendations', 'performance_history', 'skill_progress'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


# ============================================
# Admin pour Test
# ============================================

class QuestionInline(admin.TabularInline):
    """
    Inline pour afficher les questions dans l'admin Test
    """
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'points', 'order']
    show_change_link = True


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """
    Interface admin pour les tests/évaluations
    """
    list_display = [
        'title', 'subject', 'difficulty', 'status', 
        'number_of_questions', 'total_attempts', 
        'average_score_colored', 'created_at'
    ]
    list_filter = ['status', 'difficulty', 'subject', 'created_at', 'is_timed']
    search_fields = ['title', 'description', 'subject', 'topic']
    readonly_fields = [
        'created_at', 'updated_at', 'total_attempts', 
        'average_score_obtained', 'average_completion_time'
    ]
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('title', 'description', 'subject', 'topic', 'created_by')
        }),
        ('Configuration', {
            'fields': (
                'difficulty', 'duration', 'passing_score', 'total_points',
                'is_timed', 'allow_review', 'shuffle_questions'
            )
        }),
        ('Publication', {
            'fields': ('status', 'published_at')
        }),
        ('Tags et Métadonnées', {
            'fields': ('tags', 'skills_tested', 'ai_metadata'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': (
                'number_of_questions', 'total_attempts', 
                'average_score_obtained', 'average_completion_time'
            ),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def average_score_colored(self, obj):
        """Affiche le score moyen avec une couleur"""
        score = obj.average_score_obtained
        if score >= 75:
            color = 'green'
        elif score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, score
        )
    average_score_colored.short_description = 'Score Moyen'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by')


# ============================================
# Admin pour Question
# ============================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Interface admin pour les questions
    """
    list_display = [
        'question_preview', 'question_type', 'test', 
        'points', 'difficulty_level', 'success_rate_colored', 'order'
    ]
    list_filter = ['question_type', 'difficulty_level', 'test__subject', 'created_at']
    search_fields = ['question_text', 'test__title']
    readonly_fields = [
        'created_at', 'updated_at', 'times_answered', 
        'times_correct', 'average_time_spent'
    ]
    
    fieldsets = (
        ('Question', {
            'fields': ('test', 'question_text', 'question_type', 'order', 'points', 'difficulty_level')
        }),
        ('Réponses', {
            'fields': ('options', 'correct_answer')
        }),
        ('Aide et Feedback', {
            'fields': ('explanation', 'hint'),
            'classes': ('collapse',)
        }),
        ('Médias', {
            'fields': ('media_url', 'media_type'),
            'classes': ('collapse',)
        }),
        ('Analyse IA', {
            'fields': ('skills', 'ai_analysis', 'common_mistakes'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('times_answered', 'times_correct', 'average_time_spent'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        """Aperçu de la question"""
        return obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
    question_preview.short_description = 'Question'
    
    def success_rate_colored(self, obj):
        """Affiche le taux de réussite avec couleur"""
        rate = obj.calculate_success_rate()
        if rate >= 75:
            color = 'green'
        elif rate >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    success_rate_colored.short_description = 'Taux de Réussite'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('test')


# ============================================
# Admin pour Submission
# ============================================

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Interface admin pour les soumissions
    """
    list_display = [
        'student', 'test', 'status', 'score_colored', 
        'percentage', 'passed_icon', 'submitted_at'
    ]
    list_filter = ['status', 'passed', 'submitted_at', 'test__subject']
    search_fields = ['student__username', 'student__email', 'test__title']
    readonly_fields = [
        'created_at', 'updated_at', 'started_at', 
        'submitted_at', 'graded_at'
    ]
    
    fieldsets = (
        ('Références', {
            'fields': ('student', 'test', 'status')
        }),
        ('Réponses', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
        ('Temps et Progression', {
            'fields': ('started_at', 'submitted_at', 'time_spent')
        }),
        ('Score et Évaluation', {
            'fields': ('score', 'percentage', 'passed')
        }),
        ('Feedback', {
            'fields': ('teacher_feedback', 'graded_by', 'graded_at'),
            'classes': ('collapse',)
        }),
        ('Analyse IA', {
            'fields': ('ai_feedback', 'performance_analysis'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def score_colored(self, obj):
        """Affiche le score avec couleur"""
        if obj.percentage >= 75:
            color = 'green'
        elif obj.percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
            color, obj.score
        )
    score_colored.short_description = 'Score'
    
    def passed_icon(self, obj):
        """Icône pour réussite/échec"""
        if obj.passed:
            return format_html('<span style="color: green;">✓ Réussi</span>')
        return format_html('<span style="color: red;">✗ Échoué</span>')
    passed_icon.short_description = 'Résultat'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'test', 'graded_by')


# ============================================
# Admin pour Result
# ============================================

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """
    Interface admin pour les résultats détaillés
    """
    list_display = [
        'student', 'test', 'grade_colored', 'percentage_score', 
        'rank', 'percentile', 'created_at'
    ]
    list_filter = ['grade', 'test__subject', 'created_at']
    search_fields = ['student__username', 'test__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Références', {
            'fields': ('submission', 'student', 'test')
        }),
        ('Scores', {
            'fields': (
                'total_score', 'percentage_score', 'grade',
                'mcq_score', 'true_false_score', 'essay_score'
            )
        }),
        ('Analyse par Compétence', {
            'fields': ('skills_breakdown',),
            'classes': ('collapse',)
        }),
        ('Comparaisons', {
            'fields': ('rank', 'percentile', 'compared_to_average'),
            'classes': ('collapse',)
        }),
        ('Analyse Temporelle', {
            'fields': (
                'questions_per_minute', 'average_time_per_question', 
                'time_efficiency'
            ),
            'classes': ('collapse',)
        }),
        ('Analyse IA', {
            'fields': (
                'ai_analysis', 'recommendations', 'study_suggestions',
                'error_patterns', 'learning_gaps'
            ),
            'classes': ('collapse',)
        }),
        ('Visualisations', {
            'fields': ('performance_chart_data',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def grade_colored(self, obj):
        """Affiche la note avec couleur"""
        grade = obj.grade or obj.assign_grade()
        colors = {
            'A+': 'darkgreen', 'A': 'green', 'B+': 'lightgreen',
            'B': 'yellowgreen', 'C+': 'orange', 'C': 'darkorange',
            'D': 'red', 'F': 'darkred'
        }
        color = colors.get(grade, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{}</span>',
            color, grade
        )
    grade_colored.short_description = 'Note'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('submission', 'student', 'test')


# Configuration du site admin
admin.site.site_header = "Évaluation & Suivi des Performances avec IA"
admin.site.site_title = "Admin Évaluation"
admin.site.index_title = "Tableau de Bord"
