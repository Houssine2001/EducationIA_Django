"""
Service d'analyse détaillée des performances par concepts
Analyse les réponses aux tests manuels ET IA pour identifier:
- Points forts spécifiques (concepts maîtrisés)
- Points faibles spécifiques (concepts à améliorer)
- Recommandations personnalisées
"""
from collections import defaultdict
from typing import Dict, List, Tuple
from django.db.models import Q


class ConceptAnalysisService:
    """
    Analyse les performances de l'étudiant au niveau des concepts/topics
    """
    
    def __init__(self, user, db_connection=None):
        """
        Args:
            user: L'utilisateur Django
            db_connection: Connexion MongoDB (optionnel, pour tests IA)
        """
        self.user = user
        self.db = db_connection
        
    def analyze_test_results(self, results_queryset) -> Dict:
        """
        Analyse les résultats des tests MANUELS
        
        Args:
            results_queryset: QuerySet de Result
            
        Returns:
            Dict avec strengths, weaknesses, et recommendations par sujet
        """
        from evaluation.models import Submission, Question
        
        analysis_by_subject = defaultdict(lambda: {
            'concepts': defaultdict(lambda: {
                'total': 0,
                'correct': 0,
                'questions': []
            }),
            'total_questions': 0,
            'correct_answers': 0
        })
        
        for result in results_queryset:
            subject = result.test.subject or 'Général'
            
            # Récupérer la soumission associée
            try:
                submission = Submission.objects.filter(
                    student=result.student,
                    test=result.test,
                    status='submitted'
                ).latest('submitted_at')
                
                # Les réponses sont dans submission.answers
                # Structure: {"question_id": {"answer": "...", "time_spent": 120, "is_correct": true}, ...}
                answers_data = submission.answers or {}
                
                for question_id, answer_info in answers_data.items():
                    try:
                        question = Question.objects.get(id=int(question_id))
                        # ✅ FIX: Utiliser le subject du test comme concept si question.concept est vide
                        concept = question.concept or question.topic or subject or 'Général'
                        
                        # Enregistrer la performance sur ce concept
                        analysis_by_subject[subject]['concepts'][concept]['total'] += 1
                        analysis_by_subject[subject]['total_questions'] += 1
                        
                        is_correct = answer_info.get('is_correct', False)
                        if is_correct:
                            analysis_by_subject[subject]['concepts'][concept]['correct'] += 1
                            analysis_by_subject[subject]['correct_answers'] += 1
                        
                        # Garder les questions pour référence
                        analysis_by_subject[subject]['concepts'][concept]['questions'].append({
                            'text': question.text,
                            'is_correct': is_correct,
                            'test_name': result.test.title,
                            'date': result.created_at
                        })
                    except Question.DoesNotExist:
                        continue
                    except (ValueError, KeyError):
                        continue
            except Submission.DoesNotExist:
                # Pas de soumission pour ce résultat
                continue
        
        return self._generate_insights(analysis_by_subject)
    
    def analyze_ai_test_results(self, ai_submissions: List[Dict]) -> Dict:
        """
        Analyse les résultats des tests IA (ExerciseSets)
        
        Args:
            ai_submissions: Liste des submissions MongoDB
            
        Returns:
            Dict avec strengths, weaknesses, et recommendations par sujet
        """
        from bson.objectid import ObjectId
        
        if self.db is None:
            return {}
        
        analysis_by_subject = defaultdict(lambda: {
            'concepts': defaultdict(lambda: {
                'total': 0,
                'correct': 0,
                'questions': []
            }),
            'total_questions': 0,
            'correct_answers': 0
        })
        
        for submission in ai_submissions:
            # Récupérer le set d'exercices
            set_id = submission.get('exercise_set_id')
            if not set_id:
                continue
            
            set_data = self.db.exercise_sets.find_one({'_id': ObjectId(set_id)})
            if not set_data:
                continue
            
            # Récupérer le sujet depuis le CourseDocument
            source_doc_id = set_data.get('source_document_id')
            subject = 'Général'
            if source_doc_id:
                doc_data = self.db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                if doc_data and doc_data.get('subject'):
                    subject = doc_data.get('subject').capitalize()
            
            # Récupérer les exercices du set
            exercise_ids = list(self.db.exercise_generator_exerciseset_exercises.find({
                'exerciseset_id': str(set_id)
            }))
            exercise_id_list = [ex['generatedexercise_id'] for ex in exercise_ids]
            
            exercises_data = list(self.db.generated_exercises.find({
                '_id': {'$in': [ObjectId(eid) if isinstance(eid, str) else eid for eid in exercise_id_list]}
            }))
            
            # Récupérer les réponses de l'étudiant
            answers = submission.get('answers', {})
            
            # Analyser chaque exercice
            for ex_data in exercises_data:
                exercise_id = str(ex_data['_id'])
                concept = ex_data.get('concept') or ex_data.get('topic') or 'Général'
                student_answer = answers.get(exercise_id)
                
                # Vérifier si la réponse est correcte
                options_data = ex_data.get('options_data', {})
                correct_answer = options_data.get('correct')
                exercise_type = ex_data.get('exercise_type')
                
                if exercise_type == 'true_false':
                    student_bool = (student_answer == 'True' or student_answer == 'true')
                    is_correct = (correct_answer == student_bool)
                else:
                    is_correct = (str(student_answer) == str(correct_answer)) if correct_answer else False
                
                # Enregistrer
                analysis_by_subject[subject]['concepts'][concept]['total'] += 1
                analysis_by_subject[subject]['total_questions'] += 1
                
                if is_correct:
                    analysis_by_subject[subject]['concepts'][concept]['correct'] += 1
                    analysis_by_subject[subject]['correct_answers'] += 1
                
                # Garder les questions
                analysis_by_subject[subject]['concepts'][concept]['questions'].append({
                    'text': ex_data.get('question_text', ''),
                    'is_correct': is_correct,
                    'test_name': set_data.get('title', 'Test IA'),
                    'date': submission.get('submitted_at')
                })
        
        return self._generate_insights(analysis_by_subject)
    
    def _generate_insights(self, analysis_by_subject: Dict) -> Dict:
        """
        Génère les points forts, faibles et recommandations
        
        Args:
            analysis_by_subject: Analyse brute par sujet et concept
            
        Returns:
            Dict structuré avec insights par sujet
        """
        insights_by_subject = {}
        
        for subject, data in analysis_by_subject.items():
            strengths = []
            weaknesses = []
            recommendations = []
            
            # Analyser chaque concept
            for concept, stats in data['concepts'].items():
                if stats['total'] == 0:
                    continue
                
                success_rate = (stats['correct'] / stats['total']) * 100
                
                # ✅ FIX: Reconnaissance des points forts même avec 1 seule question
                # Point fort: >=80% de réussite (au moins 1 question)
                if success_rate >= 80:
                    strengths.append({
                        'concept': concept,
                        'success_rate': round(success_rate, 1),
                        'total': stats['total'],
                        'correct': stats['correct'],
                        'description': self._get_strength_description(success_rate, stats['total'])
                    })
                
                # Point moyen: entre 60% et 79%
                elif 60 <= success_rate < 80:
                    # Ajouter comme recommandation d'amélioration (sans être une faiblesse)
                    recommendations.append(
                        f"📈 {concept}: Bon niveau ({success_rate:.0f}%), continuez à pratiquer pour atteindre l'excellence"
                    )
                
                # Point faible: <60% de réussite
                elif success_rate < 60:
                    weaknesses.append({
                        'concept': concept,
                        'success_rate': round(success_rate, 1),
                        'total': stats['total'],
                        'correct': stats['correct'],
                        'description': self._get_weakness_description(success_rate, stats['total'])
                    })
                    
                    # Générer recommandation détaillée
                    recommendations.append(
                        self._generate_recommendation(subject, concept, success_rate, stats['total'])
                    )
            
            # Trier par taux de réussite
            strengths.sort(key=lambda x: x['success_rate'], reverse=True)
            weaknesses.sort(key=lambda x: x['success_rate'])
            
            overall_success_rate = (data['correct_answers'] / data['total_questions'] * 100) if data['total_questions'] > 0 else 0
            
            insights_by_subject[subject] = {
                'strengths': strengths[:5],  # Top 5
                'weaknesses': weaknesses[:5],  # Top 5
                'recommendations': recommendations[:3],  # Top 3
                'overall_success_rate': round(overall_success_rate, 1),
                'total_questions': data['total_questions'],
                'correct_answers': data['correct_answers']
            }
        
        return insights_by_subject
    
    def _get_strength_description(self, success_rate: float, total_questions: int) -> str:
        """
        Description précise d'un point fort selon le score
        """
        if success_rate == 100:
            if total_questions == 1:
                return "✨ Parfait ! Question réussie avec brio"
            elif total_questions <= 3:
                return f"🎯 Excellence ! {total_questions} questions réussies à 100%"
            else:
                return f"🏆 Maîtrise parfaite ! {total_questions} questions sans erreur"
        elif success_rate >= 90:
            return f"⭐ Très bonne maîtrise ({total_questions} question{'s' if total_questions > 1 else ''})"
        elif success_rate >= 80:
            return f"👍 Bonne compréhension ({total_questions} question{'s' if total_questions > 1 else ''})"
        else:
            return f"Niveau correct ({total_questions} question{'s' if total_questions > 1 else ''})"
    
    def _get_weakness_description(self, success_rate: float, total_questions: int) -> str:
        """
        Description précise d'un point faible selon le score
        """
        if success_rate == 0:
            return f"⚠️ Concept à retravailler entièrement ({total_questions} question{'s' if total_questions > 1 else ''} échouée{'s' if total_questions > 1 else ''})"
        elif success_rate < 30:
            return f"🔴 Difficulté importante - révision approfondie nécessaire"
        elif success_rate < 50:
            return f"🟠 Concept partiellement compris - pratique recommandée"
        else:
            return f"🟡 Proche de la réussite - quelques révisions suffiront"
    
    def _generate_recommendation(self, subject: str, concept: str, success_rate: float, total_questions: int) -> str:
        """
        Génère une recommandation personnalisée et précise
        
        Args:
            subject: La matière
            concept: Le concept faible
            success_rate: Taux de réussite
            total_questions: Nombre de questions
            
        Returns:
            Recommandation textuelle détaillée
        """
        # Déterminer le niveau de difficulté et l'action appropriée
        if success_rate == 0:
            action = "📚 <strong>Révision complète nécessaire</strong>"
            detail = f"Commencez par revoir les bases de <strong>{concept}</strong> avant de passer aux exercices"
        elif success_rate < 30:
            action = "🔴 <strong>Travail approfondi requis</strong>"
            detail = f"Consacrez du temps à étudier <strong>{concept}</strong> avec des exemples pratiques"
        elif success_rate < 50:
            action = "🟠 <strong>Renforcement nécessaire</strong>"
            detail = f"Pratiquez davantage d'exercices sur <strong>{concept}</strong> pour consolider vos acquis"
        else:  # 50-59%
            action = "🟡 <strong>Derniers ajustements</strong>"
            detail = f"Quelques révisions ciblées sur <strong>{concept}</strong> vous permettront de progresser"
        
        # Recommandations spécifiques selon le nombre de questions
        if total_questions == 1:
            practice = "Refaites des exercices similaires pour valider votre compréhension"
        elif total_questions <= 3:
            practice = f"Les {total_questions} questions montrent des lacunes - multipliez les exercices"
        else:
            practice = f"Sur {total_questions} questions, vos erreurs révèlent des points à retravailler"
        
        return f"{action}: {detail}. {practice} en {subject}."
    
    def get_combined_analysis(self, manual_results, ai_submissions) -> Dict:
        """
        Combine l'analyse des tests manuels ET IA
        
        Returns:
            Dict avec analyse complète par sujet
        """
        # Analyser tests manuels
        manual_insights = self.analyze_test_results(manual_results)
        
        # Analyser tests IA
        ai_insights = self.analyze_ai_test_results(ai_submissions)
        
        # Combiner les deux
        combined_insights = {}
        all_subjects = set(list(manual_insights.keys()) + list(ai_insights.keys()))
        
        for subject in all_subjects:
            manual_data = manual_insights.get(subject, {
                'strengths': [],
                'weaknesses': [],
                'recommendations': [],
                'total_questions': 0,
                'correct_answers': 0
            })
            
            ai_data = ai_insights.get(subject, {
                'strengths': [],
                'weaknesses': [],
                'recommendations': [],
                'total_questions': 0,
                'correct_answers': 0
            })
            
            # Combiner les concepts
            combined_concepts = defaultdict(lambda: {'total': 0, 'correct': 0})
            
            # Ajouter concepts manuels
            for strength in manual_data['strengths']:
                concept = strength['concept']
                combined_concepts[concept]['total'] += strength['total']
                combined_concepts[concept]['correct'] += strength['correct']
            
            for weakness in manual_data['weaknesses']:
                concept = weakness['concept']
                combined_concepts[concept]['total'] += weakness['total']
                combined_concepts[concept]['correct'] += weakness['correct']
            
            # Ajouter concepts IA
            for strength in ai_data['strengths']:
                concept = strength['concept']
                combined_concepts[concept]['total'] += strength['total']
                combined_concepts[concept]['correct'] += strength['correct']
            
            for weakness in ai_data['weaknesses']:
                concept = weakness['concept']
                combined_concepts[concept]['total'] += weakness['total']
                combined_concepts[concept]['correct'] += weakness['correct']
            
            # Recalculer strengths/weaknesses
            strengths = []
            weaknesses = []
            recommendations = []
            
            for concept, stats in combined_concepts.items():
                if stats['total'] == 0:
                    continue
                
                success_rate = (stats['correct'] / stats['total']) * 100
                
                if success_rate >= 75 and stats['total'] >= 2:
                    strengths.append({
                        'concept': concept,
                        'success_rate': round(success_rate, 1),
                        'total': stats['total'],
                        'correct': stats['correct']
                    })
                elif success_rate < 60:
                    weaknesses.append({
                        'concept': concept,
                        'success_rate': round(success_rate, 1),
                        'total': stats['total'],
                        'correct': stats['correct']
                    })
                    recommendations.append(
                        self._generate_recommendation(subject, concept, success_rate, stats['total'])
                    )
            
            strengths.sort(key=lambda x: x['success_rate'], reverse=True)
            weaknesses.sort(key=lambda x: x['success_rate'])
            
            total_questions = manual_data['total_questions'] + ai_data['total_questions']
            correct_answers = manual_data['correct_answers'] + ai_data['correct_answers']
            overall_success_rate = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            combined_insights[subject] = {
                'strengths': strengths[:5],
                'weaknesses': weaknesses[:5],
                'recommendations': list(set(recommendations))[:3],  # Dédupliquer
                'overall_success_rate': round(overall_success_rate, 1),
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'has_manual_tests': manual_data['total_questions'] > 0,
                'has_ai_tests': ai_data['total_questions'] > 0
            }
        
        return combined_insights
