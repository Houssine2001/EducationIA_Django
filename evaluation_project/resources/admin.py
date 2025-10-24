from django.contrib import admin
from .models import Resource, ResourceTag, ResourceTagging, SavedResource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'processing_status', 'is_public', 'created_at']
    list_filter = ['type', 'processing_status', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'views_count', 'downloads_count', 'share_token']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'title', 'description', 'file', 'type')
        }),
        ('IA et traitement', {
            'fields': ('summary', 'processing_status', 'error_message')
        }),
        ('Métadonnées', {
            'fields': ('file_size', 'views_count', 'downloads_count')
        }),
        ('Partage', {
            'fields': ('is_public', 'share_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ResourceTag)
class ResourceTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']


@admin.register(ResourceTagging)
class ResourceTaggingAdmin(admin.ModelAdmin):
    list_display = ['resource', 'tag', 'created_at']
    list_filter = ['tag', 'created_at']
    search_fields = ['resource__title', 'tag__name']


@admin.register(SavedResource)
class SavedResourceAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'resource__title']
    readonly_fields = ['saved_at']
    
    fieldsets = (
        ('Sauvegarde', {
            'fields': ('user', 'resource', 'saved_at')
        }),
        ('Notes personnelles', {
            'fields': ('notes',)
        }),
    )
