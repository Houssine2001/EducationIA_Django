from django.core.management.base import BaseCommand
from exercise_generator.views import get_mongo_document_simple
from exercise_generator.models import ExerciseSet
from pymongo import MongoClient
from django.conf import settings
from backend.mongodb_utils import get_mongodb_client

class Command(BaseCommand):
    help = 'Tester la vue exercise_set_detail'

    def handle(self, *args, **options):
        # Simuler ce que fait la vue exercise_set_detail
        set_id = '68ed2c283ed41b6a86837e9b'
        
        # Récupérer le set
        exercise_set = get_mongo_document_simple(ExerciseSet, set_id)
        self.stdout.write(f'Set récupéré: {exercise_set.title}')
        
        # Connexion MongoDB
        client = get_mongodb_client()
        db = client[settings.MONGO_DB_NAME]
        
        # Test du comptage des soumissions (avec notre fix)
        submissions_count = db.student_exercise_submissions.count_documents({
            'exercise_set_id': str(exercise_set.pk)
        })
        self.stdout.write(f'Soumissions trouvées: {submissions_count}')
        
        # Test du comptage des exercices
        relations = list(db['exercise_generator_exerciseset_exercises'].find({
            'exerciseset_id': str(exercise_set.pk)
        }))
        self.stdout.write(f'Relations exercices trouvées: {len(relations)}')
        
        # Test de récupération des exercices
        exercise_ids = [rel['generatedexercise_id'] for rel in relations]
        self.stdout.write(f'IDs exercices: {exercise_ids}')
        
        # Avec conversion ObjectId
        from bson.objectid import ObjectId
        object_ids = []
        for eid in exercise_ids:
            try:
                if isinstance(eid, str):
                    object_ids.append(ObjectId(eid))
                else:
                    object_ids.append(eid)
            except:
                continue
        
        exercises_data = list(db.generated_exercises.find({
            '_id': {'$in': object_ids}
        }))
        self.stdout.write(f'Exercices récupérés: {len(exercises_data)}')
        
        client.close()
        self.stdout.write('✅ Test terminé')
