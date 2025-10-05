"""
Script pour migrer toutes les données de MongoDB vers SQLite
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pymongo import MongoClient
from evaluation.models import Test, Question, UserProfile, Result, Submission
from django.contrib.auth.models import User

# Connexion MongoDB
mongo_client = MongoClient('localhost', 27017)
db = mongo_client['evaluation_db']

print("=" * 70)
print("MIGRATION MONGODB → SQLITE")
print("=" * 70)

# 1. Migrer les UserProfiles
print("\n📊 Migration des UserProfiles...")
profiles_mongo = list(db['user_profiles'].find())
migrated = 0
for prof_data in profiles_mongo:
    try:
        user_id = prof_data.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            print(f"  ⚠️  User {user_id} n'existe pas, skip profile")
            continue
        
        # Créer ou update le profile
        UserProfile.objects.update_or_create(
            user_id=user_id,
            defaults={
                'student_id': prof_data.get('student_id'),
                'level': prof_data.get('level', 1),
                'total_xp': prof_data.get('total_xp', 0),
                'badges': prof_data.get('badges', []),
                'strengths': prof_data.get('strengths', []),
                'weaknesses': prof_data.get('weaknesses', []),
                'ai_recommendations': prof_data.get('ai_recommendations', {}),
                'performance_history': prof_data.get('performance_history', []),
                'skill_progress': prof_data.get('skill_progress', {}),
            }
        )
        migrated += 1
    except Exception as e:
        print(f"  ✗ Erreur profile {prof_data.get('user_id')}: {e}")

print(f"  ✓ {migrated} UserProfiles migrés")

# 2. Migrer les Tests
print("\n📝 Migration des Tests...")
tests_mongo = list(db['tests'].find())
migrated = 0
for test_data in tests_mongo:
    try:
        Test.objects.update_or_create(
            id=test_data.get('id'),
            defaults={
                'title': test_data.get('title'),
                'subject': test_data.get('subject'),
                'duration': test_data.get('duration'),
                'total_points': test_data.get('total_points'),
                'created_by_id': test_data.get('created_by_id'),
                'tags': test_data.get('tags', []),
                'skills_tested': test_data.get('skills_tested', []),
            }
        )
        migrated += 1
    except Exception as e:
        print(f"  ✗ Erreur test {test_data.get('id')}: {e}")

print(f"  ✓ {migrated} Tests migrés")

# 3. Migrer les Questions
print("\n❓ Migration des Questions...")
questions_mongo = list(db['questions'].find())
migrated = 0
for q_data in questions_mongo:
    try:
        Question.objects.update_or_create(
            id=q_data.get('id'),
            defaults={
                'test_id': q_data.get('test_id'),
                'question_type': q_data.get('question_type'),
                'question_text': q_data.get('question_text'),
                'options': q_data.get('options', []),
                'correct_answer': q_data.get('correct_answer'),
                'points': q_data.get('points'),
                'skills': q_data.get('skills', []),
            }
        )
        migrated += 1
    except Exception as e:
        print(f"  ✗ Erreur question {q_data.get('id')}: {e}")

print(f"  ✓ {migrated} Questions migrées")

# 4. Migrer les Submissions
print("\n📤 Migration des Submissions...")
submissions_mongo = list(db['submissions'].find())
migrated = 0
for sub_data in submissions_mongo:
    try:
        Submission.objects.update_or_create(
            id=sub_data.get('id'),
            defaults={
                'test_id': sub_data.get('test_id'),
                'student_id': sub_data.get('student_id'),
                'status': sub_data.get('status'),
                'answers': sub_data.get('answers', {}),
                'started_at': sub_data.get('started_at'),
                'submitted_at': sub_data.get('submitted_at'),
            }
        )
        migrated += 1
    except Exception as e:
        print(f"  ✗ Erreur submission {sub_data.get('id')}: {e}")

print(f"  ✓ {migrated} Submissions migrées")

# 5. Migrer les Results
print("\n📊 Migration des Results...")
results_mongo = list(db['results'].find())
migrated = 0
for res_data in results_mongo:
    try:
        Result.objects.update_or_create(
            id=res_data.get('id'),
            defaults={
                'submission_id': res_data.get('submission_id'),
                'student_id': res_data.get('student_id'),
                'test_id': res_data.get('test_id'),
                'total_score': res_data.get('total_score'),
                'percentage_score': res_data.get('percentage_score'),
                'grade': res_data.get('grade'),
                'skills_breakdown': res_data.get('skills_breakdown', {}),
                'ai_analysis': res_data.get('ai_analysis', {}),
            }
        )
        migrated += 1
    except Exception as e:
        print(f"  ✗ Erreur result {res_data.get('id')}: {e}")

print(f"  ✓ {migrated} Results migrés")

print("\n" + "=" * 70)
print("✅ MIGRATION TERMINÉE!")
print(f"   - Users: {User.objects.count()}")
print(f"   - UserProfiles: {UserProfile.objects.count()}")
print(f"   - Tests: {Test.objects.count()}")
print(f"   - Questions: {Question.objects.count()}")
print(f"   - Submissions: {Submission.objects.count()}")
print(f"   - Results: {Result.objects.count()}")
print("=" * 70)
