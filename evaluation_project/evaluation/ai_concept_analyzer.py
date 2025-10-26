"""
Analyseur IA avancé pour l'analyse détaillée des concepts
Utilise des modèles IA puissants pour générer des analyses précises
"""
import json
import requests
from typing import Dict, List
from django.conf import settings


class AIConceptAnalyzer:
    """
    Utilise l'IA pour analyser en profondeur les performances par concept
    """
    
    def __init__(self):
        """Initialise l'analyseur IA"""
        # Utiliser Mistral-7B pour des analyses détaillées
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.api_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        self.headers = {}
        if self.api_token:
            self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def analyze_test_performance(self, test_name: str, subject: str, 
                                 questions_data: List[Dict], score: float) -> Dict:
        """
        Analyse en profondeur les performances sur un test spécifique
        
        Args:
            test_name: Nom du test
            subject: Matière du test
            questions_data: Liste des questions avec réponses
                Format: [{'question': str, 'concept': str, 'is_correct': bool, 'student_answer': str, 'correct_answer': str}]
            score: Score global (%)
            
        Returns:
            Dict avec analysis détaillée: {
                'strengths': List[str],  # Points forts détaillés
                'weaknesses': List[str],  # Points faibles détaillés
                'recommendations': List[str],  # Recommandations spécifiques
                'detailed_feedback': str  # Feedback narratif
            }
        """
        # Préparer le prompt pour l'IA
        prompt = self._build_analysis_prompt(test_name, subject, questions_data, score)
        
        try:
            # Appeler l'API Hugging Face
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 800,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraire le texte généré
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                else:
                    generated_text = result.get('generated_text', '')
                
                # Parser la réponse de l'IA
                analysis = self._parse_ai_response(generated_text)
                # Valider et nettoyer l'analyse
                cleaned_analysis = self._validate_and_clean_analysis(analysis, questions_data, subject)
                # Ajouter les métadonnées du test
                cleaned_analysis['test_name'] = test_name
                cleaned_analysis['subject'] = subject
                cleaned_analysis['score'] = score
                return cleaned_analysis
            else:
                # Fallback en cas d'erreur API
                analysis = self._generate_basic_analysis(questions_data, score, subject)
                cleaned_analysis = self._validate_and_clean_analysis(analysis, questions_data, subject)
                # Ajouter les métadonnées du test
                cleaned_analysis['test_name'] = test_name
                cleaned_analysis['subject'] = subject
                cleaned_analysis['score'] = score
                return cleaned_analysis
        
        except Exception as e:
            print(f"Erreur appel IA: {e}")
            # Fallback en cas d'erreur
            analysis = self._generate_basic_analysis(questions_data, score, subject)
            cleaned_analysis = self._validate_and_clean_analysis(analysis, questions_data, subject)
            # Ajouter les métadonnées du test
            cleaned_analysis['test_name'] = test_name
            cleaned_analysis['subject'] = subject
            cleaned_analysis['score'] = score
            return cleaned_analysis
    
    def _build_analysis_prompt(self, test_name: str, subject: str, 
                               questions_data: List[Dict], score: float) -> str:
        """
        Construit le prompt pour l'analyse IA
        """
        # Analyser les réponses
        correct_concepts = []
        incorrect_concepts = []
        
        for q in questions_data:
            concept = q.get('concept', 'Général')
            if q.get('is_correct'):
                correct_concepts.append(concept)
            else:
                incorrect_concepts.append(concept)
        
        # Compter les occurrences
        from collections import Counter
        correct_counts = Counter(correct_concepts)
        incorrect_counts = Counter(incorrect_concepts)
        
        # Construire le prompt
        prompt = f"""[INST] Tu es un expert pédagogique qui analyse les performances d'un étudiant.

Test: {test_name}
Matière: {subject}
Score global: {score:.1f}%
Nombre de questions: {len(questions_data)}

Concepts maîtrisés (réponses correctes):
"""
        
        if correct_counts:
            for concept, count in correct_counts.most_common(5):
                prompt += f"- {concept} ({count} question{'s' if count > 1 else ''} correcte{'s' if count > 1 else ''})\n"
        else:
            prompt += "- Aucun concept maîtrisé\n"
        
        prompt += "\nConcepts à améliorer (réponses incorrectes):\n"
        
        if incorrect_counts:
            for concept, count in incorrect_counts.most_common(5):
                prompt += f"- {concept} ({count} question{'s' if count > 1 else ''} incorrecte{'s' if count > 1 else ''})\n"
        else:
            prompt += "- Aucune erreur\n"
        
        prompt += f"""
Génère une analyse DÉTAILLÉE et PRÉCISE au format JSON suivant:
{{
    "strengths": ["Point fort 1", "Point fort 2", "Point fort 3"],
    "weaknesses": ["Point faible 1", "Point faible 2", "Point faible 3"],
    "recommendations": ["Recommandation 1", "Recommandation 2", "Recommandation 3"],
    "feedback": "Feedback narratif détaillé sur la performance globale"
}}

IMPORTANT:
- Les points forts doivent être SPÉCIFIQUES aux concepts maîtrisés
- Les points faibles doivent identifier PRÉCISÉMENT les lacunes
- Les recommandations doivent être ACTIONNABLES et CONCRÈTES
- Le feedback doit être motivant mais honnête

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire. [/INST]
"""
        
        return prompt
    
    def _parse_ai_response(self, generated_text: str) -> Dict:
        """
        Parse la réponse JSON de l'IA
        """
        try:
            # Trouver le JSON dans la réponse
            start_idx = generated_text.find('{')
            end_idx = generated_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = generated_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                return {
                    'strengths': data.get('strengths', [])[:5],
                    'weaknesses': data.get('weaknesses', [])[:5],
                    'recommendations': data.get('recommendations', [])[:5],
                    'detailed_feedback': data.get('feedback', '')
                }
            else:
                raise ValueError("No JSON found in response")
        
        except Exception as e:
            print(f"Erreur parsing JSON IA: {e}")
            # Extraire manuellement si le JSON est mal formé
            return self._extract_manual_analysis(generated_text)
    
    def _extract_manual_analysis(self, text: str) -> Dict:
        """
        Extraction manuelle si le JSON n'est pas valide
        """
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Chercher des patterns dans le texte
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'strength' in line.lower() or 'point fort' in line.lower():
                current_section = 'strengths'
            elif 'weakness' in line.lower() or 'point faible' in line.lower() or 'lacune' in line.lower():
                current_section = 'weaknesses'
            elif 'recommendation' in line.lower() or 'conseil' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                item = line.lstrip('-•* ').strip()
                if item and current_section:
                    if current_section == 'strengths' and len(strengths) < 5:
                        strengths.append(item)
                    elif current_section == 'weaknesses' and len(weaknesses) < 5:
                        weaknesses.append(item)
                    elif current_section == 'recommendations' and len(recommendations) < 5:
                        recommendations.append(item)
        
        return {
            'strengths': strengths or ["Analyse des points forts en cours..."],
            'weaknesses': weaknesses or ["Analyse des points faibles en cours..."],
            'recommendations': recommendations or ["Continuez à pratiquer régulièrement"],
            'detailed_feedback': text[:500]  # Premiers 500 caractères
        }
    
    def _generate_basic_analysis(self, questions_data: List[Dict], score: float, subject: str) -> Dict:
        """
        Génère une analyse basique si l'IA n'est pas disponible
        TOUJOURS génère des points forts et lacunes spécifiques
        """
        from collections import Counter
        
        correct_concepts = []
        incorrect_concepts = []
        all_concepts = []
        
        for q in questions_data:
            concept = q.get('concept', 'Général')
            all_concepts.append(concept)
            if q.get('is_correct'):
                correct_concepts.append(concept)
            else:
                incorrect_concepts.append(concept)
        
        correct_counts = Counter(correct_concepts)
        incorrect_counts = Counter(incorrect_concepts)
        all_concepts_counts = Counter(all_concepts)
        
        # Points forts - TOUJOURS générer
        strengths = []
        
        # Si l'étudiant a des réponses correctes, lister les concepts maîtrisés
        if correct_counts:
            for concept, count in correct_counts.most_common(5):
                total_concept = all_concepts_counts.get(concept, count)
                percentage = (count / total_concept * 100) if total_concept > 0 else 0
                strengths.append(f"Bonne maîtrise de {concept} ({count}/{total_concept} correctes - {percentage:.0f}%)")
        
        # Si pas assez de points forts, analyser les concepts proches de la réussite
        if len(strengths) < 3:
            # Chercher des concepts avec au moins 1 bonne réponse
            for concept in set(all_concepts):
                if concept not in [s.split('Bonne maîtrise de ')[1].split(' (')[0] for s in strengths if 'Bonne maîtrise de' in s]:
                    correct = correct_counts.get(concept, 0)
                    total = all_concepts_counts.get(concept, 0)
                    if correct > 0 and len(strengths) < 5:
                        strengths.append(f"Compréhension partielle de {concept} ({correct}/{total} correctes)")
        
        # Si toujours pas assez, ajouter des points forts basés sur l'effort
        if len(strengths) < 3:
            if score > 0:
                strengths.append(f"Engagement démontré avec un score de {score:.1f}%")
                strengths.append(f"Participation active au test sur {subject}")
                strengths.append(f"Capacité à compléter l'ensemble du test")
        
        # Minimum 3 points forts
        while len(strengths) < 3:
            strengths.append(f"Effort fourni sur les questions de {subject}")
        
        # Points faibles - TOUJOURS générer des lacunes spécifiques
        weaknesses = []
        
        # Si l'étudiant a des erreurs, lister les concepts à améliorer
        if incorrect_counts:
            for concept, count in incorrect_counts.most_common(5):
                total_concept = all_concepts_counts.get(concept, count)
                percentage = (count / total_concept * 100) if total_concept > 0 else 0
                weaknesses.append(f"À renforcer : {concept} ({count}/{total_concept} incorrectes - {percentage:.0f}%)")
        
        # Si pas d'erreurs (score parfait), identifier des axes d'amélioration potentiels
        if len(weaknesses) == 0:
            # Analyser les concepts pour suggérer des améliorations
            if all_concepts_counts:
                for concept in list(all_concepts_counts.keys())[:3]:
                    weaknesses.append(f"Approfondir davantage {concept} pour maîtrise experte")
            
            # Ajouter des suggestions d'amélioration générale
            if len(weaknesses) < 3:
                weaknesses.append(f"Chercher des exercices plus avancés en {subject}")
                weaknesses.append(f"Travailler la rapidité d'exécution")
                weaknesses.append(f"Explorer des concepts connexes à {subject}")
        
        # Minimum 3 points faibles
        while len(weaknesses) < 3:
            weaknesses.append(f"Pratiquer régulièrement pour maintenir le niveau en {subject}")
        
        # Recommandations - TOUJOURS spécifiques
        recommendations = []
        
        # Recommandations basées sur les erreurs
        for concept, count in incorrect_counts.most_common(3):
            recommendations.append(f"Réviser et pratiquer davantage {concept}")
        
        # Recommandations basées sur les réussites
        for concept, count in correct_counts.most_common(2):
            if len(recommendations) < 5:
                recommendations.append(f"Approfondir {concept} avec des exercices avancés")
        
        # Recommandations générales si besoin
        if len(recommendations) < 3:
            if score >= 80:
                recommendations.append(f"Explorer des sujets avancés en {subject}")
                recommendations.append("Aider d'autres étudiants pour renforcer vos connaissances")
                recommendations.append("Participer à des projets pratiques")
            elif score >= 60:
                recommendations.append(f"Revoir les bases de {subject}")
                recommendations.append("Pratiquer régulièrement avec des exercices variés")
                recommendations.append("Demander de l'aide sur les concepts difficiles")
            else:
                recommendations.append(f"Revoir en profondeur les fondamentaux de {subject}")
                recommendations.append("Pratiquer quotidiennement avec des exercices simples")
                recommendations.append("Consulter un tuteur ou former un groupe d'étude")
        
        # Minimum 3 recommandations
        while len(recommendations) < 3:
            recommendations.append(f"Continuer à pratiquer régulièrement {subject}")
        
        # Feedback détaillé
        if score >= 90:
            feedback = f"Excellente performance en {subject} avec {score:.1f}% ! Vous maîtrisez très bien les concepts clés. Continuez ainsi et explorez des sujets plus avancés."
        elif score >= 75:
            feedback = f"Très bonne performance en {subject} avec {score:.1f}%. Vous avez une bonne compréhension globale avec quelques points à perfectionner."
        elif score >= 60:
            feedback = f"Performance satisfaisante en {subject} avec {score:.1f}%. Vous avez acquis les bases, mais des efforts supplémentaires permettront d'atteindre l'excellence."
        elif score >= 40:
            feedback = f"Performance de {score:.1f}% en {subject}. Des lacunes importantes sont identifiées. Concentrez-vous sur les concepts fondamentaux."
        else:
            feedback = f"Performance de {score:.1f}% en {subject}. Une révision approfondie est nécessaire. N'hésitez pas à demander de l'aide."
        
        return {
            'strengths': strengths[:5],  # Maximum 5 points forts
            'weaknesses': weaknesses[:5],  # Maximum 5 points faibles
            'recommendations': recommendations[:5],  # Maximum 5 recommandations
            'detailed_feedback': feedback
        }
    
    def batch_analyze_tests(self, tests_data: List[Dict]) -> Dict[str, Dict]:
        """
        Analyse plusieurs tests en batch
        
        Args:
            tests_data: Liste de tests à analyser
                Format: [{'test_id': str, 'test_name': str, 'subject': str, 'questions': List[Dict], 'score': float}]
        
        Returns:
            Dict avec analyses par test_id
        """
        analyses = {}
        
        for test in tests_data:
            test_id = test.get('test_id')
            analysis = self.analyze_test_performance(
                test_name=test.get('test_name'),
                subject=test.get('subject'),
                questions_data=test.get('questions', []),
                score=test.get('score', 0)
            )
            analyses[test_id] = analysis
        
        return analyses

    def _validate_and_clean_analysis(self, analysis: Dict, questions_data: List[Dict], subject: str) -> Dict:
        """
        Valide et nettoie l'analyse pour éviter les messages génériques
        Force la génération de concepts spécifiques
        """
        from collections import Counter
        
        # Extraire tous les concepts
        all_concepts = [q.get('concept', subject) for q in questions_data]
        concepts_counter = Counter(all_concepts)
        
        # Messages génériques à éviter absolument
        GENERIC_MESSAGES = [
            "Pas encore de concepts maîtrisés",
            "Continuez vos efforts",
            "Aucune faiblesse majeure détectée",
            "Aucune lacune",
        ]
        
        # Nettoyer les points forts
        cleaned_strengths = []
        for strength in analysis.get('strengths', []):
            # Vérifier si c'est un message générique
            is_generic = any(gen_msg.lower() in strength.lower() for gen_msg in GENERIC_MESSAGES)
            if not is_generic:
                cleaned_strengths.append(strength)
        
        # Si pas assez de points forts spécifiques, en générer
        if len(cleaned_strengths) < 3:
            # Générer des points forts basés sur les concepts réels
            for concept in list(concepts_counter.keys())[:3]:
                if len(cleaned_strengths) < 3:
                    cleaned_strengths.append(f"Travail effectué sur {concept}")
        
        # Nettoyer les points faibles
        cleaned_weaknesses = []
        for weakness in analysis.get('weaknesses', []):
            # Vérifier si c'est un message générique
            is_generic = any(gen_msg.lower() in weakness.lower() for gen_msg in GENERIC_MESSAGES)
            if not is_generic:
                cleaned_weaknesses.append(weakness)
        
        # Si pas assez de points faibles spécifiques, en générer
        if len(cleaned_weaknesses) < 3:
            # Générer des suggestions d'amélioration basées sur les concepts
            for concept in list(concepts_counter.keys())[:3]:
                if len(cleaned_weaknesses) < 3:
                    cleaned_weaknesses.append(f"Approfondir les connaissances en {concept}")
        
        return {
            'strengths': cleaned_strengths[:5],
            'weaknesses': cleaned_weaknesses[:5],
            'recommendations': analysis.get('recommendations', [])[:5],
            'detailed_feedback': analysis.get('detailed_feedback', '')
        }
