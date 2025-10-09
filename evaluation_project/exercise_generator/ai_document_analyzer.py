"""
Moteur IA pour l'analyse de documents et l'extraction de concepts
Utilise des techniques NLP locales sans API externe
"""
import re
import string
from collections import Counter
from typing import List, Dict, Tuple
import json


class DocumentAnalyzer:
    """
    Analyseur de documents pour extraire les concepts clés et informations importantes
    Utilise des techniques NLP basiques mais efficaces
    """
    
    def __init__(self):
        # Mots vides français (stop words)
        self.french_stopwords = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'est', 'à', 'au',
            'en', 'pour', 'dans', 'sur', 'par', 'avec', 'ce', 'qui', 'que', 'quoi',
            'dont', 'où', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'je',
            'tu', 'son', 'sa', 'ses', 'leur', 'leurs', 'mon', 'ma', 'mes', 'ton',
            'ta', 'tes', 'notre', 'votre', 'comme', 'plus', 'mais', 'ou', 'donc',
            'or', 'ni', 'car', 'si', 'aussi', 'très', 'tout', 'toute', 'tous',
            'toutes', 'se', 'ne', 'pas', 'être', 'avoir', 'faire', 'dire', 'cette',
            'cet', 'ces', 'y', 'a', 'aux', 'sans', 'sous', 'vers', 'entre', 'ainsi',
            'après', 'avant', 'depuis', 'pendant', 'peut', 'peuvent', 'doit', 'doivent'
        }
        
        # Marqueurs de définition (pour identifier les concepts importants)
        self.definition_markers = [
            'est défini comme', 'est', 'désigne', 'représente', 'signifie',
            'correspond à', 'se définit comme', 'appelé', 'nommé', 'est un',
            'est une', 'sont des', 'c\'est', 'ce sont'
        ]
        
        # Marqueurs de relations causales
        self.causal_markers = [
            'car', 'parce que', 'puisque', 'donc', 'ainsi', 'par conséquent',
            'en conséquence', 'c\'est pourquoi', 'grâce à', 'à cause de',
            'provoque', 'entraîne', 'cause', 'permet'
        ]
    
    def analyze_document(self, text: str) -> Dict:
        """
        Analyse complète d'un document de cours
        
        Args:
            text: Texte du document à analyser
            
        Returns:
            Dict contenant toutes les informations extraites
        """
        if not text or len(text.strip()) == 0:
            return {
                'key_concepts': [],
                'main_topics': [],
                'important_sentences': [],
                'definitions': [],
                'causal_relations': [],
                'summary': '',
                'word_count': 0,
                'sentence_count': 0
            }
        
        # Nettoyage du texte
        clean_text = self._clean_text(text)
        
        # Extraction des phrases
        sentences = self._extract_sentences(clean_text)
        
        # Extraction des mots clés
        keywords = self._extract_keywords(clean_text, top_n=20)
        
        # Extraction des concepts (bigrammes et trigrammes importants)
        concepts = self._extract_concepts(clean_text, top_n=15)
        
        # Identification des phrases importantes
        important_sentences = self._identify_important_sentences(sentences, keywords, concepts)
        
        # Extraction des définitions
        definitions = self._extract_definitions(sentences)
        
        # Extraction des relations causales
        causal_relations = self._extract_causal_relations(sentences)
        
        # Génération d'un résumé
        summary = self._generate_summary(important_sentences[:5])
        
        # Identification des thèmes principaux
        main_topics = self._identify_main_topics(concepts, keywords)
        
        return {
            'key_concepts': concepts,
            'main_topics': main_topics,
            'important_sentences': important_sentences,
            'definitions': definitions,
            'causal_relations': causal_relations,
            'summary': summary,
            'word_count': len(clean_text.split()),
            'sentence_count': len(sentences)
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte en supprimant les caractères spéciaux
        NOUVEAU: Normalisation avancée pour éviter les fragments collés
        """
        # Normaliser les espaces autour de la ponctuation
        text = re.sub(r'([.,;!?:])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])([.,;!?:])', r'\1 \2', text)
        
        # Normaliser les espaces autour des chiffres
        text = re.sub(r'(\d{4})([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])(\d{4})', r'\1 \2', text)
        
        # Supprimer les retours à la ligne multiples
        text = re.sub(r'\n+', '\n', text)
        
        # Remplacer les tabulations par des espaces
        text = text.replace('\t', ' ')
        
        # Normaliser les espaces multiples
        text = re.sub(r' +', ' ', text)
        
        # Supprimer les fragments orphelins (mots < 2 chars seuls sur une ligne)
        lines = []
        for line in text.split('\n'):
            words = line.strip().split()
            # Garder la ligne si elle contient au moins un mot >= 3 caractères
            if any(len(w.strip(string.punctuation)) >= 3 for w in words):
                lines.append(line.strip())
        
        return ' '.join(lines)
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extrait les phrases d'un texte de manière plus intelligente"""
        # Découpage par ponctuation forte tout en préservant les acronymes
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Nettoyage et filtrage avancé
        cleaned_sentences = []
        for s in sentences:
            s = s.strip()
            
            # Filtres de qualité
            if len(s) < 15:  # Trop courte
                continue
            if len(s.split()) < 4:  # Moins de 4 mots
                continue
            if not any(c.isalpha() for c in s):  # Pas de lettres
                continue
            if s.isupper() and len(s) < 50:  # Titres en majuscules (sauf longs)
                continue
            if s.endswith(':'):  # Titres de sections
                continue
            if re.match(r'^[IVX]+\.?\s*$', s):  # Numérotation romaine seule
                continue
            if re.match(r'^\d+\.?\s*$', s):  # Numérotation seule
                continue
            
            # Vérifier que la phrase n'est pas tronquée
            # Une phrase tronquée commence ou se termine souvent par des mots incomplets
            words = s.split()
            if len(words) > 0:
                first_word = words[0]
                last_word = words[-1]
                
                # Éviter les phrases qui commencent par un mot tronqué (moins de 3 caractères et pas d'article)
                if len(first_word) < 3 and first_word.lower() not in ['le', 'la', 'un', 'de', 'à', 'en', 'il', 'on']:
                    continue
                
                # Éviter les phrases qui se terminent par un mot incomplet (contient un tiret ou moins de 3 caractères)
                if '-' in last_word or (len(last_word) < 3 and not last_word.isdigit()):
                    continue
            
            cleaned_sentences.append(s)
        
        return cleaned_sentences
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extrait les mots clés les plus importants (TF-IDF simplifié)
        Filtre les pronoms, conjonctions et mots non significatifs
        """
        # Mots à éviter absolument
        invalid_words = {
            'elle', 'il', 'ils', 'elles', 'lui', 'leur', 'leurs', 'celui', 'celle', 'ceux', 'celles',
            'qui', 'que', 'quoi', 'dont', 'où', 'lequel', 'laquelle', 'lesquels', 'lesquelles',
            'lorsque', "lorsqu", 'quand', 'comme', 'si', 'mais', 'ou', 'et', 'donc', 'or', 'ni', 'car',
            'ce', 'cet', 'cette', 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'notre', 'votre', 'nos', 'vos', 'quel', 'quelle', 'quels', 'quelles', 'tout', 'tous',
            'toute', 'toutes', 'autre', 'autres', 'même', 'mêmes', 'tel', 'telle', 'tels', 'telles'
        }
        
        # Tokenisation
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]+\b', text.lower())
        
        # Filtrage des stop words, mots courts et mots invalides
        filtered_words = [
            w for w in words 
            if w not in self.french_stopwords and w not in invalid_words and len(w) > 3
        ]
        
        # Calcul de la fréquence
        word_freq = Counter(filtered_words)
        
        # Retour des N mots les plus fréquents
        return [word for word, freq in word_freq.most_common(top_n)]
    
    def _extract_concepts(self, text: str, top_n: int = 15) -> List[str]:
        """
        Extrait les concepts (n-grammes) les plus importants
        Filtre les pronoms, conjonctions et mots non significatifs
        AMÉLIORATION: Validation stricte pour éviter les concepts tronqués ou invalides
        """
        # Mots à éviter absolument (pronoms, conjonctions, articles, etc.)
        invalid_words = {
            'elle', 'il', 'ils', 'elles', 'lui', 'leur', 'leurs', 'celui', 'celle', 'ceux', 'celles',
            'qui', 'que', 'quoi', 'dont', 'où', 'lequel', 'laquelle', 'lesquels', 'lesquelles',
            'lorsque', "lorsqu", 'quand', 'comme', 'si', 'mais', 'ou', 'et', 'donc', 'or', 'ni', 'car',
            'ce', 'cet', 'cette', 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'notre', 'votre', 'nos', 'vos', 'leur', 'leurs', 'quel', 'quelle', 'quels', 'quelles',
            'pourquoi', 'parmi', 'selon', 'vers', 'chez', 'sans', 'sous', 'dans', 'avec', 'pour',
            'résultats', 'cas', 'exemple', 'titre'  # Mots génériques souvent issus de titres
        }
        
        # Patterns de mots invalides (tronqués, mal formés)
        invalid_patterns = [
            r'^[a-z]{1,2}$',  # Mots trop courts (1-2 lettres)
            r'.*\d+.*',  # Contient des chiffres
            r'^[A-Z]+$',  # Tout en majuscules (acronymes seuls)
            r'.*-$',  # Se termine par un tiret
            r'^-.*',  # Commence par un tiret
        ]
        
        def is_valid_word(word: str) -> bool:
            """Vérifie si un mot est valide pour faire partie d'un concept"""
            if len(word) < 3:
                return False
            if word in self.french_stopwords or word in invalid_words:
                return False
            for pattern in invalid_patterns:
                if re.match(pattern, word):
                    return False
            return True
        
        # Tokenisation plus stricte
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{3,}\b', text.lower())
        
        # Filtrage préalable des mots
        valid_words = [w for w in words if is_valid_word(w)]
        
        # Extraction de bigrammes (2 mots)
        bigrams = []
        for i in range(len(valid_words) - 1):
            word1, word2 = valid_words[i], valid_words[i+1]
            bigram = f"{word1} {word2}"
            bigrams.append(bigram)
        
        # Extraction de trigrammes (3 mots)
        trigrams = []
        for i in range(len(valid_words) - 2):
            word1, word2, word3 = valid_words[i], valid_words[i+1], valid_words[i+2]
            trigram = f"{word1} {word2} {word3}"
            trigrams.append(trigram)
        
        # Comptage des n-grammes
        ngram_freq = Counter(bigrams + trigrams)
        
        # Retour des N concepts les plus fréquents, avec validation finale
        concepts = []
        seen_concepts = set()  # Pour éviter les doublons
        
        for concept, freq in ngram_freq.most_common(top_n * 3):  # Prendre plus au départ pour filtrer
            if freq >= 2:  # Au moins 2 occurrences
                # Normaliser le concept pour détecter les doublons
                normalized = ' '.join(sorted(concept.split()))
                
                if normalized in seen_concepts:
                    continue  # Doublon détecté
                
                # Validation de qualité du concept
                words_in_concept = concept.split()
                
                # Vérifier la longueur totale (pas trop court, pas trop long)
                total_chars = sum(len(w) for w in words_in_concept)
                if total_chars < 8 or total_chars > 50:
                    continue
                
                # Vérifier qu'il y a au moins un mot "substantiel" (4+ lettres)
                has_substantial = any(len(w) >= 5 for w in words_in_concept)
                if not has_substantial:
                    continue
                
                # Vérifier qu'aucun mot n'est générique ou titre-like
                if any(w in ['résultats', 'exemple', 'cas', 'titre', 'partie', 'section'] for w in words_in_concept):
                    continue
                
                # Ajouter le concept validé
                concepts.append(concept)
                seen_concepts.add(normalized)
                
                if len(concepts) >= top_n:
                    break
        
        return concepts
    
    def _identify_important_sentences(
        self, 
        sentences: List[str], 
        keywords: List[str],
        concepts: List[str]
    ) -> List[Dict]:
        """
        Identifie les phrases les plus importantes basées sur les mots clés et concepts
        """
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) < 5:  # Phrases trop courtes
                continue
            
            sentence_lower = sentence.lower()
            
            # Score basé sur la présence de mots clés
            keyword_score = sum(1 for kw in keywords if kw in sentence_lower)
            
            # Score basé sur la présence de concepts
            concept_score = sum(2 for concept in concepts if concept in sentence_lower)
            
            # Bonus pour les marqueurs de définition
            definition_bonus = 3 if any(marker in sentence_lower for marker in self.definition_markers) else 0
            
            # Bonus pour les marqueurs causaux
            causal_bonus = 2 if any(marker in sentence_lower for marker in self.causal_markers) else 0
            
            # Score total
            total_score = keyword_score + concept_score + definition_bonus + causal_bonus
            
            if total_score > 0:
                scored_sentences.append({
                    'sentence': sentence,
                    'score': total_score,
                    'has_definition': definition_bonus > 0,
                    'has_causal': causal_bonus > 0
                })
        
        # Tri par score décroissant
        scored_sentences.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_sentences[:20]  # Top 20 phrases
    
    def _extract_definitions(self, sentences: List[str]) -> List[Dict]:
        """
        Extrait les définitions du texte
        """
        definitions = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Recherche de marqueurs de définition
            for marker in self.definition_markers:
                if marker in sentence_lower:
                    # Extraction du terme défini et de la définition
                    parts = sentence_lower.split(marker, 1)
                    if len(parts) == 2:
                        term = parts[0].strip().split()[-3:]  # Les derniers mots avant le marqueur
                        term = ' '.join(term)
                        definition = parts[1].strip()
                        
                        definitions.append({
                            'term': term,
                            'definition': definition,
                            'full_sentence': sentence
                        })
                    break
        
        return definitions[:10]  # Top 10 définitions
    
    def _extract_causal_relations(self, sentences: List[str]) -> List[Dict]:
        """
        Extrait les relations causales (cause -> effet)
        """
        causal_relations = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Recherche de marqueurs causaux
            for marker in self.causal_markers:
                if marker in sentence_lower:
                    parts = sentence_lower.split(marker, 1)
                    if len(parts) == 2:
                        cause = parts[0].strip()
                        effect = parts[1].strip()
                        
                        causal_relations.append({
                            'cause': cause,
                            'effect': effect,
                            'marker': marker,
                            'full_sentence': sentence
                        })
                    break
        
        return causal_relations[:10]  # Top 10 relations
    
    def _generate_summary(self, important_sentences: List[Dict]) -> str:
        """
        Génère un résumé à partir des phrases importantes
        """
        if not important_sentences:
            return "Aucun résumé disponible."
        
        summary_sentences = [sent['sentence'] for sent in important_sentences]
        return ' '.join(summary_sentences[:3])  # 3 premières phrases
    
    def _identify_main_topics(self, concepts: List[str], keywords: List[str]) -> List[str]:
        """
        Identifie les thèmes principaux à partir des concepts et mots clés
        """
        # Regroupement des concepts similaires
        topics = []
        
        # Utilisation des premiers concepts comme thèmes
        for concept in concepts[:5]:
            topics.append(concept.title())
        
        # Ajout de quelques mots clés importants
        for keyword in keywords[:3]:
            if keyword not in ' '.join(topics).lower():
                topics.append(keyword.title())
        
        return topics[:8]  # Maximum 8 thèmes
