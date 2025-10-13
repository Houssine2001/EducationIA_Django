from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId

# Connexion MongoDB
client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]

# Analyser le set spécifique
specific_set_id = "68ed2c283ed41b6a86837e9b"
print(f"🎯 Analyse du set: {specific_set_id}")

try:
    set_data = db.exercise_sets.find_one({'_id': ObjectId(specific_set_id)})
    
    if set_data:
        print(f"✅ Set trouvé: {set_data.get('title', 'Sans titre')}")
        print(f"Status: {set_data.get('status', 'N/A')}")
        
        # Exercices dans ce set
        exercise_count = db.exercise_generator_exerciseset_exercises.count_documents({
            'exerciseset_id': specific_set_id
        })
        print(f"Exercices dans le set: {exercise_count}")
        
        # Soumissions (différentes méthodes)
        sub_count_objectid = db.student_exercise_submissions.count_documents({
            'exercise_set_id': ObjectId(specific_set_id)
        })
        sub_count_string = db.student_exercise_submissions.count_documents({
            'exercise_set_id': specific_set_id
        })
        print(f"Soumissions (ObjectId): {sub_count_objectid}")
        print(f"Soumissions (String): {sub_count_string}")
        
        # Vérifier quelques soumissions
        submissions = list(db.student_exercise_submissions.find())
        print(f"Total soumissions dans la DB: {len(submissions)}")
        
        if submissions:
            print("Exemple de soumission:")
            sub = submissions[0]
            print(f"  exercise_set_id: {sub.get('exercise_set_id')} (type: {type(sub.get('exercise_set_id'))})")
        
    else:
        print("❌ Set non trouvé")
        
except Exception as e:
    print(f"❌ Erreur: {e}")

client.close()
