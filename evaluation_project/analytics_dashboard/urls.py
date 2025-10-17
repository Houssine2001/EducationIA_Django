from django.urls import path
from . import views
from . import subject_views
from . import api_views

app_name = 'analytics_dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_overview, name='overview'),
        path('evolution/', views.student_evolution_dashboard, name='evolution_dashboard'),


    # Analytics par matière
    path('subjects/', subject_views.subject_overview, name='subject_overview'),
    path('subjects/<str:subject_name>/', subject_views.subject_detail, name='subject_detail'),
    path('subjects/class/<str:subject_name>/', subject_views.class_subject_analytics, name='class_subject_analytics'),
    path('subjects-class/', subject_views.subjects_class_list, name='subjects_class_list'),
    path('study-plan/', subject_views.student_study_plan, name='study_plan'),
    
    # Analytics étudiants
    path('student/<int:student_id>/', views.student_analytics, name='student_detail'),
    path('students/', views.students_list, name='students_list'),
    
    # Analytics classe
    path('classroom/<int:classroom_id>/', views.classroom_analytics, name='classroom_detail'),
    path('classrooms/', views.classrooms_list, name='classrooms_list'),
    
    # Rapports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    
    # Prédictions IA
    path('predictions/', views.predictions_view, name='predictions'),
    
    # API endpoints
    path('api/student-performance/<int:student_id>/', views.api_student_performance, name='api_student_performance'),
    path('api/class-trends/<int:classroom_id>/', views.api_class_trends, name='api_class_trends'),
    path('api/risk-distribution/', views.api_risk_distribution, name='api_risk_distribution'),
    path('api/overview-stats/', views.api_overview_stats, name='api_overview_stats'),
    path('api/update-predictions/', views.update_predictions, name='update_predictions'),
    path('api/refresh-analytics/', views.refresh_analytics, name='refresh_analytics'),

    # API endpoints pour les matières
    path('api/record-visit/', subject_views.record_visit_api, name='record_visit_api'),
    path('api/record-test/', subject_views.record_test_result, name='record_test'),
    path('api/subject/<str:subject_name>/', subject_views.api_subject_data, name='api_subject_data'),
    path('api/subjects-summary/', subject_views.api_all_subjects_summary, name='api_subjects_summary'),
    path('api/generate-quiz/', subject_views.generate_quiz_api, name='generate_quiz_api'),
    path('api/submit-quiz/', subject_views.submit_quiz_api, name='submit_quiz_api'),

    # API endpoints pour le tracking temps réel
    path('api/tracking/test-completion/', api_views.api_record_test_completion, name='api_record_test_completion'),
    path('api/tracking/course-visit/', api_views.api_record_course_visit, name='api_record_course_visit'),
    path('api/tracking/student-evolution/<int:student_id>/', api_views.api_get_student_evolution, name='api_get_student_evolution'),
    path('api/tracking/student-evolution/', api_views.api_get_student_evolution, name='api_get_my_evolution'),
    path('api/tracking/class-evolution/', api_views.api_get_class_evolution, name='api_get_class_evolution'),
    path('api/tracking/dashboard/', api_views.api_get_real_time_dashboard, name='api_get_real_time_dashboard'),
    path('api/tracking/performance-trends/', api_views.api_get_performance_trends, name='api_get_performance_trends'),
    path('api/tracking/engagement-metrics/', api_views.api_get_engagement_metrics, name='api_get_engagement_metrics'),
    
    # 🎮 URLs Gamification
    path('gamified/', views.gamified_dashboard, name='gamified_dashboard'),
    path('competition/<str:competition_id>/join/', views.join_competition_view, name='join_competition'),
    path('competition/<str:competition_id>/leaderboard/', views.competition_leaderboard, name='competition_leaderboard'),
    path('challenges/', views.my_challenges, name='my_challenges'),
    path('challenges/<str:challenge_id>/start/', views.start_challenge, name='start_challenge'),
    path('badges/', views.my_badges, name='my_badges'),
]