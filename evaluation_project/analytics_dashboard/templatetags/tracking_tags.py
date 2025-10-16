# c:\Users\ferie\OneDrive\Bureau\Ma gestion djangoo\EducationIA_Django\evaluation_project\analytics_dashboard\templatetags\tracking_tags.py

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('analytics_dashboard/tracking_script.html', takes_context=True)
def include_student_tracking(context):
    """Template tag pour inclure le script de tracking automatique"""
    request = context.get('request')
    
    # Vérifier si l'utilisateur est un étudiant
    is_student = (
        request and 
        request.user.is_authenticated and 
        not request.user.is_staff
    )
    
    return {
        'is_student': is_student,
        'user': request.user if request else None,
        'request': request
    }

@register.simple_tag
def tracking_script_basic():
    """Tag simple pour inclure seulement le JavaScript de base"""
    return mark_safe('''
    <script>
    // Script de tracking minimal
    function trackTest(testName, score, subject = 'General') {
        if (window.studentTracker) {
            window.studentTracker.manualTrackTest(testName, score, subject);
        } else {
            fetch('/analytics/api/tracking/test-completion/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify({
                    test_name: testName,
                    score: score,
                    subject: subject
                })
            }).catch(console.error);
        }
    }
    
    function trackVisit(courseName, duration = null) {
        if (window.studentTracker) {
            window.studentTracker.manualTrackVisit(courseName, duration);
        } else {
            fetch('/analytics/api/tracking/course-visit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify({
                    course_name: courseName,
                    duration_minutes: duration
                })
            }).catch(console.error);
        }
    }
    </script>
    ''')

@register.filter
def evolution_trend_icon(trend):
    """Filtre pour afficher l'icône de tendance appropriée"""
    icons = {
        'IMPROVING': '<i class="fas fa-arrow-up text-success"></i>',
        'DECLINING': '<i class="fas fa-arrow-down text-danger"></i>',
        'STABLE': '<i class="fas fa-minus text-warning"></i>',
        'INSUFFICIENT_DATA': '<i class="fas fa-question text-muted"></i>',
        'ERROR': '<i class="fas fa-exclamation text-danger"></i>'
    }
    
    return mark_safe(icons.get(trend, '<i class="fas fa-minus text-muted"></i>'))

@register.filter
def evolution_trend_text(trend):
    """Filtre pour afficher le texte de tendance"""
    texts = {
        'IMPROVING': 'En progression',
        'DECLINING': 'En baisse',
        'STABLE': 'Stable',
        'INSUFFICIENT_DATA': 'Données insuffisantes',
        'ERROR': 'Erreur de calcul'
    }
    
    return texts.get(trend, 'Inconnu')

@register.filter
def evolution_trend_class(trend):
    """Filtre pour la classe CSS de tendance"""
    classes = {
        'IMPROVING': 'badge-success',
        'DECLINING': 'badge-danger',
        'STABLE': 'badge-warning',
        'INSUFFICIENT_DATA': 'badge-secondary',
        'ERROR': 'badge-danger'
    }
    
    return classes.get(trend, 'badge-secondary')

@register.filter
def engagement_level_text(score):
    """Filtre pour convertir le score d'engagement en texte"""
    try:
        score = float(score)
        if score >= 0.8:
            return "Très engagé"
        elif score >= 0.6:
            return "Engagé"
        elif score >= 0.4:
            return "Modérément engagé"
        elif score >= 0.2:
            return "Peu engagé"
        else:
            return "Désengagé"
    except (ValueError, TypeError):
        return "Non défini"

@register.filter
def engagement_level_class(score):
    """Filtre pour la classe CSS du niveau d'engagement"""
    try:
        score = float(score)
        if score >= 0.8:
            return "text-success"
        elif score >= 0.6:
            return "text-info"
        elif score >= 0.4:
            return "text-warning"
        elif score >= 0.2:
            return "text-orange"
        else:
            return "text-danger"
    except (ValueError, TypeError):
        return "text-muted"

@register.simple_tag(takes_context=True)
def evolution_dashboard_link(context, student_id=None):
    """Génère un lien vers le dashboard d'évolution"""
    request = context.get('request')
    
    if student_id and request and request.user.is_staff:
        return f"/analytics/api/tracking/student-evolution/{student_id}/"
    else:
        return "/analytics/api/tracking/student-evolution/"

@register.inclusion_tag('analytics_dashboard/evolution_widget.html', takes_context=True)
def evolution_widget(context, student=None, compact=False):
    """Widget pour afficher l'évolution d'un étudiant"""
    request = context.get('request')
    
    # Déterminer l'étudiant à afficher
    if not student and request:
        student = request.user
    
    return {
        'student': student,
        'compact': compact,
        'request': request,
        'is_admin': request and request.user.is_staff if request else False
    }