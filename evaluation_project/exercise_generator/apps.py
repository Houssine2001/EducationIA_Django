from django.apps import AppConfig


class ExerciseGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exercise_generator'
    verbose_name = 'Générateur d\'Exercices IA'
    
    def ready(self):
        """Enregistrer les signals pour fix MongoDB ObjectId"""
        from django.db.models.signals import post_save
        from .models import CourseDocument, GeneratedExercise, GeneratedTest
        from bson.objectid import ObjectId
        import pymongo
        
        def fix_objectid_to_int(sender, instance, created, **kwargs):
            """Signal pour convertir ObjectId en int après sauvegarde"""
            if created:  # Seulement pour les nouvelles instances
                try:
                    # Accéder directement à MongoDB pour corriger l'ID
                    client = pymongo.MongoClient('localhost', 27017)
                    db = client['django_education']
                    collection_name = instance._meta.db_table
                    collection = db[collection_name]
                    
                    # Récupérer le document qui vient d'être créé
                    doc = collection.find_one({'_id': {'$exists': True}}, sort=[('_id', -1)])
                    
                    if doc and isinstance(doc['_id'], ObjectId):
                        # Convertir ObjectId en int
                        id_value = int(str(doc['_id'])[-8:], 16)
                        
                        # Mettre à jour avec le champ id
                        collection.update_one(
                            {'_id': doc['_id']},
                            {'$set': {'id': id_value}}
                        )
                except Exception as e:
                    print(f"⚠️  Erreur fix ObjectId: {e}")
        
        # Connecter le signal à tous les modèles concernés
        post_save.connect(fix_objectid_to_int, sender=CourseDocument)
        post_save.connect(fix_objectid_to_int, sender=GeneratedExercise)
        post_save.connect(fix_objectid_to_int, sender=GeneratedTest)
