"""
Tests unitaires pour le générateur d'exercices IA
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import CourseDocument, GeneratedExercise, GeneratedTest, ExerciseGenerationConfig
from .ai_document_analyzer import DocumentAnalyzer
from .ai_exercise_generator import ExerciseGenerator
from .services import ExerciseGenerationService


class DocumentAnalyzerTestCase(TestCase):
    """Tests pour l'analyseur de documents"""
    
    def setUp(self):
        self.analyzer = DocumentAnalyzer()
        self.sample_text = """
        La photosynthèse est le processus par lequel les plantes vertes 
        transforment la lumière solaire en énergie chimique. Ce processus 
        se déroule dans les chloroplastes. La photosynthèse nécessite de 
        l'eau, du dioxyde de carbone et de la lumière. Les produits sont 
        le glucose et l'oxygène.
        """
    
    def test_analyze_document(self):
        """Test de l'analyse complète d'un document"""
        result = self.analyzer.analyze_document(self.sample_text)
        
        # Vérifications
        self.assertIsInstance(result, dict)
        self.assertIn('key_concepts', result)
        self.assertIn('main_topics', result)
        self.assertIn('word_count', result)
        self.assertTrue(result['word_count'] > 0)
    
    def test_extract_sentences(self):
        """Test de l'extraction de phrases"""
        sentences = self.analyzer._extract_sentences(self.sample_text)
        
        self.assertIsInstance(sentences, list)
        self.assertTrue(len(sentences) > 0)
    
    def test_extract_keywords(self):
        """Test de l'extraction de mots-clés"""
        keywords = self.analyzer._extract_keywords(self.sample_text, top_n=5)
        
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)


class ExerciseGeneratorTestCase(TestCase):
    """Tests pour le générateur d'exercices"""
    
    def setUp(self):
        self.generator = ExerciseGenerator()
        self.sample_text = """
        La photosynthèse est le processus par lequel les plantes vertes 
        transforment la lumière solaire en énergie chimique. Ce processus 
        se déroule dans les chloroplastes. La photosynthèse nécessite de 
        l'eau, du dioxyde de carbone et de la lumière. Les produits sont 
        le glucose et l'oxygène. Ce processus est vital pour la vie.
        """
    
    def test_generate_exercises(self):
        """Test de la génération d'exercices"""
        config = {
            'total_exercises': 5,
            'mcq_percentage': 40,
            'true_false_percentage': 40,
            'fill_blank_percentage': 20,
            'easy_percentage': 50,
            'medium_percentage': 50,
            'hard_percentage': 0,
            'min_quality_score': 0.3
        }
        
        result = self.generator.generate_exercises_from_document(
            self.sample_text,
            config
        )
        
        # Vérifications
        self.assertIsInstance(result, dict)
        self.assertIn('exercises', result)
        self.assertIn('stats', result)
        self.assertTrue(len(result['exercises']) > 0)


class CourseDocumentModelTestCase(TestCase):
    """Tests pour le modèle CourseDocument"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testteacher',
            password='testpass123'
        )
    
    def test_create_document(self):
        """Test de création d'un document"""
        doc = CourseDocument.objects.create(
            title="Test Document",
            content="Contenu de test pour la génération d'exercices.",
            subject="Test",
            teacher=self.user,
            document_type='text'
        )
        
        self.assertEqual(doc.title, "Test Document")
        self.assertEqual(doc.teacher, self.user)
        self.assertEqual(doc.processing_status, 'pending')


class GeneratedExerciseModelTestCase(TestCase):
    """Tests pour le modèle GeneratedExercise"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testteacher',
            password='testpass123'
        )
        self.document = CourseDocument.objects.create(
            title="Test Doc",
            content="Test content",
            subject="Test",
            teacher=self.user
        )
    
    def test_create_mcq_exercise(self):
        """Test de création d'un QCM"""
        exercise = GeneratedExercise.objects.create(
            source_document=self.document,
            exercise_type='mcq',
            question_text="Qu'est-ce que la photosynthèse ?",
            concept="Photosynthèse",
            difficulty='easy',
            options_data={
                'options': {
                    'A': 'Réponse A',
                    'B': 'Réponse B',
                    'C': 'Réponse C',
                    'D': 'Réponse D'
                },
                'correct': 'A'
            },
            quality_score=0.8
        )
        
        self.assertEqual(exercise.exercise_type, 'mcq')
        self.assertEqual(exercise.difficulty, 'easy')
        self.assertTrue(exercise.quality_score > 0)


class ExerciseGenerationServiceTestCase(TestCase):
    """Tests pour le service de génération"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testteacher',
            password='testpass123'
        )
        self.service = ExerciseGenerationService()
    
    def test_process_document(self):
        """Test du traitement complet d'un document"""
        document = CourseDocument.objects.create(
            title="Test Document",
            content="""
            La photosynthèse est le processus par lequel les plantes vertes 
            transforment la lumière solaire en énergie chimique. Ce processus 
            se déroule dans les chloroplastes. La photosynthèse nécessite de 
            l'eau, du dioxyde de carbone et de la lumière. Les produits sont 
            le glucose et l'oxygène. Ce processus est vital pour la vie.
            """,
            subject="Biologie",
            teacher=self.user,
            document_type='text'
        )
        
        config = {
            'total_exercises': 3,
            'mcq_percentage': 34,
            'true_false_percentage': 33,
            'fill_blank_percentage': 33,
            'min_quality_score': 0.3
        }
        
        result = self.service.process_document(document, config)
        
        # Vérifications
        self.assertTrue(result['success'])
        self.assertIn('exercises', result)
        self.assertTrue(len(result['exercises']) > 0)
        
        # Vérifier que le document a été mis à jour
        document.refresh_from_db()
        self.assertEqual(document.processing_status, 'completed')


# Fonction pour exécuter tous les tests
def run_all_tests():
    """
    Fonction utilitaire pour exécuter tous les tests
    Usage : python manage.py shell -c "from exercise_generator.tests import run_all_tests; run_all_tests()"
    """
    import unittest
    from django.test.runner import DiscoverRunner
    
    runner = DiscoverRunner()
    test_suite = runner.build_suite(['exercise_generator'])
    unittest.TextTestRunner().run(test_suite)
