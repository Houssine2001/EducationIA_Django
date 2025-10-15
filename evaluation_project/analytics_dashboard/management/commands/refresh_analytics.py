from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_dashboard.services import AnalyticsService


class Command(BaseCommand):
    help = 'Actualise les analytics pour tous les étudiants ou un étudiant spécifique'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--student-id',
            type=int,
            help='ID de l\'étudiant spécifique à actualiser'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Actualiser tous les étudiants'
        )
    
    def handle(self, *args, **options):
        service = AnalyticsService()
        
        if options['student_id']:
            try:
                student = User.objects.get(id=options['student_id'])
                analytics = service.update_student_analytics(student)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Analytics actualisés pour {student.get_full_name()}'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Étudiant {options["student_id"]} introuvable')
                )
        else:
            # Actualiser tous les étudiants
            students = User.objects.filter(groups__name='Students')
            updated_count = 0
            
            for student in students:
                try:
                    service.update_student_analytics(student)
                    updated_count += 1
                    self.stdout.write(f'✓ {student.get_full_name()}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Erreur pour {student.get_full_name()}: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Analytics actualisés pour {updated_count} étudiants')
            )