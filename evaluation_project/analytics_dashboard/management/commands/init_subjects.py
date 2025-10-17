"""
Commande pour initialiser les matières et chapitres de démonstration
Usage: python manage.py init_subjects
"""
from django.core.management.base import BaseCommand
from analytics_dashboard.subject_models import Subject, Chapter


class Command(BaseCommand):
    help = 'Initialise les matières et chapitres de démonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📚 Initialisation des matières et chapitres...'))
        
        # Nettoyer les données existantes (optionnel)
        if input('Voulez-vous supprimer les matières existantes? (y/n): ').lower() == 'y':
            Subject.objects.all().delete()
            self.stdout.write(self.style.WARNING('🗑️  Matières existantes supprimées'))
        
        # Matière 1: Mathématiques
        math = Subject.objects.create(
            name='Mathématiques',
            code='MATH',
            description='Cours de mathématiques pour tous les niveaux',
            icon='🔢',
            color='#667eea'
        )
        
        math_chapters = [
            ('Algèbre de base', 'EASY', 'Les fondamentaux de l\'algèbre: équations simples, expressions...', 30),
            ('Géométrie euclidienne', 'MEDIUM', 'Triangles, cercles, théorèmes fondamentaux', 45),
            ('Trigonométrie', 'MEDIUM', 'Sinus, cosinus, tangente et applications', 40),
            ('Fonctions linéaires', 'EASY', 'Comprendre et tracer les fonctions du premier degré', 35),
            ('Équations du second degré', 'MEDIUM', 'Résolution par discriminant, forme canonique', 50),
            ('Dérivation', 'HARD', 'Calcul de dérivées, applications aux fonctions', 60),
            ('Intégration', 'HARD', 'Primitives, calcul d\'aires sous les courbes', 60),
        ]
        
        for i, (title, diff, desc, duration) in enumerate(math_chapters, 1):
            Chapter.objects.create(
                subject=math,
                title=title,
                order=i,
                description=desc,
                difficulty=diff,
                duration_minutes=duration,
                content=f"Contenu détaillé du chapitre {i}: {title}\n\n{desc}\n\nCe chapitre nécessite environ {duration} minutes d'étude."
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Mathématiques: {len(math_chapters)} chapitres'))
        
        # Matière 2: Physique
        physics = Subject.objects.create(
            name='Physique',
            code='PHYS',
            description='Physique générale et mécanique',
            icon='⚗️',
            color='#f59e0b'
        )
        
        physics_chapters = [
            ('Cinématique', 'MEDIUM', 'Mouvement, vitesse, accélération', 40),
            ('Dynamique newtonienne', 'MEDIUM', 'Les trois lois de Newton et applications', 45),
            ('Énergie et travail', 'MEDIUM', 'Énergie cinétique, potentielle, conservation', 50),
            ('Électrostatique', 'HARD', 'Charges, champs électriques, loi de Coulomb', 55),
            ('Circuits électriques', 'MEDIUM', 'Lois d\'Ohm, Kirchhoff, analyse de circuits', 45),
            ('Optique géométrique', 'EASY', 'Réflexion, réfraction, lentilles', 35),
        ]
        
        for i, (title, diff, desc, duration) in enumerate(physics_chapters, 1):
            Chapter.objects.create(
                subject=physics,
                title=title,
                order=i,
                description=desc,
                difficulty=diff,
                duration_minutes=duration,
                content=f"Contenu du chapitre: {title}\n\n{desc}\n\nTemps estimé: {duration} min"
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Physique: {len(physics_chapters)} chapitres'))
        
        # Matière 3: Chimie
        chemistry = Subject.objects.create(
            name='Chimie',
            code='CHEM',
            description='Chimie générale et organique',
            icon='🧪',
            color='#10b981'
        )
        
        chemistry_chapters = [
            ('Structure de l\'atome', 'EASY', 'Protons, neutrons, électrons, configuration électronique', 30),
            ('Tableau périodique', 'EASY', 'Organisation des éléments, familles chimiques', 35),
            ('Liaisons chimiques', 'MEDIUM', 'Liaisons ioniques, covalentes, métalliques', 45),
            ('Réactions chimiques', 'MEDIUM', 'Équilibrage, types de réactions', 40),
            ('Stœchiométrie', 'MEDIUM', 'Calculs de quantités en chimie', 50),
            ('Acides et bases', 'MEDIUM', 'pH, réactions acido-basiques', 45),
            ('Chimie organique', 'HARD', 'Hydrocarbures, groupes fonctionnels', 60),
        ]
        
        for i, (title, diff, desc, duration) in enumerate(chemistry_chapters, 1):
            Chapter.objects.create(
                subject=chemistry,
                title=title,
                order=i,
                description=desc,
                difficulty=diff,
                duration_minutes=duration,
                content=f"Contenu: {title}\n\n{desc}"
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Chimie: {len(chemistry_chapters)} chapitres'))
        
        # Matière 4: Biologie
        biology = Subject.objects.create(
            name='Biologie',
            code='BIO',
            description='Sciences de la vie et biologie cellulaire',
            icon='🧬',
            color='#8b5cf6'
        )
        
        biology_chapters = [
            ('La cellule', 'EASY', 'Structure et fonctions de la cellule', 35),
            ('ADN et génétique', 'MEDIUM', 'Structure de l\'ADN, réplication, mutations', 45),
            ('Métabolisme cellulaire', 'HARD', 'Respiration, photosynthèse', 55),
            ('Division cellulaire', 'MEDIUM', 'Mitose et méiose', 40),
            ('Évolution', 'MEDIUM', 'Sélection naturelle, adaptation', 45),
        ]
        
        for i, (title, diff, desc, duration) in enumerate(biology_chapters, 1):
            Chapter.objects.create(
                subject=biology,
                title=title,
                order=i,
                description=desc,
                difficulty=diff,
                duration_minutes=duration,
                content=f"Contenu: {title}\n\n{desc}"
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Biologie: {len(biology_chapters)} chapitres'))
        
        # Statistiques finales
        total_subjects = Subject.objects.count()
        total_chapters = Chapter.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Initialisation terminée!'))
        self.stdout.write(f'  📚 {total_subjects} matières créées')
        self.stdout.write(f'  📖 {total_chapters} chapitres créés')
        self.stdout.write(f'\n💡 Les étudiants peuvent maintenant consulter les matières à:')
        self.stdout.write(f'   👉 /analytics/matieres/')
