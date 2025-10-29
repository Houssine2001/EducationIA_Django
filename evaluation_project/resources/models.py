from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from backend.mongodb_utils import get_mongodb_client
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
    
    # Champ ID explicite pour compatibilité MongoDB
    id = models.AutoField(primary_key=True)
    
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
        # Générer un ID si non existant (pour compatibilité MongoDB)
        if not self.id:
            from pymongo import MongoClient
            from django.conf import settings
            
            try:
                # Connexion directe à MongoDB pour trouver le max ID
                client = get_mongodb_client()
                db = client[settings.MONGO_DB_NAME]
                collection = db.resources_resource
                
                # Trouver le document avec le plus grand ID (integer seulement, pas ObjectId)
                max_doc = collection.find_one(
                    {'id': {'$type': 'int'}},  # Seulement les IDs de type entier
                    sort=[('id', -1)],
                    projection={'id': 1, '_id': 0}  # Ne récupérer que le champ 'id'
                )
                self.id = (max_doc['id'] + 1) if max_doc and 'id' in max_doc else 1
                
                client.close()
            except Exception as e:
                print(f"Erreur génération ID: {e}")
                # Fallback : utiliser l'ORM Django
                try:
                    max_id_resource = Resource.objects.filter(id__isnull=False).order_by('-id').first()
                    self.id = (max_id_resource.id + 1) if max_id_resource else 1
                except:
                    self.id = 1
        
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
    id = models.AutoField(primary_key=True)  # ID explicite pour Djongo/MongoDB
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