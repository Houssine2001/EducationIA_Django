"""
Modèles de données pour la génération automatique d'exercices par IA
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from backend.mongodb_utils import get_mongodb_client
import json
from .fields import CompatibleJSONField
from bson.objectid import ObjectId


class MongoDBCompatibleModel(models.Model):
    """
    Classe de base pour tous les modèles compatibles MongoDB
    Gère correctement les ObjectId pour INSERT et UPDATE
    """
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save pour gérer les ObjectId de MongoDB"""
        from django.conf import settings
        from datetime import datetime
        
        # Si c'est une nouvelle instance (pas encore en DB)
        if self._state.adding:
            # Sauvegarder directement dans MongoDB avec PyMongo
            client = get_mongodb_client()
            db = client[settings.MONGO_DB_NAME]
            collection = db[self._meta.db_table]
            
            # Préparer les données
            data = {}
            for field in self._meta.fields:
                if field.name == 'id':
                    continue
                
                # Gérer les FileField/ImageField
                if isinstance(field, (models.FileField, models.ImageField)):
                    value = getattr(self, field.name, None)
                    data[field.name] = value.name if value else None
                # Gérer les ForeignKey - Convertir ObjectId en string
                elif isinstance(field, models.ForeignKey):
                    # Utiliser directement l'attribut _id pour éviter la requête
                    fk_field_name = f'{field.name}_id'
                    if hasattr(self, fk_field_name):
                        fk_value = getattr(self, fk_field_name, None)
                        if fk_value is not None:
                            # TOUJOURS convertir en string pour compatibilité Django
                            if isinstance(fk_value, ObjectId):
                                data[fk_field_name] = str(fk_value)
                            else:
                                data[fk_field_name] = str(fk_value) if fk_value else None
                else:
                    value = getattr(self, field.name, None)
                    data[field.name] = value
            
            # Ajouter timestamps si nécessaire
            if 'created_at' not in data or data.get('created_at') is None:
                data['created_at'] = datetime.now()
            if 'updated_at' not in data or data.get('updated_at') is None:
                data['updated_at'] = datetime.now()
            
            # Insérer dans MongoDB
            result = collection.insert_one(data)
            self.pk = result.inserted_id
            self._state.adding = False
            self._state.db = 'default'
            client.close()
            
        else:
            # UPDATE : Modifier le document existant dans MongoDB
            client = get_mongodb_client()
            db = client[settings.MONGO_DB_NAME]
            collection = db[self._meta.db_table]
            
            # Préparer les données pour l'update
            data = {}
            for field in self._meta.fields:
                if field.name == 'id':
                    continue
                
                # Gérer les FileField/ImageField
                if isinstance(field, (models.FileField, models.ImageField)):
                    value = getattr(self, field.name, None)
                    data[field.name] = value.name if value else None
                # Gérer les ForeignKey - Convertir ObjectId en string
                elif isinstance(field, models.ForeignKey):
                    # Utiliser directement l'attribut _id pour éviter la requête
                    fk_field_name = f'{field.name}_id'
                    if hasattr(self, fk_field_name):
                        fk_value = getattr(self, fk_field_name, None)
                        if fk_value is not None:
                            # TOUJOURS convertir en string pour compatibilité Django
                            if isinstance(fk_value, ObjectId):
                                data[fk_field_name] = str(fk_value)
                            else:
                                data[fk_field_name] = str(fk_value) if fk_value else None
                else:
                    value = getattr(self, field.name, None)
                    data[field.name] = value
            
            # Mettre à jour updated_at
            data['updated_at'] = datetime.now()
            
            # UPDATE dans MongoDB
            collection.update_one(
                {'_id': self.pk},
                {'$set': data}
            )
            client.close()

    
    def get_int_id(self):
        """
        Convertit l'ObjectId MongoDB en entier pour les URLs
        Utilise les 8 derniers caractères de l'ObjectId en hexadécimal
        """
        if isinstance(self.pk, ObjectId):
            return int(str(self.pk)[-8:], 16)
        return int(self.pk) if self.pk else None


class CourseDocument(MongoDBCompatibleModel):
    """
    Document de cours uploadé par l'enseignant (texte ou PDF)
    """
    DOCUMENT_TYPE_CHOICES = [
        ('text', 'Texte'),
        ('pdf', 'PDF'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'Traitement en cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre du document")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Créateur
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_documents')
    
    # Contenu
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True, null=True, verbose_name="Contenu textuel")  # Texte extrait
    file_path = models.FileField(upload_to='course_documents/', blank=True, null=True)  # Fichier PDF
    
    # Métadonnées académiques
    subject = models.CharField(max_length=100, verbose_name="Matière")
    topic = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sujet spécifique")
    level = models.CharField(max_length=50, blank=True, null=True, verbose_name="Niveau")
    
    # Analyse IA du document
    key_concepts = CompatibleJSONField(default=list, verbose_name="Concepts clés extraits")  # ["concept1", "concept2", ...]
    main_topics = CompatibleJSONField(default=list, verbose_name="Thèmes principaux")
    summary = models.TextField(blank=True, null=True, verbose_name="Résumé généré par IA")
    
    # Statistiques
    word_count = models.IntegerField(default=0, verbose_name="Nombre de mots")
    sentence_count = models.IntegerField(default=0, verbose_name="Nombre de phrases")
    
    # Statut de traitement
    processing_status = models.CharField(
        max_length=20, 
        choices=PROCESSING_STATUS_CHOICES, 
        default='pending',
        verbose_name="Statut de traitement"
    )
    processing_log = models.TextField(blank=True, null=True, verbose_name="Log de traitement")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_documents'
        verbose_name = 'Document de cours'
        verbose_name_plural = 'Documents de cours'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.subject})"


class GeneratedExercise(MongoDBCompatibleModel):
    """
    Exercice généré automatiquement par l'IA à partir d'un document de cours
    """
    EXERCISE_TYPE_CHOICES = [
        ('mcq', 'QCM (Choix Multiple)'),
        ('true_false', 'Vrai/Faux'),
        ('fill_blank', 'Texte à trous'),
        ('short_answer', 'Réponse courte'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('published', 'Publié'),
        ('rejected', 'Rejeté'),
    ]
    
    # Lien avec le document source
    source_document = models.ForeignKey(
        CourseDocument, 
        on_delete=models.CASCADE, 
        related_name='generated_exercises'
    )
    
    # Informations de base
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES)
    question_text = models.TextField(verbose_name="Question")
    
    # Concept/Thème associé
    concept = models.CharField(max_length=200, verbose_name="Concept testé")
    topic = models.CharField(max_length=200, blank=True, null=True, verbose_name="Thème")
    
    # Difficulté (calculée par l'IA)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    
    # Options et réponses (structure JSON)
    # Pour QCM: {"options": ["A", "B", "C", "D"], "correct": "A"}
    # Pour Vrai/Faux: {"correct": true}
    # Pour texte à trous: {"text": "Le soleil est une ___", "correct": "étoile"}
    options_data = CompatibleJSONField(default=dict, verbose_name="Options et réponses")
    
    # Explication de la réponse (générée par IA)
    explanation = models.TextField(blank=True, null=True, verbose_name="Explication")
    
    # Contexte d'extraction
    source_sentence = models.TextField(blank=True, null=True, verbose_name="Phrase source")
    
    # Score de qualité IA (0-1)
    quality_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Score de qualité IA"
    )
    
    # Validation par l'enseignant
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='validated_exercises'
    )
    validation_notes = models.TextField(blank=True, null=True)
    
    # Statistiques d'utilisation
    times_used = models.IntegerField(default=0)
    average_success_rate = models.FloatField(default=0.0)  # Taux de réussite moyen
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'generated_exercises'
        verbose_name = 'Exercice généré'
        verbose_name_plural = 'Exercices générés'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['exercise_type', 'difficulty']),
            models.Index(fields=['status', 'quality_score']),
        ]
    
    def __str__(self):
        return f"{self.get_exercise_type_display()} - {self.concept} ({self.difficulty})"


class GeneratedTest(MongoDBCompatibleModel):
    """
    Test/évaluation créé à partir d'exercices générés
    Pont entre exercise_generator et evaluation
    """
    # Lien avec le document source
    source_document = models.ForeignKey(
        CourseDocument, 
        on_delete=models.CASCADE, 
        related_name='generated_tests'
    )
    
    # Exercices inclus
    exercises = models.ManyToManyField(GeneratedExercise, related_name='included_in_tests')
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre du test")
    description = models.TextField(blank=True, null=True)
    
    # Créateur
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_tests')
    
    # Configuration
    difficulty_distribution = CompatibleJSONField(
        default=dict,
        verbose_name="Distribution de difficulté"
    )  # {"easy": 5, "medium": 10, "hard": 5}
    
    type_distribution = CompatibleJSONField(
        default=dict,
        verbose_name="Distribution des types"
    )  # {"mcq": 15, "true_false": 5}
    
    # Durée suggérée (en minutes)
    suggested_duration = models.IntegerField(default=30, verbose_name="Durée suggérée")
    
    # Lien vers le test dans l'app evaluation (optionnel)
    evaluation_test_id = models.IntegerField(null=True, blank=True)
    
    # Statut
    is_published = models.BooleanField(default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'generated_tests'
        verbose_name = 'Test généré'
        verbose_name_plural = 'Tests générés'
        ordering = ['-created_at']
    
    def __str__(self):
        # Éviter self.exercises.count() pour éviter la récursion
        return f"{self.title}"


class ExerciseGenerationConfig(MongoDBCompatibleModel):
    """
    Configuration pour la génération d'exercices (paramètres par enseignant)
    """
    teacher = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='generation_config'
    )
    
    # Préférences de génération
    default_exercise_count = models.IntegerField(default=10, verbose_name="Nombre d'exercices par défaut")
    
    # Distribution des types (en pourcentage)
    mcq_percentage = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    true_false_percentage = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fill_blank_percentage = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Distribution des difficultés (en pourcentage)
    easy_percentage = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    medium_percentage = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    hard_percentage = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Seuil de qualité minimal
    min_quality_score = models.FloatField(
        default=0.6,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Score de qualité minimal"
    )
    
    # Options avancées
    auto_validate = models.BooleanField(
        default=False, 
        verbose_name="Validation automatique"
    )  # Publier automatiquement les exercices de haute qualité
    
    include_explanations = models.BooleanField(
        default=True, 
        verbose_name="Inclure les explications"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercise_generation_configs'
        verbose_name = 'Configuration de génération'
        verbose_name_plural = 'Configurations de génération'
    
    def __str__(self):
        return f"Config de {self.teacher.username}"


class ExerciseSet(MongoDBCompatibleModel):
    """
    Ensemble d'exercices collectés et prêts à être publiés
    Le prof collecte 4 exercices → crée un set → publie pour les étudiants
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre du set")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Créateur
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_sets')
    
    # Document source
    source_document = models.ForeignKey(
        CourseDocument, 
        on_delete=models.CASCADE, 
        related_name='exercise_sets'
    )
    
    # Exercices inclus (maximum 4-6 exercices par set)
    exercises = models.ManyToManyField(GeneratedExercise, related_name='in_sets')
    
    # Statut de publication
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercise_sets'
        verbose_name = 'Ensemble d\'exercices'
        verbose_name_plural = 'Ensembles d\'exercices'
        ordering = ['-created_at']
    
    def __str__(self):
        # Éviter self.exercises.count() car ça cause une récursion infinie
        # avec notre système MongoDB personnalisé
        return f"{self.title} ({self.status})"
    
    def get_exercise_count(self):
        """Obtenir le nombre d'exercices via MongoDB directement"""
        # Si un count a déjà été calculé et stocké (par la vue), l'utiliser
        if hasattr(self, '_exercise_count'):
            return self._exercise_count
        
        # Sinon, calculer via PyMongo
        from django.conf import settings
        
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': str(self.pk)
        })
        client.close()
        return count
    
    def get_submissions_count(self):
        """Obtenir le nombre de soumissions via MongoDB directement"""
        # Si un count a déjà été calculé et stocké (par la vue), l'utiliser
        if hasattr(self, '_submissions_count'):
            return self._submissions_count
        
        # Sinon, calculer via PyMongo
        from django.conf import settings
        
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        count = db.student_exercise_submissions.count_documents({
            'exercise_set_id': str(self.pk)
        })
        client.close()
        return count
    
    def get_teacher_name(self):
        """Obtenir le nom du teacher en évitant la requête ForeignKey"""
        # Si le nom a déjà été calculé et stocké (par la vue), l'utiliser
        if hasattr(self, '_teacher_name'):
            return self._teacher_name
        
        # Sinon, essayer de récupérer via ForeignKey (peut échouer avec MongoDB)
        try:
            if self.teacher:
                return self.teacher.get_full_name() or self.teacher.username
        except:
            pass
        
        return 'Professeur'
    
    def publish(self):
        """Publier le set pour les étudiants"""
        from django.utils import timezone
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
    
    def unpublish(self):
        """Retirer de la publication"""
        self.status = 'draft'
        self.published_at = None
        self.save()


class StudentExerciseSubmission(MongoDBCompatibleModel):
    """
    Soumission d'un étudiant pour un ExerciseSet
    """
    # Étudiant
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_submissions')
    
    # Set d'exercices
    exercise_set = models.ForeignKey(ExerciseSet, on_delete=models.CASCADE, related_name='submissions')
    
    # Réponses de l'étudiant (JSON)
    # Format: {"exercise_id": "answer", ...}
    answers = CompatibleJSONField(default=dict, verbose_name="Réponses")
    
    # Résultats
    score = models.FloatField(default=0.0, verbose_name="Score (%)")
    correct_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    
    # Temps passé (en secondes)
    time_spent = models.IntegerField(default=0)
    
    # Statut
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_exercise_submissions'
        verbose_name = 'Soumission étudiant'
        verbose_name_plural = 'Soumissions étudiants'
        ordering = ['-started_at']
        unique_together = [['student', 'exercise_set']]
    
    def __str__(self):
        # Éviter les requêtes qui peuvent causer la récursion
        try:
            student_name = self.student.username if hasattr(self, 'student') else 'Unknown'
            set_title = self.exercise_set.title if hasattr(self, 'exercise_set') else 'Unknown'
            return f"{student_name} - {set_title} ({self.score}%)"
        except:
            return f"Submission {self.pk}"
