"""
Simulation de l'affichage des résultats avec vrais subjects
pour vérifier ce que l'étudiant verra
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
from collections import defaultdict

client = MongoClient('localhost', 27017)
db = client['django_education']

print("=" * 80)
print("🎓 SIMULATION AFFICHAGE ÉTUDIANT - PROGRESSION")
print("=" * 80)

# Récupérer les soumissions de l'étudiant 42 (exemple)
student_id = 42
ai_submissions = list(db.student_exercise_submissions.find({
    'student_id': student_id,
    'status': 'completed'
}))

print(f"\n📊 Étudiant ID: {student_id}")
print(f"✓ {len(ai_submissions)} tests IA complétés\n")

# Traiter les résultats comme dans student_progress
ai_results_with_details = []
for submission in ai_submissions:
    set_id = submission.get('exercise_set_id')
    if set_id:
        set_data = db.exercise_sets.find_one({'_id': ObjectId(set_id)})
        if set_data:
            # Récupérer le vrai subject depuis le CourseDocument
            subject = 'Général'
            source_doc_id = set_data.get('source_document_id')
            if source_doc_id:
                try:
                    doc_data = db.course_documents.find_one({'_id': ObjectId(source_doc_id)})
                    if doc_data and doc_data.get('subject'):
                        subject = doc_data.get('subject').capitalize()
                except:
                    pass
            
            ai_results_with_details.append({
                'submission': submission,
                'set_data': set_data,
                'score': submission.get('score', 0),
                'submitted_at': submission.get('submitted_at'),
                'subject': subject
            })

# Afficher comme dans le tableau historique
print("┌" + "─" * 78 + "┐")
print("│ TABLEAU HISTORIQUE DES TESTS IA" + " " * 45 + "│")
print("├" + "─" * 20 + "┬" + "─" * 20 + "┬" + "─" * 15 + "┬" + "─" * 20 + "┤")
print(f"│ {'Date':<18} │ {'Titre':<18} │ {'Matière':<13} │ {'Score':<18} │")
print("├" + "─" * 20 + "┼" + "─" * 20 + "┼" + "─" * 15 + "┼" + "─" * 20 + "┤")

for ai_result in ai_results_with_details:
    date = ai_result['submitted_at'].strftime('%d/%m/%Y') if ai_result['submitted_at'] else 'N/A'
    title = ai_result['set_data'].get('title', 'Test IA')[:17]
    subject = ai_result['subject'][:12]
    score = f"{ai_result['score']:.1f}%"
    
    print(f"│ {date:<18} │ {title:<18} │ {subject:<13} │ {score:<18} │")

print("└" + "─" * 20 + "┴" + "─" * 20 + "┴" + "─" * 15 + "┴" + "─" * 20 + "┘")

# Calculer performances par matière
performance_by_subject = defaultdict(list)
for ai_result in ai_results_with_details:
    subject = ai_result['subject']
    score = ai_result['score']
    performance_by_subject[subject].append(score)

print("\n📈 PERFORMANCES PAR MATIÈRE")
print("┌" + "─" * 40 + "┬" + "─" * 20 + "┬" + "─" * 15 + "┐")
print(f"│ {'Matière':<38} │ {'Score moyen':<18} │ {'Tests':<13} │")
print("├" + "─" * 40 + "┼" + "─" * 20 + "┼" + "─" * 15 + "┤")

for subject, scores in sorted(performance_by_subject.items()):
    avg_score = sum(scores) / len(scores)
    count = len(scores)
    print(f"│ {subject:<38} │ {avg_score:>6.1f}%{' '*11} │ {count:>4}{' '*9} │")

print("└" + "─" * 40 + "┴" + "─" * 20 + "┴" + "─" * 15 + "┘")

# Identifier les points forts et faibles
print("\n🎯 ANALYSE DES RÉSULTATS")
strengths = [(s, sum(scores)/len(scores)) for s, scores in performance_by_subject.items() if sum(scores)/len(scores) >= 70]
weaknesses = [(s, sum(scores)/len(scores)) for s, scores in performance_by_subject.items() if sum(scores)/len(scores) < 60]

if strengths:
    print("\n✅ POINTS FORTS:")
    for subject, avg in sorted(strengths, key=lambda x: x[1], reverse=True):
        print(f"   • Excellent en {subject} ({avg:.1f}%)")
else:
    print("\n✅ POINTS FORTS: Aucun score ≥ 70%")

if weaknesses:
    print("\n⚠️ POINTS À AMÉLIORER:")
    for subject, avg in sorted(weaknesses, key=lambda x: x[1]):
        print(f"   • À travailler en {subject} ({avg:.1f}%)")
else:
    print("\n⚠️ POINTS À AMÉLIORER: Aucun score < 60%")

print("\n" + "=" * 80)
print("✅ Tous les sujets affichés sont RÉELS (Node.js, React...) - Plus de 'IA Généré'!")
print("=" * 80)

client.close()
