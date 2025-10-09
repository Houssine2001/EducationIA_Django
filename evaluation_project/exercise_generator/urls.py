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
    path('documents/<str:pk>/', views.document_detail, name='document_detail'),
    path('documents/<str:pk>/reprocess/', views.document_reprocess, name='document_reprocess'),
    
    # Exercices
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/<str:pk>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<str:pk>/validate/', views.exercise_validate, name='exercise_validate'),
    path('exercises/bulk-action/', views.exercise_bulk_action, name='exercise_bulk_action'),
    
    # Tests
    path('tests/', views.test_list, name='test_list'),
    path('tests/create/<str:document_pk>/', views.test_create, name='test_create'),
    path('tests/<str:pk>/', views.test_detail, name='test_detail'),
    path('tests/<str:pk>/export/', views.test_export, name='test_export'),
    
    # Configuration
    path('config/', views.config_view, name='config'),
    
    # Génération rapide
    path('quick-generate/', views.quick_generate, name='quick_generate'),
    
    # Exercise Sets - Collecte et Publication
    path('sets/', views.exercise_sets_list, name='exercise_sets_list'),
    path('sets/create/<str:document_id>/', views.create_exercise_set, name='create_exercise_set'),
    path('sets/<str:set_id>/', views.exercise_set_detail, name='exercise_set_detail'),
    path('sets/<str:set_id>/publish/', views.publish_exercise_set, name='publish_exercise_set'),
    path('sets/<str:set_id>/unpublish/', views.unpublish_exercise_set, name='unpublish_exercise_set'),
    path('sets/<str:set_id>/delete/', views.delete_exercise_set, name='delete_exercise_set'),
    
    # Étudiants - Accès aux sets publiés
    path('student/sets/', views.student_exercise_sets, name='student_exercise_sets'),
    path('student/sets/<str:set_id>/take/', views.student_take_exercise_set, name='student_take_exercise_set'),
    path('student/sets/<str:set_id>/result/', views.student_exercise_result, name='student_exercise_result'),
]
