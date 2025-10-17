"""
Middleware pour tracker automatiquement les visites de cours
"""
from django.urls import resolve
from django.utils import timezone
from analytics_dashboard.subject_services import AISubjectAnalyticsService
import time


class SubjectVisitTrackingMiddleware:
    """
    Middleware pour tracker automatiquement les visites de matières
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.service = AISubjectAnalyticsService()
    
    def __call__(self, request):
        # Marquer le début de la requête
        request._start_time = time.time()
        
        response = self.get_response(request)
        
        # Tracker les visites après la réponse
        if request.user.is_authenticated and not request.user.is_staff:
            self._track_visit(request, response)
        
        return response
    
    def _track_visit(self, request, response):
        """Enregistre automatiquement les visites de matières"""
        try:
            # Calculer la durée
            duration = int((time.time() - request._start_time) / 60)  # En minutes
            if duration < 1:
                duration = 1  # Minimum 1 minute
            
            path = request.path
            
            # Tracker les visites de subject_overview
            if '/analytics/subjects/' in path:
                # Si GET parameter subject exists
                subject_name = request.GET.get('subject')
                if subject_name:
                    self.service.record_visit(
                        user=request.user,
                        subject_name=subject_name,
                        duration=duration,
                        pages_viewed=1
                    )
            
            # Tracker aussi si l'URL contient le nom de la matière
            url_name = resolve(request.path_info).url_name
            
            if url_name == 'subject_detail':
                # Extraire le subject_name des kwargs du resolver
                match = resolve(request.path_info)
                if 'subject_name' in match.kwargs:
                    subject_name = match.kwargs['subject_name']
                    self.service.record_visit(
                        user=request.user,
                        subject_name=subject_name,
                        duration=duration,
                        pages_viewed=1
                    )
                    
        except Exception as e:
            # Ne pas bloquer la requête si le tracking échoue
            print(f"Erreur tracking visite: {e}")
            pass
