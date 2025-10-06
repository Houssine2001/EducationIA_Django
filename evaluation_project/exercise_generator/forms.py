"""
Formulaires pour la génération d'exercices
"""
from django import forms
from .models import CourseDocument, ExerciseGenerationConfig


class CourseDocumentForm(forms.ModelForm):
    """
    Formulaire pour uploader un document de cours
    """
    class Meta:
        model = CourseDocument
        fields = ['title', 'description', 'subject', 'topic', 'level', 'document_type', 'content', 'file_path']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Introduction à la photosynthèse'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description courte du document...'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Biologie, Mathématiques, Histoire...'
            }),
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Photosynthèse, Équations du second degré...'
            }),
            'level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 3ème, Seconde, Terminale...'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Collez votre texte de cours ici... (ou uploadez un PDF ci-dessous)'
            }),
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }
        labels = {
            'title': 'Titre du document',
            'description': 'Description',
            'subject': 'Matière',
            'topic': 'Sujet spécifique',
            'level': 'Niveau scolaire',
            'document_type': 'Type de document',
            'content': 'Contenu textuel',
            'file_path': 'Fichier PDF (optionnel)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs content et file_path optionnels
        self.fields['content'].required = False
        self.fields['file_path'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        content = cleaned_data.get('content')
        file_path = cleaned_data.get('file_path')
        
        # Validation : soit du texte, soit un PDF
        if document_type == 'text':
            if not content:
                self.add_error('content', "Vous devez fournir un contenu textuel pour un document de type 'Texte'.")
        
        if document_type == 'pdf':
            if not file_path:
                self.add_error('file_path', "Vous devez uploader un fichier PDF pour un document de type 'PDF'.")
        
        # Au moins l'un des deux doit être fourni
        if not content and not file_path:
            raise forms.ValidationError("Vous devez fournir soit un contenu textuel, soit un fichier PDF.")
        
        return cleaned_data


class GenerationConfigForm(forms.ModelForm):
    """
    Formulaire de configuration pour la génération d'exercices
    """
    class Meta:
        model = ExerciseGenerationConfig
        fields = [
            'default_exercise_count',
            'mcq_percentage',
            'true_false_percentage',
            'fill_blank_percentage',
            'easy_percentage',
            'medium_percentage',
            'hard_percentage',
            'min_quality_score',
            'auto_validate',
            'include_explanations'
        ]
        widgets = {
            'default_exercise_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 50
            }),
            'mcq_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'true_false_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'fill_blank_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'easy_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'medium_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'hard_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'min_quality_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 1,
                'step': 0.1
            }),
            'auto_validate': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'include_explanations': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'default_exercise_count': 'Nombre d\'exercices par défaut',
            'mcq_percentage': '% de QCM',
            'true_false_percentage': '% de Vrai/Faux',
            'fill_blank_percentage': '% de Texte à trous',
            'easy_percentage': '% Facile',
            'medium_percentage': '% Moyen',
            'hard_percentage': '% Difficile',
            'min_quality_score': 'Score de qualité minimal (0-1)',
            'auto_validate': 'Validation automatique',
            'include_explanations': 'Inclure les explications'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validation : les pourcentages de types doivent faire 100%
        mcq = cleaned_data.get('mcq_percentage', 0)
        tf = cleaned_data.get('true_false_percentage', 0)
        fb = cleaned_data.get('fill_blank_percentage', 0)
        
        if mcq + tf + fb != 100:
            raise forms.ValidationError(
                "La somme des pourcentages de types d'exercices doit être égale à 100%."
            )
        
        # Validation : les pourcentages de difficultés doivent faire 100%
        easy = cleaned_data.get('easy_percentage', 0)
        medium = cleaned_data.get('medium_percentage', 0)
        hard = cleaned_data.get('hard_percentage', 0)
        
        if easy + medium + hard != 100:
            raise forms.ValidationError(
                "La somme des pourcentages de difficultés doit être égale à 100%."
            )
        
        return cleaned_data


class TestCreationForm(forms.Form):
    """
    Formulaire pour créer un test à partir d'exercices générés
    """
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Test de biologie - Chapitre 3'
        }),
        label='Titre du test'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description du test...'
        }),
        label='Description'
    )
    
    exercise_ids = forms.CharField(
        widget=forms.HiddenInput(),
        label='IDs des exercices'
    )
    
    def clean_exercise_ids(self):
        exercise_ids = self.cleaned_data.get('exercise_ids', '')
        
        if not exercise_ids:
            raise forms.ValidationError("Vous devez sélectionner au moins un exercice.")
        
        try:
            # Conversion en liste d'entiers
            ids = [int(id.strip()) for id in exercise_ids.split(',') if id.strip()]
            
            if len(ids) == 0:
                raise forms.ValidationError("Vous devez sélectionner au moins un exercice.")
            
            return ids
        except ValueError:
            raise forms.ValidationError("Format d'IDs invalide.")


class QuickGenerationForm(forms.Form):
    """
    Formulaire rapide pour générer des exercices
    """
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Collez votre texte de cours ici...'
        }),
        label='Texte du cours'
    )
    
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Biologie'
        }),
        label='Matière'
    )
    
    num_exercises = forms.IntegerField(
        min_value=5,
        max_value=30,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        label='Nombre d\'exercices'
    )
    
    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        
        if len(text.split()) < 50:
            raise forms.ValidationError(
                "Le texte est trop court. Fournissez au moins 50 mots."
            )
        
        return text
