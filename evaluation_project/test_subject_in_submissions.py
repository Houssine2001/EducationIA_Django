"""
Script pour simuler l'extraction des résultats avec subject réel
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['django_education']

# Chercher les soumissions d'étudiants
submissions = list(db.student_exercise_submissions.find({
    'status': 'completed'
}).limit(5))

print(f"✓ {len(submissions)} soumissions trouvées\n")

for submission in submissions:
    print(f"Soumission ID: {submission.get('_id')}")
    print(f"  Student ID: {submission.get('student_id')}")
    print(f"  Score: {submission.get('score')}%")
    
    # Récupérer l'ExerciseSet
    set_id = submission.get('exercise_set_id')
    if set_id:
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
        if set_data:
            print(f"  ExerciseSet: {set_data.get('title')}")
            
            # Récupérer le vrai subject depuis CourseDocument
            subject = 'Général'
            source_doc_id = set_data.get('source_document_id')
            if source_doc_id:
                try:
                    doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                    if doc_data and doc_data.get('subject'):
                        subject = doc_data.get('subject').capitalize()
                except Exception as e:
                    print(f"  Erreur: {e}")
            
            print(f"  ✅ Subject extrait: '{subject}'")
    print()

client.close()
