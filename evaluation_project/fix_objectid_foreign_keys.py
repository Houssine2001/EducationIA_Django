"""
Script pour convertir tous les ObjectId dans les ForeignKey en strings
Ceci résout le problème "Field 'id' expected a number but got ObjectId"
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configuration MongoDB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'django_education'

def convert_objectids_to_strings():
    """
    Convertir tous les ObjectId des ForeignKey en strings
    """
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB_NAME]
    
    print("🔄 Conversion des ObjectId en strings pour tous les ForeignKeys...")
    
    # 1. CourseDocuments - teacher_id
    print("\n📄 CourseDocuments - teacher_id...")
    result = db.course_documents.update_many(
        {'teacher_id': {'$type': 'objectId'}},
        [{'$set': {'teacher_id': {'$toString': '$teacher_id'}}}]
    )
    print(f"   ✅ {result.modified_count} documents mis à jour")
    
    # 2. GeneratedExercises - source_document_id et validated_by_id
    print("\n📝 GeneratedExercises...")
    result1 = db.generated_exercises.update_many(
        {'source_document_id': {'$type': 'objectId'}},
        [{'$set': {'source_document_id': {'$toString': '$source_document_id'}}}]
    )
    print(f"   ✅ source_document_id: {result1.modified_count} documents")
    
    result2 = db.generated_exercises.update_many(
        {'validated_by_id': {'$type': 'objectId'}},
        [{'$set': {'validated_by_id': {'$toString': '$validated_by_id'}}}]
    )
    print(f"   ✅ validated_by_id: {result2.modified_count} documents")
    
    # 3. GeneratedTests - source_document_id et teacher_id
    print("\n📋 GeneratedTests...")
    result1 = db.generated_tests.update_many(
        {'source_document_id': {'$type': 'objectId'}},
        [{'$set': {'source_document_id': {'$toString': '$source_document_id'}}}]
    )
    print(f"   ✅ source_document_id: {result1.modified_count} documents")
    
    result2 = db.generated_tests.update_many(
        {'teacher_id': {'$type': 'objectId'}},
        [{'$set': {'teacher_id': {'$toString': '$teacher_id'}}}]
    )
    print(f"   ✅ teacher_id: {result2.modified_count} documents")
    
    # 4. ExerciseSets - teacher_id et source_document_id
    print("\n📦 ExerciseSets...")
    result1 = db.exercise_sets.update_many(
        {'teacher_id': {'$type': 'objectId'}},
        [{'$set': {'teacher_id': {'$toString': '$teacher_id'}}}]
    )
    print(f"   ✅ teacher_id: {result1.modified_count} documents")
    
    result2 = db.exercise_sets.update_many(
        {'source_document_id': {'$type': 'objectId'}},
        [{'$set': {'source_document_id': {'$toString': '$source_document_id'}}}]
    )
    print(f"   ✅ source_document_id: {result2.modified_count} documents")
    
    # 5. StudentExerciseSubmissions - student_id et exercise_set_id
    print("\n👨‍🎓 StudentExerciseSubmissions...")
    result1 = db.student_exercise_submissions.update_many(
        {'student_id': {'$type': 'objectId'}},
        [{'$set': {'student_id': {'$toString': '$student_id'}}}]
    )
    print(f"   ✅ student_id: {result1.modified_count} documents")
    
    result2 = db.student_exercise_submissions.update_many(
        {'exercise_set_id': {'$type': 'objectId'}},
        [{'$set': {'exercise_set_id': {'$toString': '$exercise_set_id'}}}]
    )
    print(f"   ✅ exercise_set_id: {result2.modified_count} documents")
    
    # 6. Tables ManyToMany - exerciseset_exercises et generatedtest_exercises
    print("\n🔗 Tables ManyToMany...")
    result1 = db.exercise_generator_exerciseset_exercises.update_many(
        {'exerciseset_id': {'$type': 'objectId'}},
        [{'$set': {'exerciseset_id': {'$toString': '$exerciseset_id'}}}]
    )
    print(f"   ✅ exerciseset_id: {result1.modified_count} documents")
    
    result2 = db.exercise_generator_exerciseset_exercises.update_many(
        {'generatedexercise_id': {'$type': 'objectId'}},
        [{'$set': {'generatedexercise_id': {'$toString': '$generatedexercise_id'}}}]
    )
    print(f"   ✅ generatedexercise_id: {result2.modified_count} documents")
    
    result3 = db.exercise_generator_generatedtest_exercises.update_many(
        {'generatedtest_id': {'$type': 'objectId'}},
        [{'$set': {'generatedtest_id': {'$toString': '$generatedtest_id'}}}]
    )
    print(f"   ✅ generatedtest_id: {result3.modified_count} documents")
    
    result4 = db.exercise_generator_generatedtest_exercises.update_many(
        {'generatedexercise_id': {'$type': 'objectId'}},
        [{'$set': {'generatedexercise_id': {'$toString': '$generatedexercise_id'}}}]
    )
    print(f"   ✅ generatedexercise_id: {result4.modified_count} documents")
    
    client.close()
    print("\n✅ ✅ ✅ Conversion terminée avec succès!")
    print("\n💡 Les ForeignKey utilisent maintenant des strings au lieu d'ObjectId")
    print("💡 Cela résout l'erreur: Field 'id' expected a number but got ObjectId")


if __name__ == '__main__':
    convert_objectids_to_strings()
