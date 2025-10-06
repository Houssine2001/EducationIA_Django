"""
Commande pour générer et attribuer des badges réalistes aux étudiants.

Usage:
    python manage.py generate_badges
    python manage.py generate_badges --student username
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evaluation.models import UserProfile, Result
from django.db.models import Count, Avg


class Command(BaseCommand):
    help = 'Génère et attribue des badges aux étudiants basés sur leurs performances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student',
            type=str,
            help='Générer badges pour un étudiant spécifique (username)'
        )

    def handle(self, *args, **options):
        """Point d'entrée de la commande"""
        student_username = options.get('student')
        
        if student_username:
            try:
                user = User.objects.get(username=student_username)
                profile = UserProfile.objects.get(user=user)
                self.generate_badges_for_student(profile)
                self.stdout.write(self.style.SUCCESS(f'✅ Badges générés pour {student_username}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Utilisateur {student_username} introuvable'))
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Profil introuvable pour {student_username}'))
        else:
            # Générer pour tous les étudiants (utilisateurs non-staff)
            students = UserProfile.objects.filter(user__is_staff=False, user__is_superuser=False)
            count = 0
            
            self.stdout.write('Génération des badges...\n')
            
            for profile in students:
                self.generate_badges_for_student(profile)
                count += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Badges générés pour {count} étudiant(s)'))

    def generate_badges_for_student(self, profile):
        """Générer et attribuer des badges à un étudiant"""
        user = profile.user
        badges = []
        
        # Récupérer statistiques
        results = Result.objects.filter(student=user)
        total_tests = results.count()
        
        if total_tests == 0:
            self.stdout.write(f'  ⚠ {user.username}: Aucun test passé')
            return
        
        avg_score = results.aggregate(Avg('percentage_score'))['percentage_score__avg'] or 0
        perfect_scores = results.filter(percentage_score=100).count()
        passed_tests = results.filter(percentage_score__gte=60).count()
        
        # 1. BADGE "PREMIER PAS" - Premier test terminé
        if total_tests >= 1:
            badges.append({
                'name': '🎯 Premier Pas',
                'description': 'Votre premier test terminé',
                'icon': '🎯',
                'category': 'progression',
                'earned_at': results.order_by('created_at').first().created_at.strftime('%Y-%m-%d')
            })
        
        # 2. BADGE "NOVICE" - 5 tests
        if total_tests >= 5:
            badges.append({
                'name': '📚 Novice',
                'description': '5 tests terminés',
                'icon': '📚',
                'category': 'progression',
                'earned_at': results.order_by('created_at')[4].created_at.strftime('%Y-%m-%d')
            })
        
        # 3. BADGE "INTERMÉDIAIRE" - 10 tests
        if total_tests >= 10:
            badges.append({
                'name': '🎓 Intermédiaire',
                'description': '10 tests terminés',
                'icon': '🎓',
                'category': 'progression',
                'earned_at': results.order_by('created_at')[9].created_at.strftime('%Y-%m-%d')
            })
        
        # 4. BADGE "AVANCÉ" - 20 tests
        if total_tests >= 20:
            badges.append({
                'name': '🏆 Avancé',
                'description': '20 tests terminés',
                'icon': '🏆',
                'category': 'progression',
                'earned_at': results.order_by('created_at')[19].created_at.strftime('%Y-%m-%d')
            })
        
        # 5. BADGE "EXPERT" - 50 tests
        if total_tests >= 50:
            badges.append({
                'name': '👑 Expert',
                'description': '50 tests terminés',
                'icon': '👑',
                'category': 'progression',
                'earned_at': results.order_by('created_at')[49].created_at.strftime('%Y-%m-%d')
            })
        
        # 6. BADGE "PERFECTIONNISTE" - Au moins 1 score parfait
        if perfect_scores >= 1:
            perfect_result = results.filter(percentage_score=100).first()
            badges.append({
                'name': '💎 Perfectionniste',
                'description': f'Score parfait obtenu ({perfect_result.test.title})',
                'icon': '💎',
                'category': 'performance',
                'earned_at': perfect_result.created_at.strftime('%Y-%m-%d')
            })
        
        # 7. BADGE "TRIPLE PARFAIT" - 3 scores parfaits
        if perfect_scores >= 3:
            badges.append({
                'name': '⭐ Triple Parfait',
                'description': f'{perfect_scores} scores parfaits',
                'icon': '⭐',
                'category': 'performance',
                'earned_at': results.filter(percentage_score=100).order_by('created_at')[2].created_at.strftime('%Y-%m-%d')
            })
        
        # 8. BADGE "EXCELLENT" - Moyenne >= 80%
        if avg_score >= 80:
            badges.append({
                'name': '🌟 Excellent',
                'description': f'Moyenne de {avg_score:.1f}%',
                'icon': '🌟',
                'category': 'performance'
            })
        
        # 9. BADGE "BON ÉLÈVE" - Moyenne >= 70%
        elif avg_score >= 70:
            badges.append({
                'name': '✨ Bon Élève',
                'description': f'Moyenne de {avg_score:.1f}%',
                'icon': '✨',
                'category': 'performance'
            })
        
        # 10. BADGE "PERSÉVÉRANT" - Taux de réussite >= 80%
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        if success_rate >= 80:
            badges.append({
                'name': '💪 Persévérant',
                'description': f'{success_rate:.0f}% de réussite',
                'icon': '💪',
                'category': 'performance'
            })
        
        # 11. BADGE "MARATHONIEN" - Plus de 30 tests
        if total_tests >= 30:
            badges.append({
                'name': '🏃 Marathonien',
                'description': f'{total_tests} tests complétés',
                'icon': '🏃',
                'category': 'progression'
            })
        
        # 12. BADGE "DIVERSITÉ" - Tests dans 5+ matières différentes
        subjects_count = results.values('test__subject').distinct().count()
        if subjects_count >= 5:
            badges.append({
                'name': '🌈 Polyvalent',
                'description': f'{subjects_count} matières différentes',
                'icon': '🌈',
                'category': 'diversité'
            })
        
        # 13. BADGE "SPÉCIALISTE" - 10+ tests dans une matière
        top_subject = results.values('test__subject').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        if top_subject and top_subject['count'] >= 10:
            subject_name = top_subject['test__subject'] or 'Général'
            badges.append({
                'name': '🎯 Spécialiste',
                'description': f'{top_subject["count"]} tests en {subject_name}',
                'icon': '🎯',
                'category': 'expertise'
            })
        
        # 14. BADGE "RÉGULIER" - Tests sur 7+ jours différents
        distinct_days = results.values('created_at__date').distinct().count()
        if distinct_days >= 7:
            badges.append({
                'name': '📅 Régulier',
                'description': f'Actif sur {distinct_days} jours',
                'icon': '📅',
                'category': 'assiduité'
            })
        
        # 15. BADGE "CHAMPION" - Moyenne >= 90%
        if avg_score >= 90:
            badges.append({
                'name': '🥇 Champion',
                'description': f'Moyenne exceptionnelle ({avg_score:.1f}%)',
                'icon': '🥇',
                'category': 'performance'
            })
        
        # Mettre à jour le profil
        profile.badges = badges
        profile.save()
        
        # Afficher résumé
        self.stdout.write(f'  ✓ {user.username}:')
        self.stdout.write(f'    Tests: {total_tests}')
        self.stdout.write(f'    Moyenne: {avg_score:.1f}%')
        self.stdout.write(f'    Badges: {len(badges)}')
        
        for badge in badges:
            self.stdout.write(f'      {badge["icon"]} {badge["name"]}')
