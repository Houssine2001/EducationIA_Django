"""
URLs pour le générateur d'exercices
"""
from django.urls import path
from . import views

app_name = 'exercise_generator'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/new/', views.document_create, name='document_create'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/reprocess/', views.document_reprocess, name='document_reprocess'),
    
    # Exercices
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:pk>/validate/', views.exercise_validate, name='exercise_validate'),
    path('exercises/bulk-action/', views.exercise_bulk_action, name='exercise_bulk_action'),
    
    # Tests
    path('tests/', views.test_list, name='test_list'),
    path('tests/create/<int:document_pk>/', views.test_create, name='test_create'),
    path('tests/<int:pk>/', views.test_detail, name='test_detail'),
    path('tests/<int:pk>/export/', views.test_export, name='test_export'),
    
    # Configuration
    path('config/', views.config_view, name='config'),
    
    # Génération rapide
    path('quick-generate/', views.quick_generate, name='quick_generate'),
]
