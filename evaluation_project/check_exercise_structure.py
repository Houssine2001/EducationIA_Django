"""
Vérifier la structure des exercices dans MongoDB
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

client = MongoClient('localhost', 27017)
db = client['django_education']

# Récupérer un exercice de type MCQ
mcq = db.generated_exercises.find_one({'exercise_type': 'mcq'})
if mcq:
    print("=== EXERCICE MCQ ===")
    print(f"ID: {mcq['_id']}")
    print(f"Question: {mcq.get('question_text', 'N/A')}")
    print(f"Type: {mcq.get('exercise_type')}")
    print(f"\nOptions Data Structure:")
    print(json.dumps(mcq.get('options_data', {}), indent=2, ensure_ascii=False))
else:
    print("❌ Aucun exercice MCQ trouvé")

print("\n" + "="*50 + "\n")

# Récupérer un exercice True/False
tf = db.generated_exercises.find_one({'exercise_type': 'true_false'})
if tf:
    print("=== EXERCICE TRUE/FALSE ===")
    print(f"ID: {tf['_id']}")
    print(f"Question: {tf.get('question_text', 'N/A')}")
    print(f"Type: {tf.get('exercise_type')}")
    print(f"\nOptions Data Structure:")
    print(json.dumps(tf.get('options_data', {}), indent=2, ensure_ascii=False))
else:
    print("❌ Aucun exercice True/False trouvé")

client.close()
