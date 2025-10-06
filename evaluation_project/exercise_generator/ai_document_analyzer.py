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
        """Nettoie le texte en supprimant les caractères inutiles"""
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Suppression des retours à la ligne multiples
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extrait les phrases d'un texte"""
        # Découpage basique par ponctuation forte
        sentences = re.split(r'[.!?]+', text)
        # Nettoyage et filtrage
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences
    
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
        """
        # Mots à éviter absolument (pronoms, conjonctions, articles, etc.)
        invalid_words = {
            'elle', 'il', 'ils', 'elles', 'lui', 'leur', 'leurs', 'celui', 'celle', 'ceux', 'celles',
            'qui', 'que', 'quoi', 'dont', 'où', 'lequel', 'laquelle', 'lesquels', 'lesquelles',
            'lorsque', "lorsqu", 'quand', 'comme', 'si', 'mais', 'ou', 'et', 'donc', 'or', 'ni', 'car',
            'ce', 'cet', 'cette', 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'notre', 'votre', 'nos', 'vos', 'leur', 'leurs', 'quel', 'quelle', 'quels', 'quelles'
        }
        
        # Tokenisation
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]+\b', text.lower())
        
        # Extraction de bigrammes (2 mots)
        bigrams = []
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i+1]
            # Vérifier que les mots ne sont pas des stopwords ou des mots invalides
            if (word1 not in self.french_stopwords and word2 not in self.french_stopwords and
                word1 not in invalid_words and word2 not in invalid_words and
                len(word1) > 3 and len(word2) > 3):
                # Vérifier que c'est un concept substantiel (commence par une lettre minuscule dans le texte original)
                bigram = f"{word1} {word2}"
                bigrams.append(bigram)
        
        # Extraction de trigrammes (3 mots)
        trigrams = []
        for i in range(len(words) - 2):
            word1, word2, word3 = words[i], words[i+1], words[i+2]
            # Au moins 2 mots significatifs sur 3 et aucun mot invalide
            significant_words = [w for w in [word1, word2, word3] 
                               if w not in self.french_stopwords and w not in invalid_words and len(w) > 3]
            invalid_count = sum(1 for w in [word1, word2, word3] if w in invalid_words)
            
            if len(significant_words) >= 2 and invalid_count == 0:
                trigram = f"{word1} {word2} {word3}"
                trigrams.append(trigram)
        
        # Comptage des n-grammes
        ngram_freq = Counter(bigrams + trigrams)
        
        # Retour des N concepts les plus fréquents, avec validation finale
        concepts = []
        for concept, freq in ngram_freq.most_common(top_n * 2):  # Prendre plus au départ pour filtrer
            if freq >= 2:  # Au moins 2 occurrences
                # Validation finale : pas de pronoms ou conjonctions au début ou à la fin
                words_in_concept = concept.split()
                first_word = words_in_concept[0]
                last_word = words_in_concept[-1]
                
                if first_word not in invalid_words and last_word not in invalid_words:
                    # Vérifier qu'au moins un mot est un nom substantiel (commence par une voyelle ou consonne solide)
                    has_substantial_word = any(len(w) >= 4 for w in words_in_concept)
                    if has_substantial_word:
                        concepts.append(concept)
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
