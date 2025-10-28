"""
Commande pour régénérer les données de gamification à partir des résultats existants.
Utilise les Results déjà créés pour mettre à jour XP, défis, et StudentTestResult.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from evaluation.models import Result, UserProfile
from evaluation.utils import get_or_create_user_profile_safe
from analytics_dashboard.models import StudentTestResult, Challenge
from analytics_dashboard.services import ChallengeService


class Command(BaseCommand):
    help = 'Régénère les données de gamification à partir des résultats de tests existants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username spécifique à traiter (sinon tous les étudiants)',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        
        self.stdout.write(self.style.WARNING('🔄 RÉGÉNÉRATION DES DONNÉES DE GAMIFICATION'))
        self.stdout.write('=' * 70)
        
        # Filtrer les utilisateurs
        if username:
            users_list = list(User.objects.filter(username=username))
            if not users_list:
                self.stdout.write(self.style.ERROR(f'❌ Utilisateur {username} non trouvé'))
                return
        else:
            # Récupérer tous les utilisateurs et filtrer en Python pour éviter les problèmes Djongo
            all_users = list(User.objects.all())
            users_list = [u for u in all_users if not u.is_staff]
        
        self.stdout.write(f'📊 {len(users_list)} étudiant(s) à traiter\n')
        
        total_xp_added = 0
        total_test_results_created = 0
        total_challenges_updated = 0
        
        for user in users_list:
            self.stdout.write(f'\n👤 Traitement de {user.username}...')
            
            # 1. Récupérer le profil
            profile = get_or_create_user_profile_safe(user)
            initial_xp = profile.total_xp or 0
            
            # 2. Récupérer tous les résultats de tests
            results = Result.objects.filter(student=user).order_by('created_at')
            
            if not results.exists():
                self.stdout.write(f'   ⏭️ Aucun résultat trouvé')
                continue
            
            self.stdout.write(f'   📝 {results.count()} résultat(s) trouvé(s)')
            
            # 3. Supprimer les anciens StudentTestResult pour éviter les doublons
            old_test_results = StudentTestResult.objects.filter(student=user)
            old_count = old_test_results.count()
            if old_count > 0:
                old_test_results.delete()
                self.stdout.write(f'   🗑️  {old_count} ancien(s) StudentTestResult supprimé(s)')
            
            # 4. Traiter chaque résultat
            xp_gained = 0
            for result in results:
                test = result.test
                score = result.percentage_score or 0
                subject = test.subject if test and hasattr(test, 'subject') else 'Général'
                test_name = test.title if test else 'Test'
                
                # Calculer XP
                xp_base = 20
                xp_bonus = int(score / 5)
                xp_for_this_test = xp_base + xp_bonus
                xp_gained += xp_for_this_test
                
                # Créer StudentTestResult
                StudentTestResult.objects.create(
                    student=user,
                    subject=subject,
                    test_name=test_name,
                    score=score,
                    test_id=str(test.pk) if test else None,
                    completed_at=result.created_at
                )
                total_test_results_created += 1
            
            # 5. Mettre à jour le profil avec le nouvel XP
            profile.total_xp = initial_xp + xp_gained
            profile.save()
            total_xp_added += xp_gained
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'   ✅ {results.count()} StudentTestResult créés'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   💫 XP: {initial_xp} → {profile.total_xp} (+{xp_gained})'
                )
            )
            
            # 6. Générer des défis s'il n'en a pas
            active_challenges = Challenge.objects.filter(
                student=user,
                status='ACTIVE',
                expires_at__gte=timezone.now()
            )
            
            if active_challenges.count() == 0:
                try:
                    challenge_service = ChallengeService()
                    new_challenges = challenge_service.generate_daily_challenges(user)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   🎯 {len(new_challenges)} nouveau(x) défi(s) créé(s)'
                        )
                    )
                    active_challenges = Challenge.objects.filter(
                        student=user,
                        status='ACTIVE',
                        expires_at__gte=timezone.now()
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'   ⚠️ Erreur création défis: {e}'
                        )
                    )
            
            # 7. Mettre à jour la progression des défis
            if active_challenges.exists():
                challenge_service = ChallengeService()
                for challenge in active_challenges:
                    challenge_subject = challenge.target_data.get('subject', challenge.subject or '')
                    
                    # Compter les tests complétés depuis le début du défi
                    if challenge_subject:
                        tests_completed = StudentTestResult.objects.filter(
                            student=user,
                            subject__icontains=challenge_subject,
                            completed_at__gte=challenge.created_at
                        ).count()
                    else:
                        tests_completed = StudentTestResult.objects.filter(
                            student=user,
                            completed_at__gte=challenge.created_at
                        ).count()
                    
                    # Calculer score moyen
                    if tests_completed > 0:
                        avg_score = StudentTestResult.objects.filter(
                            student=user,
                            completed_at__gte=challenge.created_at
                        ).aggregate(Avg('score'))['score__avg'] or 0
                    else:
                        avg_score = 0
                    
                    # Mettre à jour
                    old_progress = challenge.current_progress
                    updated_challenge = challenge_service.update_challenge_progress(
                        challenge=challenge,
                        exercises_completed=tests_completed,
                        current_score=avg_score
                    )
                    
                    if updated_challenge.current_progress != old_progress:
                        total_challenges_updated += 1
                        self.stdout.write(
                            f'   📈 Défi "{challenge.title}": {old_progress}% → {updated_challenge.current_progress}%'
                        )
                        
                        if updated_challenge.status == 'COMPLETED':
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'      🎉 COMPLÉTÉ! +{challenge.xp_reward} XP, +{challenge.coins_reward} coins'
                                )
                            )
        
        # Résumé final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ RÉGÉNÉRATION TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'  • Étudiants traités: {len(users_list)}')
        self.stdout.write(f'  • StudentTestResult créés: {total_test_results_created}')
        self.stdout.write(f'  • XP total ajouté: {total_xp_added}')
        self.stdout.write(f'  • Défis mis à jour: {total_challenges_updated}')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                '✨ Les données de gamification ont été régénérées avec succès!'
            )
        )
