from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Upload de ressources
    path('upload/', views.upload_resource, name='upload'),
    
    # Détails et gestion des ressources
    path('<int:resource_id>/', views.resource_detail, name='detail'),
    path('<int:resource_id>/edit/', views.resource_edit, name='edit'),
    path('<int:resource_id>/delete/', views.resource_delete, name='delete'),
    
    # Actions sur les ressources
    path('<int:resource_id>/download-summary/', views.download_summary, name='download_summary'),
    path('<int:resource_id>/regenerate/', views.regenerate_summary, name='regenerate_summary'),
    path('<int:resource_id>/share/', views.share_resource, name='share'),
    
    # Partage public
    path('shared/<str:token>/', views.shared_resource, name='shared'),
    
    # Ressources publiques
    path('public/', views.public_resources, name='public'),
    path('public/<int:resource_id>/', views.public_resource_detail, name='public_detail'),
    path('public/<int:resource_id>/save/', views.save_resource, name='save'),
    path('public/<int:resource_id>/unsave/', views.unsave_resource, name='unsave'),
    
    # Ressources sauvegardées
    path('my-saved/', views.my_saved_resources, name='my_saved'),
    
    # API
    path('api/<int:resource_id>/status/', views.api_resource_status, name='api_status'),
    path('api/<int:resource_id>/debug/', views.debug_resource, name='debug_resource'),
]
