"""
Générateur d'exercices IA - Création automatique de QCM, Vrai/Faux et Texte à trous
"""
import re
import random
from typing import List, Dict, Tuple
from .ai_document_analyzer import DocumentAnalyzer


class ExerciseGenerator:
    """
    Générateur d'exercices basé sur l'analyse IA de documents
    """
    
    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        
        # Templates pour les questions
        self.mcq_templates = [
            "Que signifie {concept} ?",
            "Quelle est la définition de {concept} ?",
            "Parmi les propositions suivantes, laquelle décrit {concept} ?",
            "Qu'est-ce que {concept} ?",
            "Comment peut-on définir {concept} ?",
        ]
        
        self.true_false_templates = [
            "{statement}",  # Direct
            "Selon le cours, {statement}",
            "Il est correct d'affirmer que {statement}",
        ]
    
    def generate_exercises_from_document(
        self, 
        document_text: str,
        config: Dict = None
    ) -> Dict:
        """
        Génère automatiquement des exercices à partir d'un document
        
        Args:
            document_text: Texte du document à analyser
            config: Configuration de génération (nombre, types, difficultés)
            
        Returns:
            Dict contenant les exercices générés et les méta-informations
        """
        # Configuration par défaut
        if config is None:
            config = {
                'total_exercises': 10,
                'mcq_percentage': 50,
                'true_false_percentage': 30,
                'fill_blank_percentage': 20,
                'easy_percentage': 30,
                'medium_percentage': 50,
                'hard_percentage': 20,
                'min_quality_score': 0.6
            }
        
        # Analyse du document
        analysis = self.analyzer.analyze_document(document_text)
        
        # Calcul du nombre d'exercices par type
        total = config['total_exercises']
        num_mcq = int(total * config['mcq_percentage'] / 100)
        num_tf = int(total * config['true_false_percentage'] / 100)
        num_fb = total - num_mcq - num_tf  # Le reste en texte à trous
        
        # Génération des exercices
        exercises = []
        
        # 1. Génération des QCM
        mcq_exercises = self._generate_mcq(
            analysis, 
            num_mcq,
            config
        )
        exercises.extend(mcq_exercises)
        
        # 2. Génération des Vrai/Faux
        tf_exercises = self._generate_true_false(
            analysis,
            num_tf,
            config
        )
        exercises.extend(tf_exercises)
        
        # 3. Génération des Textes à trous
        fb_exercises = self._generate_fill_blank(
            analysis,
            num_fb,
            config
        )
        exercises.extend(fb_exercises)
        
        # Filtrage par qualité
        min_quality = config['min_quality_score']
        filtered_exercises = [ex for ex in exercises if ex['quality_score'] >= min_quality]
        
        # Si pas assez d'exercices de qualité, on abaisse le seuil
        if len(filtered_exercises) < total * 0.5:
            filtered_exercises = [ex for ex in exercises if ex['quality_score'] >= min_quality * 0.8]
        
        return {
            'exercises': filtered_exercises,
            'analysis': analysis,
            'stats': {
                'total_generated': len(exercises),
                'total_quality': len(filtered_exercises),
                'mcq': len([e for e in filtered_exercises if e['type'] == 'mcq']),
                'true_false': len([e for e in filtered_exercises if e['type'] == 'true_false']),
                'fill_blank': len([e for e in filtered_exercises if e['type'] == 'fill_blank']),
            }
        }
    
    def _generate_mcq(self, analysis: Dict, count: int, config: Dict) -> List[Dict]:
        """
        Génère des questions à choix multiples
        """
        exercises = []
        
        # Utilisation des définitions pour créer des QCM
        definitions = analysis.get('definitions', [])
        concepts = analysis.get('key_concepts', [])
        important_sentences = analysis.get('important_sentences', [])
        
        # QCM basés sur les définitions
        for definition in definitions[:count]:
            term = definition['term']
            correct_def = definition['definition']
            
            # Génération de distracteurs (mauvaises réponses)
            distractors = self._generate_distractors(correct_def, analysis, num=3)
            
            # Construction de la question
            question_text = random.choice(self.mcq_templates).format(concept=term.title())
            
            # Options (mélangées)
            options = [correct_def] + distractors
            random.shuffle(options)
            correct_index = options.index(correct_def)
            correct_option = chr(65 + correct_index)  # A, B, C, D
            
            # Calcul de la difficulté
            difficulty = self._calculate_difficulty(term, correct_def, distractors)
            
            # Calcul du score de qualité
            quality_score = self._calculate_quality_mcq(
                question_text, 
                correct_def, 
                distractors
            )
            
            exercise = {
                'type': 'mcq',
                'question': question_text,
                'concept': term.title(),
                'options': {
                    'A': options[0],
                    'B': options[1],
                    'C': options[2],
                    'D': options[3]
                },
                'correct_answer': correct_option,
                'explanation': f"La bonne réponse est : {correct_def}",
                'source_sentence': definition['full_sentence'],
                'difficulty': difficulty,
                'quality_score': quality_score
            }
            
            exercises.append(exercise)
            
            if len(exercises) >= count:
                break
        
        # QCM basés sur les concepts (si pas assez de définitions)
        if len(exercises) < count:
            for concept in concepts:
                # Recherche de phrases liées au concept
                related_sentences = [
                    s for s in important_sentences 
                    if concept in s['sentence'].lower()
                ]
                
                if related_sentences:
                    sentence = related_sentences[0]['sentence']
                    
                    question_text = f"Concernant '{concept}', quelle affirmation est correcte ?"
                    correct_answer = sentence
                    distractors = self._generate_distractors(sentence, analysis, num=3)
                    
                    options = [correct_answer] + distractors
                    random.shuffle(options)
                    correct_index = options.index(correct_answer)
                    correct_option = chr(65 + correct_index)
                    
                    difficulty = self._calculate_difficulty(concept, correct_answer, distractors)
                    quality_score = self._calculate_quality_mcq(question_text, correct_answer, distractors)
                    
                    exercise = {
                        'type': 'mcq',
                        'question': question_text,
                        'concept': concept.title(),
                        'options': {
                            'A': options[0],
                            'B': options[1],
                            'C': options[2],
                            'D': options[3]
                        },
                        'correct_answer': correct_option,
                        'explanation': f"La bonne réponse est : {correct_answer}",
                        'source_sentence': sentence,
                        'difficulty': difficulty,
                        'quality_score': quality_score
                    }
                    
                    exercises.append(exercise)
                    
                    if len(exercises) >= count:
                        break
        
        return exercises
    
    def _generate_true_false(self, analysis: Dict, count: int, config: Dict) -> List[Dict]:
        """
        Génère des questions Vrai/Faux
        """
        exercises = []
        
        important_sentences = analysis.get('important_sentences', [])
        concepts = analysis.get('key_concepts', [])
        
        for sent_data in important_sentences[:count * 2]:  # Plus de phrases pour avoir le choix
            sentence = sent_data['sentence']
            
            # Génération d'une affirmation vraie
            true_statement = sentence
            true_exercise = self._create_true_false_exercise(
                true_statement,
                is_true=True,
                concept=self._extract_main_concept(sentence, concepts),
                source=sentence,
                analysis=analysis
            )
            exercises.append(true_exercise)
            
            # Génération d'une affirmation fausse (négation ou modification)
            false_statement = self._create_false_statement(sentence, analysis)
            if false_statement:
                false_exercise = self._create_true_false_exercise(
                    false_statement,
                    is_true=False,
                    concept=self._extract_main_concept(sentence, concepts),
                    source=sentence,
                    analysis=analysis
                )
                exercises.append(false_exercise)
            
            if len(exercises) >= count:
                break
        
        return exercises[:count]
    
    def _generate_fill_blank(self, analysis: Dict, count: int, config: Dict) -> List[Dict]:
        """
        Génère des exercices de texte à trous
        """
        exercises = []
        
        important_sentences = analysis.get('important_sentences', [])
        keywords = analysis.get('key_concepts', [])
        
        for sent_data in important_sentences[:count * 2]:
            sentence = sent_data['sentence']
            
            # Recherche de mots clés à masquer
            words_to_blank = []
            for keyword in keywords:
                if keyword in sentence.lower():
                    words_to_blank.append(keyword)
            
            if not words_to_blank:
                continue
            
            # Sélection d'un mot à masquer
            word_to_blank = random.choice(words_to_blank)
            
            # Création du texte à trous
            blank_text = self._create_blank_text(sentence, word_to_blank)
            
            if blank_text:
                concept = word_to_blank.title()
                difficulty = 'medium' if len(word_to_blank.split()) == 1 else 'hard'
                quality_score = 0.7 if len(word_to_blank.split()) <= 2 else 0.6
                
                exercise = {
                    'type': 'fill_blank',
                    'question': f"Complétez la phrase suivante :",
                    'text': blank_text,
                    'concept': concept,
                    'correct_answer': word_to_blank,
                    'explanation': f"Le mot manquant est : {word_to_blank}",
                    'source_sentence': sentence,
                    'difficulty': difficulty,
                    'quality_score': quality_score
                }
                
                exercises.append(exercise)
                
                if len(exercises) >= count:
                    break
        
        return exercises
    
    def _generate_distractors(self, correct_answer: str, analysis: Dict, num: int = 3) -> List[str]:
        """
        Génère des distracteurs plausibles pour un QCM
        """
        distractors = []
        
        # Stratégie 1 : Utiliser d'autres phrases du document
        important_sentences = analysis.get('important_sentences', [])
        for sent_data in important_sentences:
            sentence = sent_data['sentence']
            if sentence != correct_answer and len(sentence) > 20:
                # Modification légère pour rendre plus plausible
                modified = self._modify_sentence(sentence)
                if modified not in distractors and modified != correct_answer:
                    distractors.append(modified)
                    if len(distractors) >= num:
                        return distractors
        
        # Stratégie 2 : Création de distracteurs génériques
        generic_distractors = [
            "Cette définition n'est pas mentionnée dans le cours.",
            "Aucune des réponses proposées n'est correcte.",
            "Cette explication est incomplète ou incorrecte.",
        ]
        
        for dist in generic_distractors:
            if len(distractors) < num:
                distractors.append(dist)
        
        return distractors[:num]
    
    def _modify_sentence(self, sentence: str) -> str:
        """
        Modifie légèrement une phrase pour créer un distracteur
        """
        # Simplification : on retourne la phrase telle quelle
        # Dans une version plus avancée, on pourrait utiliser des synonymes
        return sentence
    
    def _create_false_statement(self, true_sentence: str, analysis: Dict) -> str:
        """
        Crée une affirmation fausse à partir d'une vraie
        """
        # Stratégie simple : négation ou remplacement
        keywords = analysis.get('key_concepts', [])
        
        # Recherche d'un mot clé à remplacer
        for keyword in keywords:
            if keyword in true_sentence.lower():
                # Remplacement par un autre concept
                other_keywords = [k for k in keywords if k != keyword]
                if other_keywords:
                    replacement = random.choice(other_keywords)
                    false_sentence = true_sentence.lower().replace(keyword, replacement, 1)
                    return false_sentence.capitalize()
        
        # Si pas de remplacement possible, ajout d'une négation
        if " est " in true_sentence.lower():
            false_sentence = true_sentence.lower().replace(" est ", " n'est pas ", 1)
            return false_sentence.capitalize()
        
        return None
    
    def _create_true_false_exercise(
        self,
        statement: str,
        is_true: bool,
        concept: str,
        source: str,
        analysis: Dict
    ) -> Dict:
        """
        Crée un exercice Vrai/Faux
        """
        question_text = random.choice(self.true_false_templates).format(statement=statement)
        
        difficulty = 'easy' if is_true else 'medium'
        quality_score = 0.7 if is_true else 0.6
        
        explanation = (
            f"Cette affirmation est {'vraie' if is_true else 'fausse'}. "
            f"{'Elle correspond directement au cours.' if is_true else 'Elle contient une erreur par rapport au cours.'}"
        )
        
        return {
            'type': 'true_false',
            'question': question_text,
            'concept': concept,
            'correct_answer': is_true,
            'explanation': explanation,
            'source_sentence': source,
            'difficulty': difficulty,
            'quality_score': quality_score
        }
    
    def _create_blank_text(self, sentence: str, word_to_blank: str) -> str:
        """
        Crée un texte à trous en remplaçant un mot par des underscores
        """
        # Remplacement case-insensitive
        pattern = re.compile(re.escape(word_to_blank), re.IGNORECASE)
        blank_text = pattern.sub('___', sentence, count=1)
        
        if '___' in blank_text:
            return blank_text
        return None
    
    def _extract_main_concept(self, sentence: str, concepts: List[str]) -> str:
        """
        Extrait le concept principal d'une phrase
        """
        for concept in concepts:
            if concept in sentence.lower():
                return concept.title()
        
        # Si aucun concept trouvé, extraction du premier nom significatif
        words = sentence.split()
        for word in words:
            if len(word) > 5 and word[0].isupper():
                return word
        
        return "Concept général"
    
    def _calculate_difficulty(self, term: str, correct: str, distractors: List[str]) -> str:
        """
        Calcule la difficulté d'une question
        """
        # Critères :
        # - Longueur du terme
        # - Complexité de la définition
        # - Similarité des distracteurs
        
        term_complexity = len(term.split())
        def_complexity = len(correct.split())
        
        total_complexity = term_complexity + (def_complexity / 10)
        
        if total_complexity < 2:
            return 'easy'
        elif total_complexity < 4:
            return 'medium'
        else:
            return 'hard'
    
    def _calculate_quality_mcq(
        self,
        question: str,
        correct: str,
        distractors: List[str]
    ) -> float:
        """
        Calcule un score de qualité pour un QCM (0-1)
        """
        score = 0.5  # Score de base
        
        # Bonus si la question est claire (pas trop longue)
        if len(question.split()) < 15:
            score += 0.1
        
        # Bonus si la réponse correcte est complète
        if len(correct.split()) >= 5:
            score += 0.1
        
        # Bonus si les distracteurs sont variés
        if len(set(distractors)) == len(distractors):
            score += 0.2
        
        # Pénalité si les distracteurs sont trop similaires
        if any(dist in correct for dist in distractors):
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)
