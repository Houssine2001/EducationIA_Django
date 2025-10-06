"""
Commande pour analyser les compétences détaillées des étudiants.

Au lieu de :
- "Point fort: React" ❌

Génère :
- "Excellence en React : Hooks React (useState, useEffect, etc.) (92% - 11/12)" ✅
- "Bonne maîtrise de React : Composants et cycle de vie (78% - 7/9)" ✅
- "À améliorer en Git : Fusion et résolution de conflits (45% - 5/11)" ✅

Usage:
    python manage.py analyze_detailed_skills
    python manage.py analyze_detailed_skills --student username
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evaluation.models import UserProfile, Result
from evaluation.ai_analysis_enhanced import analyze_student_results_detailed


class Command(BaseCommand):
    help = 'Analyse détaillée des compétences granulaires par question'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student',
            type=str,
            help='Analyser un étudiant spécifique (username)'
        )

    def handle(self, *args, **options):
        """Point d'entrée de la commande"""
        student_username = options.get('student')
        
        if student_username:
            try:
                user = User.objects.get(username=student_username)
                self.analyze_student(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Utilisateur {student_username} introuvable'))
        else:
            # Analyser tous les étudiants
            students = User.objects.filter(is_staff=False, is_superuser=False)
            
            self.stdout.write('🔍 Analyse détaillée des compétences...\n')
            
            for user in students:
                self.analyze_student(user)
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Analyse terminée pour {students.count()} étudiant(s)'))

    def analyze_student(self, user):
        """Analyser en détail un étudiant"""
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        # Récupérer tous les résultats
        results = Result.objects.filter(student=user).order_by('-created_at')
        
        if results.count() == 0:
            self.stdout.write(f'  ⚠ {user.username}: Aucun test passé')
            return
        
        # Analyser avec le système amélioré
        analysis = analyze_student_results_detailed(user, results)
        
        # Convertir en format pour UserProfile
        strengths = [s['description'] for s in analysis['strengths']]
        weaknesses = [w['description'] for w in analysis['weaknesses']]
        recommendations = [
            {
                'title': r['title'],
                'description': r['description'],
                'priority': r['priority'],
                'subject': r['subject'],
                'skill': r['skill']
            }
            for r in analysis['recommendations']
        ]
        
        # Mettre à jour le profil
        profile.strengths = strengths
        profile.weaknesses = weaknesses
        profile.ai_recommendations = recommendations
        profile.save()
        
        # Afficher résumé
        self.stdout.write(f'\n📊 Analyse de {user.username}:')
        self.stdout.write(f'  Tests analysés: {results.count()}')
        self.stdout.write(f'  Compétences analysées: {analysis["total_skills_analyzed"]}')
        self.stdout.write(f'  Matières couvertes: {analysis["subjects_covered"]}')
        
        # Points forts (top 5)
        if strengths:
            self.stdout.write(f'\n  ✅ Points forts: {len(strengths)}')
            for strength in analysis['strengths'][:5]:
                level_icon = '🌟' if strength['level'] == 'excellence' else '✨'
                self.stdout.write(f'    {level_icon} {strength["subject"]} : {strength["skill"]} ({strength["percentage"]:.0f}%)')
        
        # Lacunes (top 5)
        if weaknesses:
            self.stdout.write(f'\n  ⚠️  Lacunes: {len(weaknesses)}')
            for weakness in analysis['weaknesses'][:5]:
                severity_icon = '🔴' if weakness['severity'] == 'high' else '🟡'
                self.stdout.write(f'    {severity_icon} {weakness["subject"]} : {weakness["skill"]} ({weakness["percentage"]:.0f}%)')
        
        # Recommandations (top 3)
        if recommendations:
            self.stdout.write(f'\n  💡 Recommandations: {len(recommendations)}')
            for rec in analysis['recommendations'][:3]:
                priority_icon = '🔥' if rec['priority'] == 'high' else '📌'
                self.stdout.write(f'    {priority_icon} {rec["title"]}')
