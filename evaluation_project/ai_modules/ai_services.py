"""
Service d'Intelligence Artificielle pour l'évaluation
Utilise l'API gratuite de Hugging Face
"""
import requests
import json
from django.conf import settings


class HuggingFaceAI:
    """
    Service d'IA utilisant Hugging Face Inference API (gratuite)
    """
    
    # URL de l'API Hugging Face
    API_URL = "https://api-inference.huggingface.co/models/"
    
    # Modèles recommandés (gratuits)
    MODELS = {
        'text_generation': 'mistralai/Mistral-7B-Instruct-v0.1',
        'sentiment': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
        'zero_shot': 'facebook/bart-large-mnli',
        'summarization': 'facebook/bart-large-cnn',
        'question_answering': 'deepset/roberta-base-squad2'
    }
    
    def __init__(self, api_token=None):
        """
        Initialise le service IA
        
        Args:
            api_token: Token API Hugging Face (optionnel pour démo)
        """
        self.api_token = api_token or getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        self.headers = {}
        if self.api_token:
            self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def query_model(self, model_name, payload):
        """
        Envoie une requête à un modèle Hugging Face
        
        Args:
            model_name: Nom du modèle
            payload: Données à envoyer
            
        Returns:
            dict: Réponse du modèle
        """
        url = self.API_URL + model_name
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API Hugging Face: {e}")
            return None
    
    def generate_text(self, prompt, max_length=200):
        """
        Génère du texte avec un modèle de langage
        
        Args:
            prompt: Texte d'entrée
            max_length: Longueur maximale
            
        Returns:
            str: Texte généré
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        result = self.query_model(self.MODELS['text_generation'], payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').replace(prompt, '').strip()
        
        return None
    
    def analyze_sentiment(self, text):
        """
        Analyse le sentiment d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            dict: Score de sentiment
        """
        payload = {"inputs": text}
        result = self.query_model(self.MODELS['sentiment'], payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        
        return None


class EssayGrader:
    """
    Service de correction automatique pour les questions ouvertes
    """
    
    def __init__(self):
        self.ai = HuggingFaceAI()
    
    def grade_essay(self, question, student_answer, max_points=10):
        """
        Corrige une question de rédaction avec IA
        
        Args:
            question: Instance de Question
            student_answer: Réponse de l'étudiant
            max_points: Points maximum
            
        Returns:
            dict: Résultat de la correction
        """
        # Créer un prompt pour l'IA
        prompt = f"""Tu es un correcteur d'examens. Évalue cette réponse sur {max_points} points.

Question: {question.question_text}

Réponse attendue (guide): {question.explanation or 'Non spécifié'}

Réponse de l'étudiant: {student_answer}

Fournis:
1. Une note sur {max_points}
2. Des points positifs
3. Des points à améliorer
4. Un feedback constructif

Format: Note: X/{max_points}
Points positifs: ...
À améliorer: ...
Feedback: ..."""

        # Générer l'évaluation avec l'IA
        ai_response = self.ai.generate_text(prompt, max_length=300)
        
        if not ai_response:
            # Fallback: correction basique
            return self._basic_essay_grading(student_answer, max_points)
        
        # Parser la réponse de l'IA
        return self._parse_ai_grading(ai_response, max_points)
    
    def _basic_essay_grading(self, answer, max_points):
        """
        Correction basique sans IA (fallback)
        """
        word_count = len(answer.split())
        
        # Scoring simple basé sur la longueur
        if word_count < 20:
            score = max_points * 0.3
            feedback = "Réponse trop courte. Développez davantage."
        elif word_count < 50:
            score = max_points * 0.5
            feedback = "Réponse acceptable mais pourrait être plus détaillée."
        elif word_count < 100:
            score = max_points * 0.7
            feedback = "Bonne réponse. Quelques détails supplémentaires seraient appréciés."
        else:
            score = max_points * 0.85
            feedback = "Réponse complète et détaillée."
        
        return {
            'points_earned': round(score, 2),
            'feedback': feedback,
            'positive_points': ["Réponse fournie"],
            'improvements': ["Correction manuelle recommandée"],
            'requires_manual_review': True
        }
    
    def _parse_ai_grading(self, ai_response, max_points):
        """
        Parse la réponse de l'IA pour extraire la note et le feedback
        """
        try:
            # Extraction simple de la note
            lines = ai_response.split('\n')
            score = max_points * 0.7  # Score par défaut
            feedback = ai_response
            
            for line in lines:
                if 'Note:' in line or 'note:' in line.lower():
                    # Extraire le chiffre
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        score = min(float(numbers[0]), max_points)
            
            return {
                'points_earned': score,
                'feedback': feedback,
                'positive_points': ["Évaluation IA"],
                'improvements': ["Voir feedback détaillé"],
                'requires_manual_review': False
            }
        except Exception as e:
            print(f"Erreur parsing IA: {e}")
            return self._basic_essay_grading("", max_points)


class FeedbackGenerator:
    """
    Génère du feedback personnalisé avec IA
    """
    
    def __init__(self):
        self.ai = HuggingFaceAI()
    
    def generate_personalized_feedback(self, student_profile, result):
        """
        Génère un feedback personnalisé basé sur le profil et les résultats
        
        Args:
            student_profile: Instance UserProfile
            result: Instance Result
            
        Returns:
            dict: Feedback personnalisé
        """
        # Créer un prompt contextuel
        prompt = f"""Tu es un tuteur pédagogue. Génère un feedback personnalisé pour cet étudiant.

Score obtenu: {result.percentage_score}%
Matière: {result.test.subject}
Points forts de l'étudiant: {', '.join(student_profile.strengths) if student_profile.strengths else 'Non définis'}
Points faibles: {', '.join(student_profile.weaknesses) if student_profile.weaknesses else 'Non définis'}

Fournis un feedback encourageant et 3 recommandations concrètes."""

        ai_feedback = self.ai.generate_text(prompt, max_length=250)
        
        if not ai_feedback:
            return self._generate_basic_feedback(student_profile, result)
        
        return {
            'overall_feedback': ai_feedback,
            'encouragement': self._extract_encouragement(result.percentage_score),
            'ai_generated': True
        }
    
    def _generate_basic_feedback(self, profile, result):
        """
        Génère un feedback basique sans IA
        """
        score = result.percentage_score
        
        if score >= 90:
            feedback = "Excellent travail ! Vous maîtrisez très bien le sujet."
        elif score >= 75:
            feedback = "Très bon travail ! Continuez sur cette voie."
        elif score >= 60:
            feedback = "Bon travail. Quelques points à renforcer."
        elif score >= 50:
            feedback = "Travail acceptable. Il y a des lacunes à combler."
        else:
            feedback = "Vous devez travailler davantage. Ne vous découragez pas !"
        
        return {
            'overall_feedback': feedback,
            'encouragement': "Continuez vos efforts !",
            'ai_generated': False
        }
    
    def _extract_encouragement(self, score):
        """
        Génère un message d'encouragement basé sur le score
        """
        if score >= 90:
            return "🌟 Performance exceptionnelle !"
        elif score >= 75:
            return "👏 Très bonne performance !"
        elif score >= 60:
            return "👍 Bonne performance, continuez !"
        elif score >= 50:
            return "💪 Vous progressez, ne lâchez rien !"
        else:
            return "🎯 Gardez confiance, vous allez y arriver !"


class WeaknessAnalyzer:
    """
    Analyse les points faibles des étudiants avec IA
    """
    
    def __init__(self):
        self.ai = HuggingFaceAI()
    
    def identify_weaknesses(self, student_profile, recent_results):
        """
        Identifie les points faibles d'un étudiant
        
        Args:
            student_profile: Instance UserProfile
            recent_results: QuerySet de Result récents
            
        Returns:
            dict: Analyse des faiblesses
        """
        # Analyser les compétences sur plusieurs tests
        skills_aggregate = {}
        
        for result in recent_results:
            for skill, performance in result.skills_breakdown.items():
                if skill not in skills_aggregate:
                    skills_aggregate[skill] = []
                skills_aggregate[skill].append(performance['percentage'])
        
        # Identifier les compétences faibles (moyenne < 60%)
        weaknesses = []
        strengths = []
        
        for skill, scores in skills_aggregate.items():
            avg_score = sum(scores) / len(scores)
            
            if avg_score < 60:
                weaknesses.append({
                    'skill': skill,
                    'average_score': round(avg_score, 2),
                    'tests_count': len(scores),
                    'trend': self._calculate_trend(scores)
                })
            elif avg_score >= 80:
                strengths.append({
                    'skill': skill,
                    'average_score': round(avg_score, 2)
                })
        
        # Générer des recommandations avec IA
        recommendations = self._generate_recommendations(weaknesses)
        
        return {
            'weaknesses': weaknesses,
            'strengths': strengths,
            'recommendations': recommendations,
            'overall_trend': self._calculate_overall_trend(recent_results)
        }
    
    def _calculate_trend(self, scores):
        """
        Calcule la tendance (amélioration/stagnation/régression)
        """
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Comparer les 2 derniers scores
        if scores[-1] > scores[-2]:
            return 'improving'
        elif scores[-1] < scores[-2]:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_overall_trend(self, results):
        """
        Calcule la tendance générale de l'étudiant
        """
        # Accepte liste ou queryset
        results_list = list(results) if hasattr(results, 'count') else results
        
        if len(results_list) < 2:
            return 'insufficient_data'
        
        scores = [r.percentage_score for r in results_list]
        
        # Calculer la différence entre premier et dernier
        improvement = scores[-1] - scores[0]
        
        if improvement > 10:
            return 'significant_improvement'
        elif improvement > 0:
            return 'slight_improvement'
        elif improvement < -10:
            return 'significant_decline'
        elif improvement < 0:
            return 'slight_decline'
        else:
            return 'stable'
    
    def _generate_recommendations(self, weaknesses):
        """
        Génère des recommandations pour les faiblesses identifiées
        """
        recommendations = []
        
        for weakness in weaknesses:
            skill = weakness['skill']
            score = weakness['average_score']
            
            if score < 40:
                recommendations.append({
                    'skill': skill,
                    'priority': 'high',
                    'suggestion': f"Révision complète de {skill} recommandée. Commencez par les bases.",
                    'study_time': '30-45 min/jour'
                })
            elif score < 60:
                recommendations.append({
                    'skill': skill,
                    'priority': 'medium',
                    'suggestion': f"Pratiquez régulièrement {skill} avec des exercices ciblés.",
                    'study_time': '15-30 min/jour'
                })
        
        return recommendations


# Fonction utilitaire pour obtenir les services
def get_ai_services():
    """
    Retourne les instances des services IA
    """
    return {
        'essay_grader': EssayGrader(),
        'feedback_generator': FeedbackGenerator(),
        'weakness_analyzer': WeaknessAnalyzer()
    }
