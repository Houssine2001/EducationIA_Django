# ==========================================
# Gamification Service - Badges & Classements
# ==========================================
"""
Système de gamification pour motiver les étudiants.

Fonctionnalités:
- Badges et achievements
- Classements (leaderboards)
- Points d'expérience (XP)
- Niveaux et rangs
- Défis et objectifs
"""

from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta


class GamificationService:
    """
    Service de gamification pour le système d'évaluation.
    """
    
    # Définition des badges disponibles
    BADGES = {
        # BADGES DE SCORE
        'perfect_score': {
            'name': 'Score Parfait',
            'description': 'Obtenir 100% à un test',
            'icon': '🏆',
            'color': 'gold',
            'rarity': 'epic',
            'points': 100
        },
        'high_achiever': {
            'name': 'Haut Niveau',
            'description': 'Obtenir plus de 90% à 5 tests',
            'icon': '⭐',
            'color': 'yellow',
            'rarity': 'rare',
            'points': 50
        },
        'consistent_performer': {
            'name': 'Régulier',
            'description': 'Obtenir plus de 70% à 10 tests consécutifs',
            'icon': '📊',
            'color': 'blue',
            'rarity': 'uncommon',
            'points': 30
        },
        
        # BADGES DE PROGRESSION
        'fast_learner': {
            'name': 'Apprenant Rapide',
            'description': 'Améliorer son score de 20% en une semaine',
            'icon': '🚀',
            'color': 'purple',
            'rarity': 'rare',
            'points': 40
        },
        'comeback_king': {
            'name': 'Retour en Force',
            'description': 'Passer de <60% à >80%',
            'icon': '💪',
            'color': 'orange',
            'rarity': 'rare',
            'points': 45
        },
        
        # BADGES DE PARTICIPATION
        'dedicated_student': {
            'name': 'Étudiant Dévoué',
            'description': 'Compléter 20 tests',
            'icon': '📚',
            'color': 'green',
            'rarity': 'common',
            'points': 20
        },
        'marathon_runner': {
            'name': 'Marathonien',
            'description': 'Compléter 50 tests',
            'icon': '🏃',
            'color': 'red',
            'rarity': 'epic',
            'points': 80
        },
        'daily_streak_7': {
            'name': 'Série de 7 jours',
            'description': 'Passer au moins un test pendant 7 jours consécutifs',
            'icon': '🔥',
            'color': 'orange',
            'rarity': 'uncommon',
            'points': 25
        },
        'daily_streak_30': {
            'name': 'Série de 30 jours',
            'description': 'Passer au moins un test pendant 30 jours consécutifs',
            'icon': '🔥🔥',
            'color': 'red',
            'rarity': 'legendary',
            'points': 150
        },
        
        # BADGES DE MAÎTRISE
        'subject_master': {
            'name': 'Maître de Matière',
            'description': 'Obtenir >90% de moyenne dans une matière',
            'icon': '🎓',
            'color': 'gold',
            'rarity': 'rare',
            'points': 60
        },
        'all_rounder': {
            'name': 'Polyvalent',
            'description': 'Obtenir >75% dans 5 matières différentes',
            'icon': '🌟',
            'color': 'rainbow',
            'rarity': 'epic',
            'points': 90
        },
        
        # BADGES DE VITESSE
        'speed_demon': {
            'name': 'Démon de Vitesse',
            'description': 'Terminer un test en moins de la moitié du temps',
            'icon': '⚡',
            'color': 'yellow',
            'rarity': 'uncommon',
            'points': 35
        },
        
        # BADGES SPÉCIAUX
        'first_test': {
            'name': 'Premier Pas',
            'description': 'Compléter votre premier test',
            'icon': '🎯',
            'color': 'blue',
            'rarity': 'common',
            'points': 10
        },
        'ai_master': {
            'name': 'Maître de l\'IA',
            'description': 'Obtenir >90% sur 5 questions corrigées par IA',
            'icon': '🤖',
            'color': 'purple',
            'rarity': 'epic',
            'points': 100
        }
    }
    
    # Niveaux et XP requis
    LEVELS = [
        {'level': 1, 'xp_required': 0, 'title': 'Débutant'},
        {'level': 2, 'xp_required': 100, 'title': 'Novice'},
        {'level': 3, 'xp_required': 250, 'title': 'Apprenti'},
        {'level': 4, 'xp_required': 500, 'title': 'Étudiant'},
        {'level': 5, 'xp_required': 1000, 'title': 'Avancé'},
        {'level': 6, 'xp_required': 2000, 'title': 'Expert'},
        {'level': 7, 'xp_required': 3500, 'title': 'Maître'},
        {'level': 8, 'xp_required': 5500, 'title': 'Grand Maître'},
        {'level': 9, 'xp_required': 8000, 'title': 'Virtuose'},
        {'level': 10, 'xp_required': 12000, 'title': 'Légende'},
    ]
    
    
    def __init__(self, student_profile):
        """
        Initialiser le service de gamification.
        
        Args:
            student_profile: Instance de UserProfile
        """
        self.profile = student_profile
        self.user = student_profile.user
    
    
    def check_and_award_badges(self):
        """
        Vérifier et attribuer les nouveaux badges mérités.
        
        Processus:
        1. Récupérer tous les résultats de l'étudiant
        2. Vérifier chaque condition de badge
        3. Attribuer les nouveaux badges
        4. Mettre à jour les points XP
        
        Returns:
            list: Nouveaux badges obtenus
        """
        from evaluation.models import Result, Submission
        
        # Récupérer les badges déjà obtenus
        current_badges = self.profile.badges or []
        current_badge_ids = [b['badge_id'] for b in current_badges]
        
        # Liste des nouveaux badges
        new_badges = []
        
        # Récupérer les données nécessaires
        results = Result.objects.filter(student=self.user)
        submissions = Submission.objects.filter(student=self.user, status='completed')
        
        # VÉRIFIER CHAQUE BADGE
        
        # 1. Premier test
        if 'first_test' not in current_badge_ids and results.count() >= 1:
            new_badges.append(self._award_badge('first_test'))
        
        # 2. Score parfait
        if 'perfect_score' not in current_badge_ids and results.filter(percentage_score=100).count() > 0:
            new_badges.append(self._award_badge('perfect_score'))
        
        # 3. High Achiever (5 tests >90%)
        if 'high_achiever' not in current_badge_ids and results.filter(percentage_score__gte=90).count() >= 5:
            new_badges.append(self._award_badge('high_achiever'))
        
        # 4. Consistent Performer (10 tests consécutifs >70%)
        if 'consistent_performer' not in current_badge_ids:
            if self._check_consecutive_scores(results, 70, 10):
                new_badges.append(self._award_badge('consistent_performer'))
        
        # 5. Dedicated Student (20 tests)
        if 'dedicated_student' not in current_badge_ids and results.count() >= 20:
            new_badges.append(self._award_badge('dedicated_student'))
        
        # 6. Marathon Runner (50 tests)
        if 'marathon_runner' not in current_badge_ids and results.count() >= 50:
            new_badges.append(self._award_badge('marathon_runner'))
        
        # 7. Fast Learner (amélioration de 20% en 1 semaine)
        if 'fast_learner' not in current_badge_ids:
            if self._check_fast_improvement(results):
                new_badges.append(self._award_badge('fast_learner'))
        
        # 8. Comeback King (<60% à >80%)
        if 'comeback_king' not in current_badge_ids:
            if self._check_comeback(results):
                new_badges.append(self._award_badge('comeback_king'))
        
        # 9. Daily Streak 7 jours - DÉSACTIVÉ (nécessite current_streak dans UserProfile)
        # if 'daily_streak_7' not in current_badge_ids:
        #     if self.profile.current_streak >= 7:
        #         new_badges.append(self._award_badge('daily_streak_7'))
        
        # 10. Daily Streak 30 jours - DÉSACTIVÉ (nécessite current_streak dans UserProfile)
        # if 'daily_streak_30' not in current_badge_ids:
        #     if self.profile.current_streak >= 30:
        #         new_badges.append(self._award_badge('daily_streak_30'))
        
        # 11. Subject Master (>90% dans une matière)
        if 'subject_master' not in current_badge_ids:
            if self._check_subject_mastery(results):
                new_badges.append(self._award_badge('subject_master'))
        
        # 12. All Rounder (>75% dans 5 matières)
        if 'all_rounder' not in current_badge_ids:
            if self._check_all_rounder(results):
                new_badges.append(self._award_badge('all_rounder'))
        
        # 13. Speed Demon (terminer en <50% du temps)
        if 'speed_demon' not in current_badge_ids:
            if self._check_speed_demon(submissions):
                new_badges.append(self._award_badge('speed_demon'))
        
        # Mettre à jour le profil
        if new_badges:
            self.profile.badges = current_badges + new_badges
            
            # Ajouter les points XP
            total_xp_gained = sum([b['points'] for b in new_badges])
            self.profile.total_xp = (self.profile.total_xp or 0) + total_xp_gained
            
            # Recalculer le niveau
            self.profile.level = self._calculate_level(self.profile.total_xp)
            
            self.profile.save()
        
        return new_badges
    
    
    def _award_badge(self, badge_id):
        """Créer un objet badge à attribuer."""
        badge_data = self.BADGES[badge_id]
        
        return {
            'badge_id': badge_id,
            'name': badge_data['name'],
            'description': badge_data['description'],
            'icon': badge_data['icon'],
            'color': badge_data['color'],
            'rarity': badge_data['rarity'],
            'points': badge_data['points'],
            'earned_at': timezone.now().isoformat()
        }
    
    
    def _calculate_level(self, total_xp):
        """Calculer le niveau basé sur l'XP total."""
        for i in range(len(self.LEVELS) - 1, -1, -1):
            if total_xp >= self.LEVELS[i]['xp_required']:
                return self.LEVELS[i]['level']
        return 1
    
    
    def get_level_info(self):
        """Obtenir les infos du niveau actuel."""
        current_xp = self.profile.total_xp or 0
        current_level = self.profile.level or 1
        
        # Trouver le niveau actuel et le suivant
        current_level_data = next((l for l in self.LEVELS if l['level'] == current_level), self.LEVELS[0])
        next_level_data = next((l for l in self.LEVELS if l['level'] == current_level + 1), None)
        
        if next_level_data:
            xp_for_next = next_level_data['xp_required'] - current_xp
            progress = ((current_xp - current_level_data['xp_required']) / 
                       (next_level_data['xp_required'] - current_level_data['xp_required'])) * 100
        else:
            xp_for_next = 0
            progress = 100
        
        return {
            'current_level': current_level,
            'current_title': current_level_data['title'],
            'current_xp': current_xp,
            'next_level': next_level_data['level'] if next_level_data else None,
            'next_title': next_level_data['title'] if next_level_data else 'Max Level',
            'xp_for_next_level': xp_for_next,
            'progress_percentage': round(progress, 2)
        }
    
    
    def _check_consecutive_scores(self, results, min_score, count):
        """Vérifier si l'étudiant a eu X scores consécutifs >= min_score."""
        # Convertir en liste pour éviter les problèmes avec djongo count() après slicing
        ordered_results = list(results.order_by('-created_at')[:count])
        
        if len(ordered_results) < count:
            return False
        
        return all(r.percentage_score >= min_score for r in ordered_results)
    
    
    def _check_fast_improvement(self, results):
        """Vérifier amélioration de 20% en 1 semaine."""
        now = timezone.now()
        one_week_ago = now - timedelta(days=7)
        
        recent = results.filter(created_at__gte=one_week_ago)
        older = results.filter(created_at__lt=one_week_ago)
        
        if not recent.count() > 0 or not older.count() > 0:
            return False
        
        # Correction: utiliser percentage_score au lieu de percentage
        recent_avg = recent.aggregate(Avg('percentage_score'))['percentage_score__avg']
        older_avg = older.aggregate(Avg('percentage_score'))['percentage_score__avg']
        
        if recent_avg and older_avg:
            return (recent_avg - older_avg) >= 20
        
        return False
    
    
    def _check_comeback(self, results):
        """Vérifier si passé de <60% à >80%."""
        ordered = results.order_by('created_at')
        
        if ordered.count() < 2:
            return False
        
        # Trouver un test <60% suivi d'un test >80%
        had_low = False
        for result in ordered:
            if result.percentage_score < 60:
                had_low = True
            elif had_low and result.percentage_score > 80:
                return True
        
        return False
    
    
    def _check_subject_mastery(self, results):
        """Vérifier >90% de moyenne dans une matière."""
        from django.db.models import Avg
        
        subjects = results.values('test__subject').annotate(
            avg_score=Avg('percentage_score')
        )
        
        return any(s.get('avg_score', 0) >= 90 for s in subjects)
    
    
    def _check_all_rounder(self, results):
        """Vérifier >75% dans 5 matières différentes."""
        from django.db.models import Avg
        
        subjects = results.values('test__subject').annotate(
            avg_score=Avg('percentage_score')
        )
        
        high_subjects = [s for s in subjects if s.get('avg_score', 0) >= 75]
        
        return len(high_subjects) >= 5
    
    
    def _check_speed_demon(self, submissions):
        """Vérifier si terminé en <50% du temps."""
        for submission in submissions:
            if submission.start_time and submission.submitted_at:
                actual_time = (submission.submitted_at - submission.start_time).total_seconds() / 60
                allowed_time = submission.test.time_limit
                
                if allowed_time and actual_time < (allowed_time * 0.5):
                    return True
        
        return False
    
    
    def get_leaderboard(self, period='all_time', subject=None, limit=10):
        """
        Obtenir le classement des étudiants.
        
        Args:
            period: 'all_time', 'monthly', 'weekly'
            subject: Filtrer par matière (optionnel)
            limit: Nombre de résultats à retourner
            
        Returns:
            list: Classement des étudiants
        """
        from evaluation.models import UserProfile, Result
        from django.db.models import Avg, Count
        
        # Filtrer par période
        now = timezone.now()
        if period == 'weekly':
            date_filter = now - timedelta(days=7)
        elif period == 'monthly':
            date_filter = now - timedelta(days=30)
        else:
            date_filter = None
        
        # Construire le query
        results_query = Result.objects.all()
        if date_filter:
            results_query = results_query.filter(created_at__gte=date_filter)
        if subject:
            results_query = results_query.filter(test__subject=subject)
        
        # Calculer les moyennes par étudiant
        student_stats = results_query.values('student').annotate(
            avg_score=Avg('percentage_score'),
            test_count=Count('id')
        ).order_by('-avg_score')[:limit]
        
        # Construire le leaderboard
        leaderboard = []
        for rank, stat in enumerate(student_stats, start=1):
            try:
                profile = UserProfile.objects.get(user_id=stat['student'])
                
                leaderboard.append({
                    'rank': rank,
                    'student_id': stat['student'],
                    'student_name': profile.user.get_full_name() or profile.user.username,
                    'average_score': round(stat['avg_score'], 2),
                    'test_count': stat['test_count'],
                    'level': profile.level or 1,
                    'total_xp': profile.total_xp or 0,
                    'badge_count': len(profile.badges or []),
                    'is_current_user': (profile.user == self.user)
                })
            except UserProfile.DoesNotExist:
                continue
        
        return leaderboard
    
    
    def get_student_rank(self, period='all_time', subject=None):
        """
        Obtenir le rang de l'étudiant actuel.
        
        Returns:
            dict: Position dans le classement
        """
        leaderboard = self.get_leaderboard(period=period, subject=subject, limit=1000)
        
        for item in leaderboard:
            if item['is_current_user']:
                return {
                    'rank': item['rank'],
                    'total_students': len(leaderboard),
                    'percentile': round((1 - (item['rank'] / len(leaderboard))) * 100, 2),
                    'average_score': item['average_score']
                }
        
        return None


    def get_badge_progress(self):
        """
        Obtenir la progression de TOUS les badges (obtenus et non obtenus).
        
        Returns:
            dict: {
                'earned_badges': [...],  # Badges obtenus
                'available_badges': [...] # Badges disponibles avec progression
            }
        """
        from evaluation.models import Result, Submission
        
        # Récupérer les badges déjà obtenus
        current_badges = self.profile.badges or []
        current_badge_ids = [b['badge_id'] for b in current_badges]
        
        # Récupérer les données nécessaires
        results = Result.objects.filter(student=self.user)
        submissions = Submission.objects.filter(student=self.user, status='completed')
        
        # Liste des badges disponibles avec progression
        available_badges = []
        
        for badge_id, badge_data in self.BADGES.items():
            # Vérifier si le badge est déjà obtenu
            is_earned = badge_id in current_badge_ids
            
            # Calculer la progression
            progress = self._calculate_badge_progress(badge_id, results, submissions)
            
            badge_info = {
                'badge_id': badge_id,
                'name': badge_data['name'],
                'description': badge_data['description'],
                'icon': badge_data['icon'],
                'color': badge_data['color'],
                'rarity': badge_data['rarity'],
                'points': badge_data['points'],
                'is_earned': is_earned,
                'progress': progress['current'],
                'target': progress['target'],
                'progress_percentage': progress['percentage']
            }
            
            if is_earned:
                # Trouver la date d'obtention
                earned_badge = next((b for b in current_badges if b['badge_id'] == badge_id), None)
                if earned_badge:
                    badge_info['earned_at'] = earned_badge.get('earned_at')
            
            available_badges.append(badge_info)
        
        return {
            'earned_badges': [b for b in available_badges if b['is_earned']],
            'available_badges': [b for b in available_badges if not b['is_earned']]
        }
    
    
    def _calculate_badge_progress(self, badge_id, results, submissions):
        """
        Calculer la progression d'un badge spécifique.
        
        Returns:
            dict: {'current': int, 'target': int, 'percentage': float}
        """
        current = 0
        target = 1
        
        # Calculer selon le type de badge
        if badge_id == 'first_test':
            current = min(results.count(), 1)
            target = 1
        
        elif badge_id == 'perfect_score':
            current = min(results.filter(percentage_score=100).count(), 1)
            target = 1
        
        elif badge_id == 'high_achiever':
            current = results.filter(percentage_score__gte=90).count()
            target = 5
        
        elif badge_id == 'consistent_performer':
            # Vérifier les 10 derniers tests
            recent_10 = results.order_by('-created_at')[:10]
            current = sum(1 for r in recent_10 if r.percentage_score >= 70)
            target = 10
        
        elif badge_id == 'dedicated_student':
            current = results.count()
            target = 20
        
        elif badge_id == 'marathon_runner':
            current = results.count()
            target = 50
        
        elif badge_id == 'fast_learner':
            # Vérifier amélioration
            if self._check_fast_improvement(results):
                current = 1
            target = 1
        
        elif badge_id == 'comeback_king':
            # Vérifier comeback
            if self._check_comeback(results):
                current = 1
            target = 1
        
        elif badge_id == 'daily_streak_7':
            # DÉSACTIVÉ - nécessite current_streak dans UserProfile
            current = 0
            target = 7
        
        elif badge_id == 'daily_streak_30':
            # DÉSACTIVÉ - nécessite current_streak dans UserProfile
            current = 0
            target = 30
        
        elif badge_id == 'subject_master':
            # Vérifier >90% dans une matière
            from django.db.models import Avg
            subjects = results.values('test__subject').annotate(
                avg_score=Avg('percentage_score')
            )
            high_subjects = [s for s in subjects if s.get('avg_score', 0) >= 90]
            current = min(len(high_subjects), 1)
            target = 1
        
        elif badge_id == 'all_rounder':
            # Vérifier >75% dans 5 matières
            from django.db.models import Avg
            subjects = results.values('test__subject').annotate(
                avg_score=Avg('percentage_score')
            )
            high_subjects = [s for s in subjects if s.get('avg_score', 0) >= 75]
            current = len(high_subjects)
            target = 5
        
        elif badge_id == 'speed_demon':
            # Vérifier vitesse
            if self._check_speed_demon(submissions):
                current = 1
            target = 1
        
        elif badge_id == 'ai_master':
            # Vérifier >90% sur 5 questions IA
            ai_correct = 0
            for sub in submissions:
                if hasattr(sub, 'answers') and sub.answers:
                    answers = sub.answers if isinstance(sub.answers, dict) else {}
                    for ans_info in answers.values():
                        if isinstance(ans_info, dict) and ans_info.get('is_correct'):
                            ai_correct += 1
            current = min(ai_correct, 5)
            target = 5
        
        # Calculer le pourcentage
        percentage = (current / target * 100) if target > 0 else 0
        percentage = min(percentage, 100)  # Max 100%
        
        return {
            'current': current,
            'target': target,
            'percentage': round(percentage, 1)
        }
