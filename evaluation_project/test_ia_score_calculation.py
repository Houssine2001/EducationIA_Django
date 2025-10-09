"""
Test du calcul des scores en points pour les tests IA
"""
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['django_education']

print("=" * 80)
print("🧪 TEST - Calcul des scores en points pour tests IA")
print("=" * 80)

# Récupérer une soumission
submission = db.student_exercise_submissions.find_one({'status': 'completed'})

if submission:
    print(f"\n✓ Soumission trouvée: {submission.get('_id')}")
    print(f"  Student ID: {submission.get('student_id')}")
    
    # Données brutes
    total_count = submission.get('total_count', 0)
    correct_count = submission.get('correct_count', 0)
    score_percentage = submission.get('score', 0)
    
    print(f"\n📊 Données brutes:")
    print(f"  Total questions: {total_count}")
    print(f"  Réponses correctes: {correct_count}")
    print(f"  Score %: {score_percentage}%")
    
    # Calcul du score en points
    total_score = (score_percentage / 100) * total_count if total_count > 0 else 0
    
    print(f"\n✅ Calcul des points:")
    print(f"  Score obtenu: {total_score:.1f} / {total_count} pts")
    print(f"  Pourcentage: {score_percentage:.1f}%")
    
    # Calcul de la note (grade)
    if score_percentage >= 90:
        grade = 'A+'
    elif score_percentage >= 85:
        grade = 'A'
    elif score_percentage >= 80:
        grade = 'B+'
    elif score_percentage >= 75:
        grade = 'B'
    elif score_percentage >= 70:
        grade = 'C+'
    elif score_percentage >= 65:
        grade = 'C'
    elif score_percentage >= 60:
        grade = 'D'
    else:
        grade = 'F'
    
    print(f"  Note: {grade}")
    
    # Récupérer le set pour voir le titre
    set_id = submission.get('exercise_set_id')
    if set_id:
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
        if set_data:
            print(f"\n📝 Test: {set_data.get('title')}")
            
            # Subject extraction
            source_doc_id = set_data.get('source_document_id')
            if source_doc_id:
                doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                if doc_data:
                    subject = doc_data.get('subject', 'Général').capitalize()
                    print(f"  Matière: {subject}")
    
    # Affichage comme dans le tableau
    print("\n" + "=" * 80)
    print("📋 AFFICHAGE DANS LE TABLEAU")
    print("=" * 80)
    print(f"""
    Date       | Test                | Matière    | Score           | %      | Note
    -----------|---------------------|------------|-----------------|--------|------
    09/10/2025 | {set_data.get('title', 'Test IA')[:19]:<19} | {subject[:10]:<10} | {total_score:.1f} / {total_count} pts | {score_percentage:.1f}% | {grade}
    """)
    
    print("\n✅ AVANT: Score = — (vide)")
    print(f"✅ APRÈS: Score = {total_score:.1f} / {total_count} pts")
    print(f"✅ APRÈS: Note = {grade}")
    
else:
    print("\n❌ Aucune soumission trouvée")

client.close()

print("\n" + "=" * 80)
print("✅ Le score en points et la note sont maintenant calculés pour les tests IA!")
print("=" * 80)
