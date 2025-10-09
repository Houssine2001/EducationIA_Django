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
        AMÉLIORATION: Validation stricte des concepts et questions
        """
        exercises = []
        
        # Utilisation des définitions pour créer des QCM
        definitions = analysis.get('definitions', [])
        concepts = analysis.get('key_concepts', [])
        important_sentences = analysis.get('important_sentences', [])
        
        # QCM basés sur les définitions
        for definition in definitions[:count * 2]:  # Plus pour filtrage
            term = definition['term']
            correct_def = definition['definition']
            
            # VALIDATION: Vérifier que le terme est complet et valide
            if not self._is_valid_concept(term):
                continue
            
            # VALIDATION: Limiter la longueur de la définition
            # Maximum 20 mots ou 150 caractères pour une réponse
            if len(correct_def.split()) > 20 or len(correct_def) > 150:
                # Tronquer à la première phrase complète
                correct_def = self._truncate_to_sentence(correct_def, max_words=20)
            
            # VALIDATION: Vérifier que la définition est complète mais pas trop longue
            if len(correct_def.split()) < 5 or len(correct_def) < 20:
                continue
            if len(correct_def.split()) > 25 or len(correct_def) > 180:
                continue
            
            # VALIDATION: La définition ne doit pas être une question
            if correct_def.strip().endswith('?'):
                continue
            
            # Génération de distracteurs (mauvaises réponses)
            distractors = self._generate_distractors(correct_def, analysis, num=3)
            
            # VALIDATION: Vérifier la qualité des distracteurs
            if len(distractors) < 3:
                continue
            
            # Construction de la question avec validation
            question_text = self._build_valid_question(term)
            
            # VALIDATION: Vérifier que la question est bien formée
            if not question_text or len(question_text) < 10:
                continue
            
            # VALIDATION: La question doit rester courte (max 15 mots)
            if len(question_text.split()) > 15:
                continue
            
            # Options (mélangées)
            options = [correct_def] + distractors
            
            # VALIDATION: S'assurer qu'il n'y a pas d'options identiques ou très similaires
            unique_options = []
            for opt in options:
                is_duplicate = False
                for existing_opt in unique_options:
                    similarity = self._calculate_text_similarity(opt, existing_opt)
                    if similarity > 0.90:  # 90% de similarité = doublon
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_options.append(opt)
            
            # Si moins de 4 options uniques, passer à la question suivante
            if len(unique_options) < 4:
                continue
            
            options = unique_options[:4]  # Garder seulement 4 options
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
        used_sentences = set()  # Pour éviter les doublons
        
        if len(exercises) < count:
            for concept in concepts:
                # VALIDATION: Vérifier que le concept est valide
                if not self._is_valid_concept(concept):
                    continue
                
                # Recherche de phrases liées au concept
                related_sentences = [
                    s for s in important_sentences 
                    if concept in s['sentence'].lower() and s['sentence'] not in used_sentences
                ]
                
                if related_sentences:
                    sentence = related_sentences[0]['sentence']
                    
                    # VALIDATION: Vérifier que la phrase est complète et de qualité
                    if len(sentence.split()) < 8 or len(sentence) < 30:
                        continue
                    
                    # VALIDATION: Limiter la longueur de la phrase (max 25 mots ou 180 caractères)
                    if len(sentence.split()) > 25 or len(sentence) > 180:
                        sentence = self._truncate_to_sentence(sentence, max_words=20)
                        # Vérifier après troncature
                        if len(sentence.split()) < 8:
                            continue
                    
                    # VALIDATION: Éviter les phrases qui ressemblent à des titres
                    if sentence.endswith(':') or sentence.isupper():
                        continue
                    
                    question_text = f"Concernant '{concept.title()}', quelle affirmation est correcte ?"
                    correct_answer = sentence
                    distractors = self._generate_distractors(sentence, analysis, num=3)
                    
                    # VALIDATION: Vérifier qu'on a assez de distracteurs
                    if len(distractors) < 3:
                        continue
                    
                    options = [correct_answer] + distractors
                    
                    # VALIDATION: S'assurer qu'il n'y a pas d'options identiques
                    unique_options = []
                    for opt in options:
                        is_duplicate = False
                        for existing_opt in unique_options:
                            similarity = self._calculate_text_similarity(opt, existing_opt)
                            if similarity > 0.90:
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            unique_options.append(opt)
                    
                    if len(unique_options) < 4:
                        continue
                    
                    options = unique_options[:4]
                    random.shuffle(options)
                    correct_index = options.index(correct_answer)
                    correct_option = chr(65 + correct_index)
                    
                    difficulty = self._calculate_difficulty(concept, correct_answer, distractors)
                    quality_score = self._calculate_quality_mcq(question_text, correct_answer, distractors)
                    
                    # VALIDATION: Vérifier le score de qualité minimum
                    if quality_score < 0.5:
                        continue
                    
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
                    used_sentences.add(sentence)  # Marquer comme utilisée
                    
                    if len(exercises) >= count:
                        break
        
        # Éliminer les doublons finaux basés sur la similarité des questions
        unique_exercises = self._remove_duplicate_exercises(exercises)
        
        # Vérifier qu'il n'y a pas de réponses identiques entre différentes questions
        unique_exercises = self._remove_duplicate_answers(unique_exercises)
        
        return unique_exercises
    
    def _generate_true_false(self, analysis: Dict, count: int, config: Dict) -> List[Dict]:
        """
        Génère des questions Vrai/Faux
        AMÉLIORATION V3: Évite les doublons et limite la longueur des affirmations
        """
        exercises = []
        used_sentences = set()  # Pour éviter de réutiliser la même phrase
        
        important_sentences = analysis.get('important_sentences', [])
        concepts = analysis.get('key_concepts', [])
        
        for sent_data in important_sentences[:count * 3]:  # Plus de phrases pour avoir le choix
            sentence = sent_data['sentence']
            
            # VALIDATION: Éviter les phrases déjà utilisées
            if sentence in used_sentences:
                continue
            
            # VALIDATION: Limiter la longueur (max 25 mots)
            if len(sentence.split()) > 25:
                sentence = self._truncate_to_sentence(sentence, max_words=20)
            
            # VALIDATION: Vérifier la longueur après troncature
            if len(sentence.split()) < 8 or len(sentence.split()) > 25:
                continue
            
            # Génération d'une affirmation vraie (1 sur 2 seulement)
            if len([e for e in exercises if e['correct_answer'] is True]) < count * 0.5:
                true_exercise = self._create_true_false_exercise(
                    sentence,
                    is_true=True,
                    concept=self._extract_main_concept(sentence, concepts),
                    source=sentence,
                    analysis=analysis
                )
                exercises.append(true_exercise)
                used_sentences.add(sentence)
            
            # Génération d'une affirmation fausse
            false_statement = self._create_false_statement(sentence, analysis)
            if false_statement and false_statement not in used_sentences:
                # VALIDATION: Vérifier que l'affirmation fausse n'est pas identique à la vraie
                if false_statement.lower().strip() != sentence.lower().strip():
                    false_exercise = self._create_true_false_exercise(
                        false_statement,
                        is_true=False,
                        concept=self._extract_main_concept(sentence, concepts),
                        source=sentence,
                        analysis=analysis
                    )
                    exercises.append(false_exercise)
                    used_sentences.add(false_statement)
            
            if len(exercises) >= count:
                break
        
        # Supprimer les doublons finaux
        return self._remove_duplicate_exercises(exercises)[:count]
    
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
        AMÉLIORATION: Limite la longueur des distracteurs pour éviter les paragraphes
        """
        distractors = []
        correct_words = len(correct_answer.split())
        
        # Stratégie 1 : Utiliser d'autres phrases du document
        important_sentences = analysis.get('important_sentences', [])
        for sent_data in important_sentences:
            sentence = sent_data['sentence']
            
            # Filtrer les phrases selon la longueur
            # Les distracteurs doivent avoir une longueur similaire à la réponse correcte
            sentence_words = len(sentence.split())
            
            # VALIDATION: Longueur entre 5 et 25 mots maximum
            if sentence_words < 5 or sentence_words > 25:
                continue
            
            # VALIDATION: Pas trop différent de la réponse correcte (±50%)
            if sentence_words < correct_words * 0.5 or sentence_words > correct_words * 1.5:
                continue
            
            if sentence != correct_answer and len(sentence) > 20:
                # Tronquer si trop long
                if len(sentence.split()) > 20:
                    sentence = self._truncate_to_sentence(sentence, max_words=18)
                
                # Modification légère pour rendre plus plausible
                modified = self._modify_sentence(sentence)
                
                # VALIDATION: Vérifier que le distracteur n'est pas identique à la réponse
                if modified not in distractors and modified != correct_answer:
                    # VALIDATION: Éviter les distracteurs trop similaires
                    similarity = self._calculate_text_similarity(modified, correct_answer)
                    if similarity < 0.8:  # Moins de 80% de similarité
                        distractors.append(modified)
                        if len(distractors) >= num:
                            return distractors
        
        # Stratégie 2 : Création de distracteurs génériques (seulement si pas assez)
        generic_distractors = [
            "Cette définition n'est pas mentionnée dans le cours.",
            "Cette explication est incomplète ou incorrecte.",
            "Cette réponse ne correspond pas au contenu du document.",
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
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes (coefficient de Jaccard)
        NOUVEAU: Évite les distracteurs trop similaires à la réponse correcte
        """
        # Normaliser les textes
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        # Intersection et union
        intersection = words1 & words2
        union = words1 | words2
        
        # Coefficient de Jaccard
        similarity = len(intersection) / len(union) if len(union) > 0 else 0.0
        
        return similarity
    
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
    
    def _is_valid_concept(self, concept: str) -> bool:
        """
        Vérifie si un concept est valide et complet
        V4 FINAL: Validation linguistique stricte
        """
        if not concept or len(concept.strip()) < 3:
            return False
        
        concept = concept.strip()
        
        # Nettoyer les espaces multiples et caractères bizarres
        concept = re.sub(r'\s+', ' ', concept)
        concept = re.sub(r'[^\w\sàâäéèêëïîôùûüÿæœç\'-]', '', concept)
        
        # Limite de longueur stricte (max 35 caractères)
        if len(concept) > 35:
            return False
        
        # Pas de guillemets ou apostrophes multiples
        if concept.count("'") > 1 or '"' in concept or '«' in concept or '»' in concept:
            return False
        
        # Pas de ponctuation forte
        if any(p in concept for p in ['.', ',', ';', ':', '!', '?', '(', ')']):
            return False
        
        # NOUVEAU: Détecter les mots collés (ex: "En2009Chaque")
        if re.search(r'\d+[A-Z]', concept) or re.search(r'[a-z][A-Z][a-z]', concept):
            return False
        
        # NOUVEAU: Pas de répétition de mots (ex: "Les Les")
        words = concept.lower().split()
        if len(words) != len(set(words)):
            return False
        
        # Patterns invalides étendus
        invalid_patterns = [
            r'^[A-Z]{1,2}$',  # 1-2 lettres majuscules seules
            r'.*\s[A-Z]$',  # Se termine par une lettre majuscule seule
            r'^[A-Z]\s.*',  # Commence par une lettre majuscule seule
            r'.*\d+$',  # Se termine par un chiffre
            r'^\d+.*',  # Commence par un chiffre
            r'.*\s-\s*$',  # Se termine par un tiret
            r'^\s*-\s.*',  # Commence par un tiret
            r'.*\?.*',  # Contient un point d'interrogation
            r'.*qui\s*$',  # Se termine par "qui" (ex: "Chose Qui")
            r'.*que\s*$',  # Se termine par "que"
            r'.*dont\s*$',  # Se termine par "dont"
            r'.*où\s*$',  # Se termine par "où"
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, concept, re.IGNORECASE):
                return False
        
        # Vérifier qu'il n'y a pas de mots trop courts (< 2 lettres) sauf articles
        words = concept.split()
        allowed_short = {'le', 'la', 'un', 'de', 'du', 'à', 'au', 'en', 'et', 'ou'}
        
        # Maximum 4 mots pour un concept
        if len(words) > 4:
            return False
        
        for word in words:
            if len(word) < 2:
                return False
            if len(word) == 2 and word.lower() not in allowed_short:
                return False
        
        # Vérifier qu'il y a au moins un mot substantiel (5+ lettres)
        has_substantial = any(len(w) >= 5 for w in words)
        if not has_substantial:
            return False
        
        # Éviter les titres de sections génériques et mots interrogatifs
        generic_titles = [
            'résultats', 'introduction', 'conclusion', 'exemple', 'cas', 
            'partie', 'section', 'chapitre', 'titre', 'pourquoi', 'comment',
            'chose', 'choses', 'quelque', 'quelques', 'autre', 'autres',
            'même', 'mêmes', 'préexistante', 'préexistant', 'préexistantes',
            'composée', 'composé', 'composés', 'virtuelle', 'virtuel', 'virtuels',
            'document', 'documents', 'fichier', 'fichiers', 'chaque', 'création',
            'organisme', 'compétent'
        ]
        
        # Vérifier les mots complets uniquement
        concept_words_lower = [w.lower() for w in words]
        if any(title in concept_words_lower for title in generic_titles):
            return False
        
        # NOUVEAU: Rejeter si commence par article + année (ex: "En 2009")
        if len(words) >= 2:
            if words[0].lower() in ['en', 'le', 'la', 'les', 'un', 'une', 'des'] and words[1].isdigit():
                return False
        
        # NOUVEAU: Rejeter si contient tiret collé (ex: "a-la")
        if '-' in concept and not re.match(r'^[\w]+-[\w]+$', concept):
            return False
        
        # Maximum 1 adjectif
        adjectives = ['virtuelle', 'composée', 'nouveau', 'nouvelle', 'ancien', 'ancienne', 
                     'grand', 'grande', 'petit', 'petite', 'bon', 'bonne', 'mauvais', 'mauvaise',
                     'chaque', 'tout', 'toute', 'tous', 'toutes']
        adj_count = sum(1 for word in words if word.lower() in adjectives)
        if adj_count > 0:  # Aucun adjectif accepté
            return False
        
        # NOUVEAU: Rejeter si commence/termine par article (ex: "Les brevets")
        if words[0].lower() in ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de']:
            return False
        if words[-1].lower() in ['le', 'la', 'les', 'un', 'une', 'des']:
            return False
        
        # Rejeter si trop de majuscules (titre)
        uppercase_words = sum(1 for w in words if len(w) > 1 and w[0].isupper())
        if uppercase_words > len(words) * 0.6 and len(words) > 2:
            return False
        
        return True
    
    def _build_valid_question(self, concept: str) -> str:
        """
        Construit une question valide à partir d'un concept
        AMÉLIORATION V3: Questions ultra-courtes (1 phrase max, 10 mots max)
        """
        # Nettoyer le concept
        concept = concept.strip()
        
        # Vérifier si le concept est valide
        if not self._is_valid_concept(concept):
            return None
        
        # Capitaliser correctement
        concept_display = concept.title()
        
        # Templates de questions ultra-courts (max 10 mots)
        templates = [
            f"Que signifie {concept_display} ?",  # 3-4 mots
            f"Définissez {concept_display}.",  # 2-3 mots
            f"Qu'est-ce que {concept_display} ?",  # 3-4 mots
        ]
        
        # Choisir un template aléatoire
        question = random.choice(templates)
        
        # VALIDATION FINALE: Vérifier que la question est vraiment courte
        if len(question.split()) > 10:
            # Si trop long, utiliser le template le plus court
            question = f"Définissez {concept_display}."
        
        return question
    
    def _truncate_to_sentence(self, text: str, max_words: int = 20) -> str:
        """
        Tronque un texte à la première phrase complète sans dépasser max_words
        NOUVEAU: Évite les réponses trop longues (paragraphes entiers)
        """
        # Nettoyer le texte
        text = text.strip()
        
        # Si déjà assez court, retourner tel quel
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Chercher la première phrase complète
        sentence_endings = ['.', '!', '?']
        
        for i, char in enumerate(text):
            if char in sentence_endings:
                # Vérifier que c'est bien une fin de phrase (pas une abréviation)
                if i + 1 < len(text) and (text[i + 1] == ' ' or i + 1 == len(text)):
                    first_sentence = text[:i + 1].strip()
                    # Vérifier que la phrase n'est pas trop longue
                    if len(first_sentence.split()) <= max_words:
                        return first_sentence
        
        # Si pas de phrase complète trouvée, tronquer aux max_words
        truncated = ' '.join(words[:max_words])
        
        # Ne pas ajouter de points de suspension si le texte se termine proprement
        # Vérifier si le dernier mot est complet
        if not truncated.endswith(('.', '!', '?', ',')):
            truncated += '.'
        
        return truncated
    
    def _remove_duplicate_exercises(self, exercises: List[Dict]) -> List[Dict]:
        """
        Supprime les exercices en doublon basés sur la similarité
        AMÉLIORATION V3: Détection plus stricte des doublons
        """
        unique = []
        seen_concepts = set()
        seen_questions_normalized = set()
        seen_statements = set()  # Pour Vrai/Faux
        
        for exercise in exercises:
            concept = exercise.get('concept', '').lower().strip()
            question = exercise.get('question', '').lower().strip()
            
            # Pour les Vrai/Faux, vérifier aussi l'affirmation (statement)
            if exercise.get('type') == 'true_false':
                # Extraire l'affirmation de la question
                statement = question
                for template_start in ['selon le cours', 'il est correct d\'affirmer que']:
                    if template_start in statement:
                        statement = statement.split(template_start, 1)[-1].strip()
                
                # Normaliser l'affirmation
                statement_normalized = re.sub(r'[^\w\s]', '', statement)
                statement_normalized = ' '.join(statement_normalized.split())
                
                # Vérifier si on a déjà vu cette affirmation
                if statement_normalized in seen_statements:
                    continue  # Doublon détecté
                seen_statements.add(statement_normalized)
            
            # Normaliser la question (retirer ponctuation, espaces multiples)
            question_normalized = re.sub(r'[^\w\s]', '', question)
            question_normalized = ' '.join(question_normalized.split())
            
            # Vérifier si on a déjà vu ce concept avec une question très similaire
            concept_question_key = f"{concept}_{question_normalized[:50]}"
            
            if concept_question_key in seen_questions_normalized:
                continue  # Doublon détecté
            
            # Vérifier la similarité avec les questions existantes
            is_duplicate = False
            for existing_q in seen_questions_normalized:
                # Calcul de similarité simple (Jaccard)
                words1 = set(question_normalized.split())
                words2 = set(existing_q.split('_', 1)[-1].split() if '_' in existing_q else existing_q.split())
                
                if len(words1) > 0 and len(words2) > 0:
                    intersection = len(words1 & words2)
                    union = len(words1 | words2)
                    similarity = intersection / union if union > 0 else 0
                    
                    # Si similarité > 65% (plus strict), c'est un doublon
                    if similarity > 0.65:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique.append(exercise)
                seen_concepts.add(concept)
                seen_questions_normalized.add(concept_question_key)
        
        return unique
    
    def _remove_duplicate_answers(self, exercises: List[Dict]) -> List[Dict]:
        """
        Supprime les exercices QCM qui ont des réponses identiques
        NOUVEAU V3: Évite qu'une même phrase soit réponse correcte dans plusieurs QCM
        """
        if not exercises:
            return exercises
        
        mcq_exercises = [e for e in exercises if e.get('type') == 'mcq']
        other_exercises = [e for e in exercises if e.get('type') != 'mcq']
        
        # Tracker les réponses déjà utilisées
        seen_answers = set()
        unique_mcq = []
        
        for exercise in mcq_exercises:
            # Récupérer la réponse correcte
            correct_option = exercise.get('correct_answer')
            options = exercise.get('options', {})
            correct_answer = options.get(correct_option, '')
            
            # Normaliser la réponse
            answer_normalized = re.sub(r'[^\w\s]', '', correct_answer.lower())
            answer_normalized = ' '.join(answer_normalized.split())
            
            # Vérifier si cette réponse a déjà été utilisée
            if answer_normalized and answer_normalized not in seen_answers:
                # Vérifier aussi la similarité avec les réponses existantes
                is_duplicate = False
                for seen_answer in seen_answers:
                    similarity = self._calculate_text_similarity(answer_normalized, seen_answer)
                    if similarity > 0.85:  # 85% de similarité = doublon
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_mcq.append(exercise)
                    seen_answers.add(answer_normalized)
        
        return unique_mcq + other_exercises
