from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Resource(models.Model):
    """Modèle pour gérer les ressources pédagogiques"""
    
    TYPE_CHOICES = [
        ('pdf', 'Document PDF'),
        ('video', 'Vidéo'),
        ('text', 'Document Texte'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    file = models.FileField(upload_to='resources/%Y/%m/%d/', verbose_name='Fichier')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other', verbose_name='Type')
    
    # Champs IA
    summary = models.TextField(blank=True, verbose_name='Résumé IA')
    processing_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Statut de traitement'
    )
    error_message = models.TextField(blank=True, verbose_name='Message d\'erreur')
    
    # Métadonnées
    file_size = models.BigIntegerField(default=0, verbose_name='Taille du fichier (bytes)')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    downloads_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de téléchargements')
    
    # Partage
    is_public = models.BooleanField(default=False, verbose_name='Publique')
    share_token = models.CharField(max_length=100, unique=True, blank=True, verbose_name='Token de partage')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ressource'
        verbose_name_plural = 'Ressources'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Générer un token de partage si non existant
        if not self.share_token:
            self.share_token = str(uuid.uuid4())
        
        # Définir la taille du fichier
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Retourne la taille du fichier en MB"""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
    
    @property
    def has_summary(self):
        """Vérifie si la ressource a un résumé"""
        return bool(self.summary)
    
    def increment_views(self):
        """Incrémente le nombre de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_downloads(self):
        """Incrémente le nombre de téléchargements"""
        self.downloads_count += 1
        self.save(update_fields=['downloads_count'])


class ResourceTag(models.Model):
    """Modèle pour les tags/étiquettes des ressources"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Nom')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Couleur')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    
    def __str__(self):
        return self.name


class ResourceTagging(models.Model):
    """Table de liaison entre Resources et Tags"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='taggings')
    tag = models.ForeignKey(ResourceTag, on_delete=models.CASCADE, related_name='taggings')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('resource', 'tag')
        verbose_name = 'Tag de ressource'
        verbose_name_plural = 'Tags de ressources'
    
    def __str__(self):
        return f"{self.resource.title} - {self.tag.name}"


class SavedResource(models.Model):
    """Modèle pour les ressources publiques sauvegardées par les utilisateurs"""
    user_id = models.IntegerField(verbose_name='ID Utilisateur')  # Stocker l'ID au lieu de ForeignKey
    resource_id = models.IntegerField(verbose_name='ID Ressource')  # Stocker l'ID au lieu de ForeignKey
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de sauvegarde')
    notes = models.TextField(blank=True, verbose_name='Notes personnelles')
    
    class Meta:
        ordering = ['-saved_at']
        verbose_name = 'Ressource sauvegardée'
        verbose_name_plural = 'Ressources sauvegardées'
    
    def __str__(self):
        return f"User {self.user_id} - Resource {self.resource_id}"
    
    @property
    def user(self):
        """Récupère l'utilisateur associé"""
        from django.contrib.auth.models import User
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None
    
    @property
    def resource(self):
        """Récupère la ressource associée"""
        try:
            return Resource.objects.get(id=self.resource_id)
        except Resource.DoesNotExist:
            return None
