from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId

class Command(BaseCommand):
    help = 'Diagnostiquer les soumissions pour un set spécifique'

    def handle(self, *args, **options):
        client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]

        # Vérifier le set spécifique
        set_id = '68ed2c283ed41b6a86837e9b'
        self.stdout.write('=== DIAGNOSTIC SET ===')
        self.stdout.write(f'Set ID: {set_id}')

        # Vérifier le set
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
        if set_data:
            self.stdout.write(f'Set trouvé: {set_data.get("title", "Sans titre")}')
            self.stdout.write(f'Status: {set_data.get("status", "N/A")}')
        else:
            self.stdout.write('Set non trouvé!')

        # Vérifier les exercices
        exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({'exerciseset_id': set_id})
        self.stdout.write(f'Exercices dans le set: {exercise_count}')

        # Vérifier les soumissions
        sub_count = db.student_exercise_submissions.count_documents({'exercise_set_id': set_id})
        self.stdout.write(f'Soumissions: {sub_count}')

        # Lister quelques soumissions
        total_subs = db.student_exercise_submissions.count_documents({})
        self.stdout.write(f'Total soumissions dans DB: {total_subs}')
        
        if total_subs > 0:
            subs = list(db.student_exercise_submissions.find().limit(2))
            for i, sub in enumerate(subs):
                self.stdout.write(f'Soumission {i+1} - exercise_set_id: {sub.get("exercise_set_id")} (type: {type(sub.get("exercise_set_id"))})')

        client.close()
