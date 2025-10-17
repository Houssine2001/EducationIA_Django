"""
Commande pour synchroniser la gamification depuis les soumissions MongoDB
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId


class Command(BaseCommand):
    help = 'Synchronise la gamification depuis les soumissions MongoDB'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Synchronisation de la gamification...")
        
        # Connexion MongoDB
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]
        
        # Importer les modèles
        from analytics_dashboard.models import StudentTestResult, Challenge
        from evaluation.models import UserProfile
        from analytics_dashboard.services import ChallengeService
        
        # Récupérer toutes les soumissions complétées
        submissions = db.student_exercise_submissions.find({
            'status': 'completed'
        })
        
        total_processed = 0
        total_xp_added = 0
        
        for submission in submissions:
            try:
                # Récupérer l'étudiant
                student_id = submission.get('student_id')
                if not student_id:
                    continue
                    
                try:
                    student = User.objects.get(id=student_id)
                except User.DoesNotExist:
                    continue
                
                if student.is_staff:
                    continue
                
                # Récupérer le set d'exercices
                set_id = submission.get('exercise_set_id')
                if not set_id:
                    continue
                
                set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
                if not set_data:
                    continue
                
                # Récupérer les infos
                subject = set_data.get('subject', 'General')
                test_name = set_data.get('title', 'Exercice IA')
                score = submission.get('score', 0)
                
                # Vérifier si déjà traité
                test_result, result_created = StudentTestResult.objects.get_or_create(
                    student=student,
                    subject=subject,
                    test_name=test_name,
                    defaults={'score': score}
                )
                
                if result_created:
                    self.stdout.write(f"  ✅ {student.username} - {test_name} ({score}%)")
                    
                    # Récupérer le profil
                    profile, created_profile = UserProfile.objects.get_or_create(
                        user=student,
                        defaults={
                            'role': 'student',
                            'level': 1,
                            'total_xp': 0
                        }
                    )
                    
                    # Calculer et ajouter XP
                    base_xp = int(score / 10)
                    if score >= 80:
                        base_xp += 20
                    elif score >= 60:
                        base_xp += 10
                    
                    old_xp = profile.total_xp
                    profile.total_xp += base_xp
                    new_level = (profile.total_xp // 100) + 1
                    level_up = new_level > profile.level
                    profile.level = new_level
                    profile.updated_at = timezone.now()
                    profile.save()
                    
                    total_xp_added += base_xp
                    total_processed += 1
                    
                    if level_up:
                        self.stdout.write(f"     🎊 LEVEL UP ! Niveau {profile.level}")
                    
                    # Mettre à jour les challenges
                    active_challenges = Challenge.objects.filter(
                        student=student,
                        status='ACTIVE',
                        expires_at__gte=timezone.now()
                    )
                    
                    challenge_service = ChallengeService()
                    
                    for challenge in active_challenges:
                        challenge_subject = challenge.target_data.get('subject', challenge.subject or '') if challenge.target_data else challenge.subject or ''
                        
                        subject_match = (
                            not challenge_subject or
                            challenge_subject.lower() in subject.lower() or
                            subject.lower() in challenge_subject.lower()
                        )
                        
                        if subject_match:
                            if challenge_subject:
                                exercises_completed = StudentTestResult.objects.filter(
                                    student=student,
                                    subject__icontains=challenge_subject,
                                    completed_at__gte=challenge.created_at
                                ).count()
                            else:
                                exercises_completed = StudentTestResult.objects.filter(
                                    student=student,
                                    completed_at__gte=challenge.created_at
                                ).count()
                            
                            updated_challenge = challenge_service.update_challenge_progress(
                                challenge=challenge,
                                exercises_completed=exercises_completed,
                                current_score=score
                            )
                            
                            if updated_challenge.status == 'COMPLETED':
                                self.stdout.write(f"     🎉 Challenge complété: {challenge.title}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur: {e}"))
                continue
        
        client.close()
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Synchronisation terminée !"))
        self.stdout.write(f"   {total_processed} soumissions traitées")
        self.stdout.write(f"   {total_xp_added} XP ajoutés au total")
