"""
Module pour la génération de feedback IA personnalisé
"""
from django.db.models import Avg
from .models import Result, Question


class AIFeedbackGenerator:
    """
    Générateur de feedback IA personnalisé basé sur les performances de l'étudiant
    """
    
    @staticmethod
    def generate_comprehensive_feedback(result, submission):
        """
        Génère un feedback complet avec points forts, lacunes et recommandations
        
        Args:
            result: Instance Result
            submission: Instance Submission
            
        Returns:
            dict: Analyse IA complète
        """
        test = result.test
        student = result.student
        answers = submission.answers or {}
        
        # Analyser les réponses
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'chapters_to_review': [],
            'exercises_to_redo': [],
            'overall_feedback': '',
            'encouragement': '',
            'detailed_analysis': {},
            'skill_mastery': {},
            'error_patterns': [],
            'time_management_analysis': ''
        }
        
        # 1. Analyser PRÉCISÉMENT chaque question
        correct_questions = []
        incorrect_questions = []
        skills_performance = {}
        question_types_performance = {'mcq': {'correct': 0, 'total': 0}, 
                                     'true_false': {'correct': 0, 'total': 0},
                                     'essay': {'correct': 0, 'total': 0}}
        
        for question in test.questions.all():
            q_id = str(question.id)
            answer_data = answers.get(q_id, {})
            
            if isinstance(answer_data, dict):
                is_correct = answer_data.get('is_correct', False)
            else:
                is_correct = False
            
            # Tracker par type de question
            q_type = question.question_type
            if q_type in question_types_performance:
                question_types_performance[q_type]['total'] += 1
                if is_correct:
                    question_types_performance[q_type]['correct'] += 1
            
            if is_correct:
                correct_questions.append(question)
                # Compter les compétences maîtrisées
                for skill in question.skills:
                    if skill not in skills_performance:
                        skills_performance[skill] = {
                            'correct': 0, 
                            'total': 0, 
                            'points_earned': 0,
                            'points_possible': 0,
                            'questions': []
                        }
                    skills_performance[skill]['correct'] += 1
                    skills_performance[skill]['total'] += 1
                    skills_performance[skill]['points_earned'] += question.points
                    skills_performance[skill]['points_possible'] += question.points
                    skills_performance[skill]['questions'].append({
                        'text': question.question_text[:100],
                        'correct': True
                    })
            else:
                incorrect_questions.append(question)
                # Compter les compétences à améliorer
                for skill in question.skills:
                    if skill not in skills_performance:
                        skills_performance[skill] = {
                            'correct': 0, 
                            'total': 0,
                            'points_earned': 0,
                            'points_possible': 0,
                            'questions': []
                        }
                    skills_performance[skill]['total'] += 1
                    skills_performance[skill]['points_possible'] += question.points
                    skills_performance[skill]['questions'].append({
                        'text': question.question_text[:100],
                        'correct': False
                    })
        
        # 2. Analyser PRÉCISÉMENT les compétences avec niveaux de maîtrise
        for skill, perf in skills_performance.items():
            if perf['total'] > 0:
                percentage = (perf['correct'] / perf['total']) * 100
                mastery_level = ''
                
                # Déterminer le niveau de maîtrise exact
                if percentage >= 90:
                    mastery_level = 'Expert'
                    analysis['strengths'].append(
                        f"🌟 **{skill}** - Maîtrise excellente ({percentage:.0f}%) - {perf['correct']}/{perf['total']} questions correctes"
                    )
                elif percentage >= 70:
                    mastery_level = 'Compétent'
                    analysis['strengths'].append(
                        f"✅ **{skill}** - Bonne maîtrise ({percentage:.0f}%) - {perf['correct']}/{perf['total']} questions correctes"
                    )
                elif percentage >= 50:
                    mastery_level = 'En développement'
                    analysis['weaknesses'].append(
                        f"⚠️ **{skill}** - À améliorer ({percentage:.0f}%) - Seulement {perf['correct']}/{perf['total']} questions correctes"
                    )
                    analysis['chapters_to_review'].append(
                        f"📖 Chapitre: **{skill}** - Révisez les concepts de base et refaites les exercices"
                    )
                else:
                    mastery_level = 'Débutant'
                    analysis['weaknesses'].append(
                        f"❌ **{skill}** - Lacune importante ({percentage:.0f}%) - {perf['total'] - perf['correct']}/{perf['total']} questions incorrectes"
                    )
                    analysis['chapters_to_review'].append(
                        f"🚨 **PRIORITÉ** - Chapitre: **{skill}** - Nécessite une révision complète"
                    )
                
                analysis['skill_mastery'][skill] = {
                    'percentage': round(percentage, 1),
                    'level': mastery_level,
                    'correct': perf['correct'],
                    'total': perf['total'],
                    'points_earned': perf['points_earned'],
                    'points_possible': perf['points_possible']
                }
        
        # 3. Analyser les PATTERNS d'erreurs par type de question
        for q_type, perf in question_types_performance.items():
            if perf['total'] > 0:
                percentage = (perf['correct'] / perf['total']) * 100
                type_names = {'mcq': 'Questions à Choix Multiples', 
                            'true_false': 'Questions Vrai/Faux',
                            'essay': 'Questions Rédactionnelles'}
                
                if percentage < 50:
                    analysis['error_patterns'].append(
                        f"🔍 Difficulté avec les **{type_names[q_type]}** - {perf['correct']}/{perf['total']} correctes ({percentage:.0f}%)"
                    )
                    
                    # Préparer la recommandation selon le type
                    if q_type == 'mcq':
                        strategy = "Éliminez d'abord les réponses évidemment fausses, puis comparez les options restantes"
                    else:
                        strategy = "Prenez le temps de bien lire chaque affirmation avant de répondre"
                    
                    analysis['recommendations'].append(
                        f"💡 Pratiquez davantage les **{type_names[q_type]}**. Stratégie: {strategy}"
                    )
        
        # 4. Générer un feedback TRÈS PRÉCIS basé sur le score
        score = result.percentage_score
        total_questions = test.questions.count()
        correct_count = len(correct_questions)
        incorrect_count = len(incorrect_questions)
        
        if score >= 90:
            analysis['overall_feedback'] = f"🏆 **Excellent travail !** Vous avez réussi {correct_count}/{total_questions} questions ({score:.1f}%). Vous maîtrisez parfaitement le sujet avec une performance exceptionnelle."
            analysis['encouragement'] = "🌟 Vous êtes au niveau expert ! Continuez à maintenir ce niveau d'excellence. Vous pourriez maintenant aider d'autres étudiants."
        elif score >= 75:
            analysis['overall_feedback'] = f"✅ **Très bon résultat !** Vous avez réussi {correct_count}/{total_questions} questions ({score:.1f}%). Vous avez une solide compréhension du sujet."
            analysis['encouragement'] = f"👍 Excellent niveau ! Avec un peu plus de révision sur {incorrect_count} point(s), vous atteindrez l'excellence."
        elif score >= 60:
            analysis['overall_feedback'] = f"📊 **Résultat correct.** Vous avez réussi {correct_count}/{total_questions} questions ({score:.1f}%). Vous comprenez les bases mais certains concepts nécessitent plus de travail."
            analysis['encouragement'] = f"💪 Vous êtes sur la bonne voie ! Concentrez-vous sur les {incorrect_count} questions manquées pour progresser rapidement."
        elif score >= 50:
            analysis['overall_feedback'] = f"⚠️ **Résultat passable.** Vous avez réussi {correct_count}/{total_questions} questions ({score:.1f}%). Il est important de consolider vos connaissances."
            analysis['encouragement'] = f"🔥 Ne vous découragez pas ! Avec du travail ciblé sur vos lacunes, vous pouvez améliorer votre score de {100 - score:.0f} points."
        else:
            analysis['overall_feedback'] = f"📚 **Vous devez travailler davantage.** Vous n'avez réussi que {correct_count}/{total_questions} questions ({score:.1f}%). Une révision approfondie est nécessaire."
            analysis['encouragement'] = f"💡 Chaque difficulté est une opportunité d'apprendre ! Concentrez-vous sur les bases et progressez étape par étape."
        
        # 5. Générer des recommandations TRÈS SPÉCIFIQUES
        if incorrect_questions:
            # Recommandations par compétence faible
            weak_skills = [skill for skill, data in analysis['skill_mastery'].items() 
                          if data['percentage'] < 60]
            
            if weak_skills:
                analysis['recommendations'].append(
                    f"🎯 **Priorité #1**: Concentrez-vous sur {', '.join(weak_skills[:2])} - Ce sont vos lacunes principales"
                )
            
            # Recommandations par nombre d'erreurs
            if incorrect_count >= total_questions * 0.7:
                analysis['recommendations'].append(
                    f"📖 **Révision complète nécessaire** - Reprenez le cours depuis le début, prenez des notes détaillées"
                )
                analysis['recommendations'].append(
                    f"👥 **Demandez de l'aide** - Consultez votre professeur ou rejoignez un groupe d'étude"
                )
            elif incorrect_count >= total_questions * 0.4:
                analysis['recommendations'].append(
                    f"📝 **Révision ciblée** - Refaites les exercices sur les {len(weak_skills)} compétences identifiées"
                )
                analysis['recommendations'].append(
                    f"⏱️ **Pratiquez régulièrement** - 30 minutes par jour pendant 1 semaine sur vos points faibles"
                )
            else:
                analysis['recommendations'].append(
                    f"🔍 **Peaufinage** - Quelques révisions suffiront pour atteindre l'excellence"
                )
            
            # Recommandations par type d'erreur
            mcq_errors = [q for q in incorrect_questions if q.question_type == 'mcq']
            if len(mcq_errors) > len(incorrect_questions) * 0.6:
                analysis['recommendations'].append(
                    f"💭 **Stratégie QCM** - Lisez TOUTES les options avant de choisir. Éliminez d'abord les réponses absurdes"
                )
        
        # 6. Suggestions d'exercices TRÈS PRÉCISES
        if incorrect_questions:
            for skill, data in analysis['skill_mastery'].items():
                if data['percentage'] < 60:
                    exercises_needed = max(5, int((100 - data['percentage']) / 10))
                    analysis['exercises_to_redo'].append({
                        'skill': skill,
                        'recommendation': f"Faire **{exercises_needed} exercices** sur ce thème. Visez 80% de réussite avant de passer au suivant.",
                        'priority': 'Haute' if data['percentage'] < 40 else 'Moyenne',
                        'estimated_time': f"{exercises_needed * 5}-{exercises_needed * 10} minutes"
                    })
        
        # 7. Analyse de gestion du temps
        if submission.time_spent and test.duration:
            time_ratio = submission.time_spent / (test.duration * 60)
            avg_time_per_q = submission.time_spent / total_questions
            
            if time_ratio > 0.95:
                analysis['time_management_analysis'] = f"⏱️ Vous avez utilisé {time_ratio*100:.0f}% du temps - Vous devriez pratiquer en vous chronométrant"
                analysis['recommendations'].append(
                    f"🕐 **Gestion du temps** - Allouez maximum {test.duration*60/total_questions:.0f}s par question. "
                    f"Actuellement: {avg_time_per_q:.0f}s/question"
                )
            elif time_ratio < 0.5:
                analysis['time_management_analysis'] = f"⚡ Vous avez utilisé seulement {time_ratio*100:.0f}% du temps - Prenez plus de temps pour réfléchir"
                analysis['recommendations'].append(
                    f"🤔 **Relecture importante** - Vous allez trop vite. Relisez vos réponses avant de soumettre"
                )
        
        # 8. Analyse comparative avec la moyenne
        from django.db.models import Avg
        avg_score = Result.objects.filter(test=test).aggregate(
            avg=Avg('percentage_score')
        )['avg'] or 0
        
        if avg_score > 0:
            diff = score - avg_score
            if diff > 15:
                analysis['encouragement'] += f" 🏅 Vous êtes **{diff:.0f} points au-dessus** de la moyenne ({avg_score:.1f}%) !"
            elif diff > 5:
                analysis['encouragement'] += f" 👏 Vous êtes légèrement au-dessus de la moyenne ({avg_score:.1f}%)"
            elif diff < -15:
                analysis['recommendations'].append(
                    f"📊 Vous êtes {abs(diff):.0f} points en dessous de la moyenne ({avg_score:.1f}%). "
                    f"Consultez les ressources du cours et les corrections détaillées"
                )
        
        return analysis
    
    @staticmethod
    def generate_learning_path(student, subject):
        """
        Génère un parcours d'apprentissage personnalisé basé sur l'historique
        
        Args:
            student: Instance User
            subject: Sujet/matière
            
        Returns:
            dict: Parcours d'apprentissage recommandé
        """
        results = Result.objects.filter(
            student=student,
            test__subject=subject
        ).order_by('-created_at')[:5]
        
        if not results:
            return {
                'status': 'new_learner',
                'recommendations': [
                    f"Commencez par les bases de {subject}",
                    "Pratiquez régulièrement (15-30 min par jour)",
                    "N'hésitez pas à revoir les concepts difficiles"
                ]
            }
        
        # Analyser la progression
        scores = [r.percentage_score for r in results]
        avg_score = sum(scores) / len(scores)
        
        # Détecter la tendance
        if len(scores) >= 3:
            recent_avg = sum(scores[:2]) / 2
            older_avg = sum(scores[2:]) / len(scores[2:])
            
            if recent_avg > older_avg + 5:
                trend = 'improving'
            elif recent_avg < older_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        learning_path = {
            'current_level': 'beginner' if avg_score < 60 else 'intermediate' if avg_score < 80 else 'advanced',
            'trend': trend,
            'average_score': avg_score,
            'recommendations': []
        }
        
        # Recommandations basées sur le niveau et la tendance
        if trend == 'improving':
            learning_path['recommendations'].append("Excellent ! Vous êtes en progression. Continuez sur cette lancée !")
        elif trend == 'declining':
            learning_path['recommendations'].append(
                "Attention, vos résultats baissent. Prenez le temps de consolider vos acquis."
            )
        
        if avg_score < 60:
            learning_path['recommendations'].extend([
                f"Revoir les fondamentaux de {subject}",
                "Pratiquer des exercices simples pour consolider les bases",
                "Demander de l'aide si nécessaire"
            ])
        elif avg_score < 80:
            learning_path['recommendations'].extend([
                "Approfondir les concepts avancés",
                "Pratiquer des exercices de niveau intermédiaire",
                "Participer à des projets pratiques"
            ])
        else:
            learning_path['recommendations'].extend([
                "Relever des défis plus complexes",
                "Aider d'autres étudiants (méthode d'apprentissage par enseignement)",
                "Explorer des sujets connexes avancés"
            ])
        
        return learning_path
