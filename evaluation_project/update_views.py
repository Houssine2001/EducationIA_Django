import re

with open('exercise_generator/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer get_object_or_404 par get_mongo_object
patterns = [
    # CourseDocument avec document_pk
    (r'get_object_or_404\(CourseDocument, pk=convert_to_objectid\(document_pk\), teacher=request\.user\)',
     r'get_mongo_object(CourseDocument, document_pk, teacher=request.user)'),
    
    # CourseDocument avec document_id
    (r'get_object_or_404\(CourseDocument, pk=convert_to_objectid\(document_id\), teacher=request\.user\)',
     r'get_mongo_object(CourseDocument, document_id, teacher=request.user)'),
    
    # CourseDocument avec pk (document_reprocess)
    (r'get_object_or_404\(CourseDocument, pk=convert_to_objectid\(pk\), teacher=request\.user\)',
     r'get_mongo_object(CourseDocument, pk, teacher=request.user)'),
    
    # GeneratedExercise
    (r'get_object_or_404\(\s*GeneratedExercise,\s*pk=convert_to_objectid\(pk\),\s*source_document__teacher=request\.user\s*\)',
     r'get_mongo_object(GeneratedExercise, pk, source_document__teacher=request.user)'),
    
    # GeneratedTest
    (r'get_object_or_404\(GeneratedTest, pk=convert_to_objectid\(pk\), teacher=request\.user\)',
     r'get_mongo_object(GeneratedTest, pk, teacher=request.user)'),
    
    # ExerciseSet avec teacher
    (r'get_object_or_404\(ExerciseSet, pk=convert_to_objectid\(set_id\), teacher=request\.user\)',
     r'get_mongo_object(ExerciseSet, set_id, teacher=request.user)'),
    
    # ExerciseSet avec status
    (r"get_object_or_404\(ExerciseSet, pk=convert_to_objectid\(set_id\), status='published'\)",
     r"get_mongo_object(ExerciseSet, set_id, status='published')"),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

with open('exercise_generator/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Toutes les vues mises à jour avec get_mongo_object')
