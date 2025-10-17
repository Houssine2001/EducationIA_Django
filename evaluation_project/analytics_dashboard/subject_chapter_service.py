"""
Service pour gérer les matières, chapitres et prédictions
"""
from django.utils import timezone
from datetime import timedelta
from .subject_models import Subject, Chapter, ChapterVisit, StudentSubjectProgress
from analytics_dashboard.models import PerformanceTrend
import statistics


class SubjectChapterService:
    """Service pour gérer les matières et chapitres"""
    
    def get_all_subjects(self):
        """Récupère toutes les matières avec leurs stats"""
        return Subject.objects.all()
    
    def get_subject_with_chapters(self, subject_id):
        """Récupère une matière avec tous ses chapitres"""
        try:
            # Convertir l'ID en ObjectId si c'est une string
            from bson import ObjectId
            if isinstance(subject_id, str):
                subject_id = ObjectId(subject_id)
            
            subject = Subject.objects.get(_id=subject_id)
            # Utiliser Chapter.objects.filter au lieu de subject.chapters
            chapters = Chapter.objects.filter(subject=subject).order_by('order')
            return subject, list(chapters)
        except Subject.DoesNotExist:
            return None, []
    
    def get_student_progress(self, student, subject):
        """Récupère ou crée la progression d'un étudiant"""
        progress, created = StudentSubjectProgress.objects.get_or_create(
            student=student,
            subject=subject,
            defaults={
                'total_visits': 0,
                'chapters_visited': 0,
                'total_time_minutes': 0
            }
        )
        return progress
    
    def record_chapter_visit(self, student, chapter, duration_seconds=0, completed=False):
        """Enregistre une visite de chapitre"""
        # Créer la visite
        visit = ChapterVisit.objects.create(
            student=student,
            chapter=chapter,
            duration_seconds=duration_seconds,
            completed=completed
        )
        
        # Mettre à jour la progression
        progress = self.get_student_progress(student, chapter.subject)
        progress.total_visits += 1
        progress.total_time_minutes += duration_seconds // 60
        
        # Compter les chapitres visités uniques
        visited_chapters = ChapterVisit.objects.filter(
            student=student,
            chapter__subject=chapter.subject
        ).values('chapter').distinct().count()
        progress.chapters_visited = visited_chapters
        
        # Compter les chapitres complétés
        completed_chapters = ChapterVisit.objects.filter(
            student=student,
            chapter__subject=chapter.subject,
            completed=True
        ).values('chapter').distinct().count()
        progress.chapters_completed = completed_chapters
        
        # Calculer la consistance (visites régulières)
        progress.consistency_score = self._calculate_consistency(student, chapter.subject)
        
        # Mettre à jour la prédiction
        self._update_test_scores(progress, student, chapter.subject)
        progress.update_prediction()
        progress.save()
        
        return visit
    
    def _calculate_consistency(self, student, subject):
        """Calcule le score de consistance des visites"""
        recent_visits = ChapterVisit.objects.filter(
            student=student,
            chapter__subject=subject,
            visited_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('visited_at')
        
        if recent_visits.count() < 2:
            return 0.5
        
        # Calculer l'écart entre visites
        visit_dates = [v.visited_at for v in recent_visits]
        gaps = []
        for i in range(1, len(visit_dates)):
            gap = (visit_dates[i] - visit_dates[i-1]).days
            gaps.append(gap)
        
        if not gaps:
            return 0.5
        
        # Plus les écarts sont réguliers, meilleur le score
        avg_gap = statistics.mean(gaps)
        if avg_gap == 0:
            return 1.0
        
        std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
        consistency = max(0, 1 - (std_gap / max(avg_gap, 1)))
        
        return min(consistency, 1.0)
    
    def _update_test_scores(self, progress, student, subject):
        """Met à jour les scores de tests"""
        # Récupérer les tests de cette matière
        tests = PerformanceTrend.objects.filter(
            student=student,
            subject=subject.name
        )
        
        if tests.exists():
            progress.tests_taken = tests.count()
            
            scores = [t.score for t in tests]
            progress.average_test_score = statistics.mean(scores)
            progress.best_score = max(scores)
            
            # Compter les tests passés (>= 60%)
            progress.tests_passed = tests.filter(score__gte=60).count()
    
    def get_student_chapter_status(self, student, subject):
        """Récupère le statut de chaque chapitre pour un étudiant"""
        chapters = Chapter.objects.filter(subject=subject).order_by('order')
        chapter_status = []
        
        for chapter in chapters:
            # Vérifier si visité
            visits = list(ChapterVisit.objects.filter(
                student=student,
                chapter=chapter
            ))
            
            is_visited = len(visits) > 0
            # Compter manuellement les visites complétées (bug Djongo avec .filter(boolean=True))
            is_completed = any(v.completed for v in visits)
            visit_count = len(visits)
            total_time = sum(v.duration_seconds for v in visits)
            
            chapter_status.append({
                'chapter': chapter,
                'is_visited': is_visited,
                'is_completed': is_completed,
                'visit_count': visit_count,
                'total_time_minutes': total_time // 60,
                'progress_percentage': 100 if is_completed else (50 if is_visited else 0)
            })
        
        return chapter_status
    
    def get_subject_overview_for_student(self, student):
        """Vue d'ensemble des matières pour un étudiant"""
        subjects = Subject.objects.all()
        overview = []
        
        for subject in subjects:
            progress = self.get_student_progress(student, subject)
            
            total_chapters = Chapter.objects.filter(subject=subject).count()
            completion_rate = progress.calculate_completion_rate()
            
            overview.append({
                'subject': subject,
                'progress': progress,
                'total_chapters': total_chapters,
                'completion_rate': completion_rate,
                'chapters_status': {
                    'visited': progress.chapters_visited,
                    'completed': progress.chapters_completed,
                    'remaining': total_chapters - progress.chapters_visited
                }
            })
        
        return overview
    
    def generate_recommendations(self, student, subject):
        """Génère des recommandations personnalisées"""
        progress = self.get_student_progress(student, subject)
        recommendations = []
        
        # Recommandation 1: Chapitres non visités
        visited_chapter_ids = ChapterVisit.objects.filter(student=student).values_list('chapter___id', flat=True)
        unvisited_chapters = Chapter.objects.filter(subject=subject).exclude(
            _id__in=list(visited_chapter_ids)
        )[:3]
        
        if unvisited_chapters:
            recommendations.append({
                'type': 'CHAPTER',
                'priority': 'HIGH',
                'title': 'Chapitres à découvrir',
                'description': f'Vous n\'avez pas encore visité {unvisited_chapters.count()} chapitres',
                'chapters': list(unvisited_chapters),
                'icon': '📖'
            })
        
        # Recommandation 2: Améliorer les tests
        if progress.average_test_score < 60:
            recommendations.append({
                'type': 'TEST',
                'priority': 'CRITICAL',
                'title': 'Renforcer les connaissances',
                'description': f'Votre moyenne ({progress.average_test_score:.1f}%) peut être améliorée',
                'action': 'Révisez les chapitres et passez plus de tests',
                'icon': '📝'
            })
        
        # Recommandation 3: Régularité
        if progress.consistency_score < 0.5:
            recommendations.append({
                'type': 'ENGAGEMENT',
                'priority': 'MEDIUM',
                'title': 'Soyez plus régulier',
                'description': 'Essayez de visiter les chapitres régulièrement',
                'action': 'Planifiez des sessions d\'étude régulières',
                'icon': '📅'
            })
        
        # Recommandation 4: Compléter les chapitres
        incomplete_rate = (progress.chapters_visited - progress.chapters_completed) / max(progress.chapters_visited, 1)
        if incomplete_rate > 0.5:
            recommendations.append({
                'type': 'COMPLETION',
                'priority': 'MEDIUM',
                'title': 'Terminez vos chapitres',
                'description': f'{progress.chapters_visited - progress.chapters_completed} chapitres commencés mais non terminés',
                'action': 'Complétez les chapitres déjà commencés',
                'icon': '✅'
            })
        
        return recommendations


class PredictionReportService:
    """Service pour générer des rapports de prédiction"""
    
    def generate_detailed_report(self, student, subject):
        """Génère un rapport détaillé de prédiction"""
        service = SubjectChapterService()
        progress = service.get_student_progress(student, subject)
        
        # Facteurs de prédiction détaillés
        visit_engagement = progress.calculate_visit_engagement()
        test_engagement = progress.calculate_test_engagement()
        
        report = {
            'student': student,
            'subject': subject,
            'prediction': {
                'success_rate': progress.predicted_success_rate,
                'confidence': progress.confidence_level,
                'risk_level': progress.risk_level,
                'risk_color': self._get_risk_color(progress.risk_level)
            },
            'engagement': {
                'overall': progress.engagement_score * 100,
                'visits': visit_engagement * 100,
                'tests': test_engagement * 100,
                'consistency': progress.consistency_score * 100
            },
            'metrics': {
                'chapters': {
                    'total': Chapter.objects.filter(subject=subject).count(),
                    'visited': progress.chapters_visited,
                    'completed': progress.chapters_completed,
                    'completion_rate': progress.calculate_completion_rate()
                },
                'tests': {
                    'taken': progress.tests_taken,
                    'passed': progress.tests_passed,
                    'average_score': progress.average_test_score,
                    'best_score': progress.best_score,
                    'success_rate': (progress.tests_passed / max(progress.tests_taken, 1)) * 100
                },
                'time': {
                    'total_minutes': progress.total_time_minutes,
                    'total_hours': progress.total_time_minutes / 60,
                    'average_per_visit': progress.total_time_minutes / max(progress.total_visits, 1)
                }
            },
            'recommendations': service.generate_recommendations(student, subject),
            'last_activity': progress.last_activity
        }
        
        return report
    
    def _get_risk_color(self, risk_level):
        """Couleur selon le niveau de risque"""
        colors = {
            'LOW': '#4caf50',  # Vert
            'MEDIUM': '#ff9800',  # Orange
            'HIGH': '#f44336',  # Rouge
            'CRITICAL': '#9c27b0'  # Violet
        }
        return colors.get(risk_level, '#999')
