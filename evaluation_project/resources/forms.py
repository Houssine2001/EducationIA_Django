from django import forms
from .models import Resource


class ResourceUploadForm(forms.ModelForm):
    """Formulaire pour uploader une ressource"""
    
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'type', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Titre de la ressource'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Description de la ressource (optionnel)',
                'rows': 4
            }),
            'file': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'file-upload'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Vérifier la taille (max 100MB)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('Le fichier ne doit pas dépasser 100 MB.')
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_type = cleaned_data.get('type')
        
        if file and file_type:
            # Auto-détection du type si "other"
            if file_type == 'other':
                if file.name.endswith('.pdf'):
                    cleaned_data['type'] = 'pdf'
                elif file.name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    cleaned_data['type'] = 'video'
                elif file.name.endswith(('.txt', '.doc', '.docx')):
                    cleaned_data['type'] = 'text'
        
        return cleaned_data


class ResourceFilterForm(forms.Form):
    """Formulaire pour filtrer les ressources"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Rechercher...'
        })
    )
    
    type = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les types')] + Resource.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les statuts')] + Resource.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )


class ResourceEditForm(forms.ModelForm):
    """Formulaire pour éditer une ressource"""
    
    class Meta:
        model = Resource
        fields = ['title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }
