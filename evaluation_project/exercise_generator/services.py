"""
Service principal pour la génération automatique d'exercices
Orchestre l'analyse de documents et la génération d'exercices
"""
from typing import Dict, List, Optional
from django.contrib.auth.models import User
from backend.mongodb_utils import get_mongodb_client
from .models import (
    CourseDocument, 
    GeneratedExercise, 
    GeneratedTest,
    ExerciseGenerationConfig
)
from .ai_document_analyzer import DocumentAnalyzer
from .ai_exercise_generator import ExerciseGenerator
from .pdf_extractor import PDFTextExtractor


class ExerciseGenerationService:
    """
    Service principal pour la génération d'exercices
    """
    
    def __init__(self):
        self.document_analyzer = DocumentAnalyzer()
        self.exercise_generator = ExerciseGenerator()
        self.pdf_extractor = PDFTextExtractor()
    
    def process_document(
        self,
        document: CourseDocument,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        Traite un document de cours et génère des exercices
        
        Args:
            document: Instance de CourseDocument
            config: Configuration de génération (optionnelle)
            
        Returns:
            Dict avec les résultats du traitement
        """
        try:
            # Mise à jour du statut
            document.processing_status = 'processing'
            document.save()
            
            # Extraction du texte si nécessaire (PDF)
            if document.document_type == 'pdf' and document.file_path:
                text = self._extract_text_from_pdf(document)
                if not text or "Erreur" in text:
                    document.processing_status = 'failed'
                    document.processing_log = text
                    document.save()
                    return {'success': False, 'error': text}
                
                document.content = text
                document.save()
            
            # Analyse du document
            analysis_result = self.document_analyzer.analyze_document(document.content)
            
            # Mise à jour des informations du document
            document.key_concepts = analysis_result['key_concepts']
            document.main_topics = analysis_result['main_topics']
            document.summary = analysis_result['summary']
            document.word_count = analysis_result['word_count']
            document.sentence_count = analysis_result['sentence_count']
            document.save()
            
            # Récupération de la configuration
            if config is None:
                config = self._get_teacher_config(document.teacher)
            
            # Génération des exercices
            generation_result = self.exercise_generator.generate_exercises_from_document(
                document.content,
                config
            )
            
            # Sauvegarde des exercices générés
            saved_exercises = self._save_generated_exercises(
                document,
                generation_result['exercises']
            )
            
            # Mise à jour du statut
            document.processing_status = 'completed'
            document.processing_log = (
                f"Analyse terminée. {len(saved_exercises)} exercices générés. "
                f"Stats: {generation_result['stats']}"
            )
            document.save()
            
            return {
                'success': True,
                'document': document,
                'exercises': saved_exercises,
                'analysis': analysis_result,
                'stats': generation_result['stats']
            }
            
        except Exception as e:
            # En cas d'erreur
            document.processing_status = 'failed'
            document.processing_log = f"Erreur : {str(e)}"
            document.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text_from_pdf(self, document: CourseDocument) -> str:
        """
        Extrait le texte d'un PDF uploadé
        """
        if document.file_path:
            try:
                # Extraction depuis le chemin du fichier
                return self.pdf_extractor.extract_text_from_file(document.file_path)
            except Exception as e:
                return f"Erreur d'extraction PDF : {str(e)}"
        return ""
    
    def _get_teacher_config(self, teacher: User) -> Dict:
        """
        Récupère la configuration de génération de l'enseignant
        """
        try:
            config_obj = ExerciseGenerationConfig.objects.get(teacher=teacher)
            
            return {
                'total_exercises': config_obj.default_exercise_count,
                'mcq_percentage': config_obj.mcq_percentage,
                'true_false_percentage': config_obj.true_false_percentage,
                'fill_blank_percentage': config_obj.fill_blank_percentage,
                'easy_percentage': config_obj.easy_percentage,
                'medium_percentage': config_obj.medium_percentage,
                'hard_percentage': config_obj.hard_percentage,
                'min_quality_score': config_obj.min_quality_score
            }
        except ExerciseGenerationConfig.DoesNotExist:
            # Configuration par défaut
            return {
                'total_exercises': 10,
                'mcq_percentage': 50,
                'true_false_percentage': 30,
                'fill_blank_percentage': 20,
                'easy_percentage': 30,
                'medium_percentage': 50,
                'hard_percentage': 20,
                'min_quality_score': 0.6
            }
    
    def _save_generated_exercises(
        self,
        document: CourseDocument,
        exercises: List[Dict]
    ) -> List[GeneratedExercise]:
        """
        Sauvegarde les exercices générés en base de données
        """
        saved_exercises = []
        
        for exercise_data in exercises:
            try:
                # Préparation des données selon le type
                exercise_type = exercise_data['type']
                
                if exercise_type == 'mcq':
                    options_data = {
                        'options': exercise_data['options'],
                        'correct': exercise_data['correct_answer']
                    }
                elif exercise_type == 'true_false':
                    options_data = {
                        'correct': exercise_data['correct_answer']
                    }
                elif exercise_type == 'fill_blank':
                    options_data = {
                        'text': exercise_data['text'],
                        'correct': exercise_data['correct_answer']
                    }
                else:
                    options_data = {}
                
                # Création de l'exercice via PyMongo (contourne bug ObjectId)
                from django.conf import settings
                from bson import ObjectId as BsonObjectId
                from datetime import datetime
                
                client = get_mongodb_client()
                db = client[settings.MONGO_DB_NAME]
                
                exercise_doc = {
                    'source_document_id': document.pk,  # ObjectId du document
                    'exercise_type': exercise_type,
                    'question_text': exercise_data['question'],
                    'concept': exercise_data.get('concept', 'Concept général'),
                    'topic': document.topic or document.subject,
                    'difficulty': exercise_data.get('difficulty', 'medium'),
                    'options_data': options_data,
                    'explanation': exercise_data.get('explanation', ''),
                    'source_sentence': exercise_data.get('source_sentence', ''),
                    'quality_score': exercise_data.get('quality_score', 0.5),
                    'status': 'draft',
                    'validated_by_id': None,
                    'validation_notes': None,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                }
                
                # Insérer directement dans MongoDB
                result = db.generated_exercises.insert_one(exercise_doc)
                
                # Créer instance Django (retirer _id du dict)
                exercise_id = exercise_doc.pop('_id', None)  # Retirer _id si MongoDB l'a ajouté
                exercise = GeneratedExercise(**exercise_doc)
                exercise.pk = result.inserted_id
                exercise._state.adding = False
                exercise._state.db = 'default'
                
                saved_exercises.append(exercise)
                
            except Exception as e:
                print(f"Erreur lors de la sauvegarde d'un exercice : {e}")
                continue
        
        return saved_exercises
    
    def create_test_from_exercises(
        self,
        document: CourseDocument,
        teacher: User,
        exercise_ids: List[int],
        title: str,
        description: str = ""
    ) -> GeneratedTest:
        """
        Crée un test à partir d'exercices sélectionnés
        """
        # Récupération des exercices
        exercises = GeneratedExercise.objects.filter(
            id__in=exercise_ids,
            source_document=document
        )
        
        # Calcul des distributions
        type_distribution = {}
        difficulty_distribution = {}
        
        for exercise in exercises:
            # Distribution des types
            ex_type = exercise.exercise_type
            type_distribution[ex_type] = type_distribution.get(ex_type, 0) + 1
            
            # Distribution des difficultés
            difficulty = exercise.difficulty
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        # Calcul de la durée suggérée (2 min par QCM, 1 min par V/F, 1.5 min par texte à trous)
        duration = (
            type_distribution.get('mcq', 0) * 2 +
            type_distribution.get('true_false', 0) * 1 +
            type_distribution.get('fill_blank', 0) * 1.5
        )
        
        # Création du test
        test = GeneratedTest.objects.create(
            source_document=document,
            teacher=teacher,
            title=title,
            description=description,
            difficulty_distribution=difficulty_distribution,
            type_distribution=type_distribution,
            suggested_duration=int(duration),
            is_published=False
        )
        
        # Ajout des exercices
        test.exercises.set(exercises)
        
        return test
    
    def export_to_evaluation_app(self, generated_test: GeneratedTest) -> Optional[int]:
        """
        Exporte un test généré vers l'application evaluation
        Crée un Test dans l'app evaluation avec les questions
        
        Returns:
            ID du test créé dans evaluation, ou None en cas d'erreur
        """
        try:
            from evaluation.models import Test, Question
            
            # Création du test dans evaluation
            test = Test.objects.create(
                title=generated_test.title,
                description=generated_test.description or "Test généré automatiquement par IA",
                subject=generated_test.source_document.subject,
                topic=generated_test.source_document.topic,
                created_by=generated_test.teacher,
                difficulty='medium',  # Par défaut
                duration=generated_test.suggested_duration,
                total_points=generated_test.exercises.count() * 10,  # 10 points par question
                passing_score=60,
                status='published'
            )
            
            # Création des questions
            for exercise in generated_test.exercises.all():
                # Conversion du type
                question_type_map = {
                    'mcq': 'multiple_choice',
                    'true_false': 'true_false',
                    'fill_blank': 'short_answer'
                }
                question_type = question_type_map.get(exercise.exercise_type, 'multiple_choice')
                
                # Préparation des options
                if exercise.exercise_type == 'mcq':
                    options_list = [
                        exercise.options_data['options']['A'],
                        exercise.options_data['options']['B'],
                        exercise.options_data['options']['C'],
                        exercise.options_data['options']['D']
                    ]
                    correct_answer = exercise.options_data['correct']
                elif exercise.exercise_type == 'true_false':
                    options_list = ['Vrai', 'Faux']
                    correct_answer = 'Vrai' if exercise.options_data['correct'] else 'Faux'
                else:
                    options_list = []
                    correct_answer = exercise.options_data.get('correct', '')
                
                # Création de la question
                Question.objects.create(
                    test=test,
                    question_text=exercise.question_text,
                    question_type=question_type,
                    options=options_list,
                    correct_answer=correct_answer,
                    points=10,
                    explanation=exercise.explanation,
                    difficulty=exercise.difficulty,
                    order=list(generated_test.exercises.all()).index(exercise) + 1
                )
            
            # Mise à jour du lien
            generated_test.evaluation_test_id = test.id
            generated_test.is_published = True
            generated_test.save()
            
            return test.id
            
        except Exception as e:
            print(f"Erreur lors de l'export vers evaluation : {e}")
            return None
    
    def validate_exercises(
        self,
        exercise_ids: List[int],
        validator: User,
        status: str = 'validated',
        notes: str = ""
    ):
        """
        Valide ou rejette des exercices générés
        """
        exercises = GeneratedExercise.objects.filter(id__in=exercise_ids)
        
        for exercise in exercises:
            exercise.status = status
            exercise.validated_by = validator
            exercise.validation_notes = notes
            exercise.save()
        
        return exercises
