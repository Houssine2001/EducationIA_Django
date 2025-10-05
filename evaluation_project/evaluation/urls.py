"""
URLs pour l'application evaluation
"""
from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    # ============================================
    # URLs Enseignants
    # ============================================
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/test/create/', views.create_test, name='create_test'),
    path('teacher/test/<int:test_id>/edit/', views.edit_test, name='edit_test'),
    path('teacher/test/<int:test_id>/question/add/', views.add_question, name='add_question'),
    path('teacher/test/<int:test_id>/statistics/', views.test_statistics, name='test_statistics'),
    
    # ============================================
    # URLs Étudiants
    # ============================================
    path('', views.student_dashboard, name='student_dashboard'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
    path('test/<int:test_id>/start/', views.start_test, name='start_test'),
    path('test/<int:test_id>/history/', views.test_history, name='test_history'),
    path('submission/<int:submission_id>/take/', views.take_test, name='take_test'),
    path('submission/<int:submission_id>/submit/', views.submit_test, name='submit_test'),
    path('result/<int:result_id>/', views.view_result, name='view_result'),
    path('progress/', views.student_progress, name='student_progress'),
    
    # ============================================
    # API AJAX
    # ============================================
    path('api/save-answer/', views.save_answer_ajax, name='save_answer_ajax'),
    path('api/test/<int:test_id>/stats/', views.get_test_stats_ajax, name='get_test_stats_ajax'),
]
