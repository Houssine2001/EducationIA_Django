"""
Commande Django pour analyser et mettre à jour les points forts/lacunes des étudiants.
Analyse les résultats de tests et met à jour les profils avec une IA précise.

Usage:
    python manage.py analyze_student_strengths
    python manage.py analyze_student_strengths --student etudiant1
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from collections import defaultdict
from evaluation.models import Result, UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Analyse et met à jour les points forts et lacunes des étudiants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student',
            type=str,
            help='Username d\'un étudiant spécifique à analyser'
        )

    def handle(self, *args, **options):
        student_username = options.get('student')
        
        if student_username:
            try:
                student = User.objects.get(username=student_username)
                students = [student]
                self.stdout.write(f'Analyse de l\'étudiant: {student_username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Étudiant {student_username} introuvable'))
                return
        else:
            # Analyser tous les étudiants (non-staff)
            students = User.objects.filter(is_staff=False, is_superuser=False)
            self.stdout.write(f'Analyse de {students.count()} étudiants...')
        
        for student in students:
            self.analyze_student(student)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Analyse terminée !'))

    def analyze_student(self, student):
        """Analyse approfondie d'un étudiant"""
        self.stdout.write(f'\n📊 Analyse de {student.username}...')
        
        # Récupérer tous les résultats
        results = Result.objects.filter(student=student).select_related('test')
        
        if results.count() == 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Aucun résultat trouvé pour {student.username}'))
            return
        
        # Analyse par matière
        subject_data = defaultdict(lambda: {
            'scores': [],
            'count': 0,
            'average': 0,
            'best': 0,
            'worst': 100,
            'total_points': 0,
            'earned_points': 0
        })
        
        for result in results:
            subject = result.test.subject
            score = result.percentage_score
            
            subject_data[subject]['scores'].append(score)
            subject_data[subject]['count'] += 1
            subject_data[subject]['best'] = max(subject_data[subject]['best'], score)
            subject_data[subject]['worst'] = min(subject_data[subject]['worst'], score)
            subject_data[subject]['total_points'] += result.total_score
            subject_data[subject]['earned_points'] += result.percentage_score
        
        # Calculer moyennes
        for subject, data in subject_data.items():
            data['average'] = sum(data['scores']) / len(data['scores'])
        
        # Identifier points forts (moyenne >= 70%)
        strengths = []
        for subject, data in subject_data.items():
            if data['average'] >= 70:
                if data['average'] >= 90:
                    strengths.append(f"Excellence en {subject} (moyenne {data['average']:.1f}%)")
                elif data['average'] >= 80:
                    strengths.append(f"Très bonne maîtrise de {subject} (moyenne {data['average']:.1f}%)")
                else:
                    strengths.append(f"Bonne compréhension de {subject} (moyenne {data['average']:.1f}%)")
        
        # Compétences générales basées sur la régularité
        total_avg = sum(r.percentage_score for r in results) / results.count()
        if total_avg >= 70:
            strengths.insert(0, f"Excellente performance globale ({total_avg:.1f}%)")
            
        # Identifier si l'étudiant s'améliore
        recent_results = list(results.order_by('-created_at')[:10])
        old_results = list(results.order_by('created_at')[:10])
        
        if len(recent_results) >= 5 and len(old_results) >= 5:
            recent_avg = sum(r.percentage_score for r in recent_results) / len(recent_results)
            old_avg = sum(r.percentage_score for r in old_results) / len(old_results)
            
            if recent_avg > old_avg + 10:
                strengths.append(f"Progression remarquable (+{recent_avg - old_avg:.1f}% récemment)")
            elif recent_avg > old_avg + 5:
                strengths.append(f"Amélioration constante (+{recent_avg - old_avg:.1f}%)")
        
        # Si aucun point fort, ajouter au moins la motivation
        if not strengths:
            strengths.append("Engagement dans les tests")
            strengths.append("Volonté de progresser")
        
        # Identifier lacunes (moyenne < 60%)
        weaknesses = []
        for subject, data in subject_data.items():
            if data['average'] < 60:
                if data['average'] < 40:
                    weaknesses.append(f"Difficulté majeure en {subject} (moyenne {data['average']:.1f}%)")
                elif data['average'] < 50:
                    weaknesses.append(f"Nécessite renforcement en {subject} (moyenne {data['average']:.1f}%)")
                else:
                    weaknesses.append(f"À améliorer en {subject} (moyenne {data['average']:.1f}%)")
        
        # Lacunes basées sur la variabilité
        for subject, data in subject_data.items():
            if len(data['scores']) >= 3:
                variance = max(data['scores']) - min(data['scores'])
                if variance > 30 and data['average'] >= 60:
                    weaknesses.append(f"Irrégularité en {subject} (écart de {variance:.0f}%)")
        
        # Lacunes basées sur le temps (si peu de tests)
        if results.count() < 5:
            weaknesses.append("Manque de pratique (peu de tests effectués)")
        
        # Si régression récente
        if len(recent_results) >= 5 and len(old_results) >= 5:
            recent_avg = sum(r.percentage_score for r in recent_results) / len(recent_results)
            old_avg = sum(r.percentage_score for r in old_results) / len(old_results)
            
            if recent_avg < old_avg - 10:
                weaknesses.append(f"Baisse de performance récente (-{old_avg - recent_avg:.1f}%)")
        
        # Si aucune lacune détectée
        if not weaknesses:
            if total_avg >= 80:
                weaknesses.append("Aucune lacune majeure détectée")
            else:
                weaknesses.append("Continuer à pratiquer régulièrement")
        
        # Mettre à jour le profil
        profile, created = UserProfile.objects.get_or_create(user=student)
        profile.strengths = strengths[:10]  # Max 10 points forts
        profile.weaknesses = weaknesses[:10]  # Max 10 lacunes
        profile.save()
        
        # Afficher le résumé
        self.stdout.write(self.style.SUCCESS(f'  ✓ {student.username} analysé'))
        self.stdout.write(f'    Tests: {results.count()}')
        self.stdout.write(f'    Moyenne globale: {total_avg:.1f}%')
        self.stdout.write(f'    Points forts: {len(strengths)}')
        for strength in strengths[:5]:
            self.stdout.write(self.style.SUCCESS(f'      ✓ {strength}'))
        self.stdout.write(f'    Lacunes: {len(weaknesses)}')
        for weakness in weaknesses[:5]:
            self.stdout.write(self.style.WARNING(f'      ⚠ {weakness}'))
