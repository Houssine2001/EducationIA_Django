"""
URLs pour l'application evaluation
"""
from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    # ============================================
    # Authentification
    # ============================================
   path('signup/', views.signup, name='signup'),    
    # ============================================
    # URLs Enseignants
    # ============================================
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/test/create/', views.create_test, name='create_test'),
    path('teacher/test/<str:test_id>/edit/', views.edit_test, name='edit_test'),
    path('teacher/test/<str:test_id>/question/add/', views.add_question, name='add_question'),
    path('teacher/test/<str:test_id>/statistics/', views.test_statistics, name='test_statistics'),
    path('teacher/students/', views.students_list, name='students_list'),
    
    # Recommandations manuelles
    path('teacher/recommendations/', views.manual_recommendations_list, name='manual_recommendations_list'),
    path('teacher/recommendations/create/', views.create_recommendation, name='create_recommendation'),
    path('teacher/recommendations/<int:recommendation_id>/edit/', views.edit_recommendation, name='edit_recommendation'),
    path('teacher/recommendations/<int:recommendation_id>/delete/', views.delete_recommendation, name='delete_recommendation'),
    
    # ============================================
    # URLs Étudiants
    # ============================================
    path('', views.student_dashboard, name='student_dashboard'),
    path('my-tests/', views.my_tests, name='my_tests'),
    path('my-badges/', views.my_badges, name='my_badges'),
    path('test/<str:test_id>/', views.test_detail, name='test_detail'),
    path('test/<str:test_id>/start/', views.start_test, name='start_test'),
    path('test/<str:test_id>/history/', views.test_history, name='test_history'),
    path('submission/<str:submission_id>/take/', views.take_test, name='take_test'),
    path('submission/<str:submission_id>/submit/', views.submit_test, name='submit_test'),
    path('result/<str:result_id>/', views.view_result, name='view_result'),
    path('progress/', views.student_progress, name='student_progress'),
    
    # ============================================
    # API AJAX
    # ============================================
    path('api/save-answer/', views.save_answer_ajax, name='save_answer_ajax'),
    path('api/test/<str:test_id>/stats/', views.get_test_stats_ajax, name='get_test_stats_ajax'),
]
