from django.urls import path
from . import views

app_name = 'analytics_dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_overview, name='overview'),
    
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
]