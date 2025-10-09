"""
Script de migration automatique SQLite → MongoDB
Exporte toutes les données de SQLite et les importe dans MongoDB
"""
import os
import sys
import django
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation.models import UserProfile, Test, Question, Submission, Result
from django.core import serializers
import sqlite3
from pymongo import MongoClient

class SQLiteToMongoMigration:
    def __init__(self):
        self.sqlite_db = 'db.sqlite3'
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.mongo_db_name = 'django_education'
        
        # Connexion MongoDB
        self.mongo_client = MongoClient(self.mongo_uri)
        self.mongo_db = self.mongo_client[self.mongo_db_name]
        
        print("✅ Connexion MongoDB établie")
    
    def backup_sqlite_data(self):
        """Sauvegarde les données SQLite en JSON"""
        print("\n📦 Sauvegarde des données SQLite...")
        
        backup_dir = 'backup_sqlite'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Liste des modèles à sauvegarder
        models_to_backup = [
            ('users', User),
            ('profiles', UserProfile),
            ('tests', Test),
            ('questions', Question),
            ('submissions', Submission),
            ('results', Result),
        ]
        
        for name, model in models_to_backup:
            data = serializers.serialize('json', model.objects.all())
            filepath = f'{backup_dir}/{name}.json'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            count = model.objects.count()
            print(f"  ✓ {name}: {count} enregistrements sauvegardés")
        
        print(f"\n✅ Sauvegarde terminée dans ./{backup_dir}/")
        return backup_dir
    
    def migrate_users(self):
        """Migrer les utilisateurs"""
        print("\n👥 Migration des utilisateurs...")
        
        collection = self.mongo_db['auth_user']
        collection.delete_many({})  # Nettoyer la collection
        
        users = User.objects.all()
        migrated = 0
        
        for user in users:
            doc = {
                '_id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} utilisateurs migrés")
        return migrated
    
    def migrate_profiles(self):
        """Migrer les profils utilisateurs"""
        print("\n📋 Migration des profils...")
        
        collection = self.mongo_db['evaluation_userprofile']
        collection.delete_many({})
        
        profiles = UserProfile.objects.all()
        migrated = 0
        
        for profile in profiles:
            doc = {
                '_id': profile.id,
                'user_id': profile.user.id,
                'student_id': profile.student_id,
                'date_of_birth': profile.date_of_birth,
                'phone_number': profile.phone_number,
                'class_level': profile.class_level,
                'specialization': profile.specialization,
                'total_tests_taken': profile.total_tests_taken,
                'average_score': profile.average_score,
                'total_study_time': profile.total_study_time,
                'level': profile.level,
                'total_xp': profile.total_xp,
                'badges': profile.badges,
                'strengths': profile.strengths,
                'weaknesses': profile.weaknesses,
                'ai_recommendations': profile.ai_recommendations,
                'learning_style': profile.learning_style if hasattr(profile, 'learning_style') else '',
                'performance_history': profile.performance_history if hasattr(profile, 'performance_history') else [],
                'created_at': profile.created_at if hasattr(profile, 'created_at') else None,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} profils migrés")
        return migrated
    
    def migrate_tests(self):
        """Migrer les tests"""
        print("\n📝 Migration des tests...")
        
        collection = self.mongo_db['evaluation_test']
        collection.delete_many({})
        
        tests = Test.objects.all()
        migrated = 0
        
        for test in tests:
            doc = {
                '_id': test.id,
                'title': test.title,
                'description': test.description or '',
                'subject': test.subject,
                'topic': test.topic if hasattr(test, 'topic') else '',
                'difficulty': test.difficulty if hasattr(test, 'difficulty') else 'medium',
                'duration': test.duration,
                'passing_score': test.passing_score,
                'total_points': test.total_points if hasattr(test, 'total_points') else 100.0,
                'number_of_questions': test.number_of_questions if hasattr(test, 'number_of_questions') else 0,
                'is_timed': test.is_timed if hasattr(test, 'is_timed') else True,
                'allow_review': test.allow_review if hasattr(test, 'allow_review') else True,
                'shuffle_questions': test.shuffle_questions if hasattr(test, 'shuffle_questions') else False,
                'status': test.status if hasattr(test, 'status') else 'published',
                'published_at': test.published_at if hasattr(test, 'published_at') else None,
                'tags': test.tags if hasattr(test, 'tags') else [],
                'skills_tested': test.skills_tested if hasattr(test, 'skills_tested') else [],
                'ai_metadata': test.ai_metadata if hasattr(test, 'ai_metadata') else {},
                'total_attempts': test.total_attempts if hasattr(test, 'total_attempts') else 0,
                'average_score_obtained': test.average_score_obtained if hasattr(test, 'average_score_obtained') else 0.0,
                'average_completion_time': test.average_completion_time if hasattr(test, 'average_completion_time') else 0,
                'created_by_id': test.created_by.id if test.created_by else None,
                'created_at': test.created_at if hasattr(test, 'created_at') else None,
                'updated_at': test.updated_at if hasattr(test, 'updated_at') else None,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} tests migrés")
        return migrated
    
    def migrate_questions(self):
        """Migrer les questions"""
        print("\n❓ Migration des questions...")
        
        collection = self.mongo_db['evaluation_question']
        collection.delete_many({})
        
        questions = Question.objects.all()
        migrated = 0
        
        for question in questions:
            doc = {
                '_id': question.id,
                'test_id': question.test.id if question.test else None,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'points': question.points,
                'difficulty_level': question.difficulty_level,
                'explanation': question.explanation,
                'skills': question.skills,
                'order': question.order,
                'created_at': question.created_at,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} questions migrées")
        return migrated
    
    def migrate_submissions(self):
        """Migrer les soumissions"""
        print("\n📤 Migration des soumissions...")
        
        collection = self.mongo_db['evaluation_submission']
        collection.delete_many({})
        
        submissions = Submission.objects.all()
        migrated = 0
        
        for submission in submissions:
            doc = {
                '_id': submission.id,
                'student_id': submission.student.id,
                'test_id': submission.test.id,
                'answers': submission.answers,
                'status': submission.status,
                'started_at': submission.started_at,
                'submitted_at': submission.submitted_at,
                'time_spent': submission.time_spent,
                'ip_address': submission.ip_address,
                'created_at': submission.created_at,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} soumissions migrées")
        return migrated
    
    def migrate_results(self):
        """Migrer les résultats"""
        print("\n📊 Migration des résultats...")
        
        collection = self.mongo_db['evaluation_result']
        collection.delete_many({})
        
        results = Result.objects.all()
        migrated = 0
        
        for result in results:
            doc = {
                '_id': result.id,
                'submission_id': result.submission.id,
                'student_id': result.student.id,
                'test_id': result.test.id,
                'total_score': result.total_score,
                'percentage_score': result.percentage_score,
                'grade': result.grade or '',
                'mcq_score': result.mcq_score if hasattr(result, 'mcq_score') else 0.0,
                'true_false_score': result.true_false_score if hasattr(result, 'true_false_score') else 0.0,
                'essay_score': result.essay_score if hasattr(result, 'essay_score') else 0.0,
                'skills_breakdown': result.skills_breakdown if hasattr(result, 'skills_breakdown') else {},
                'rank': result.rank if hasattr(result, 'rank') else None,
                'percentile': result.percentile if hasattr(result, 'percentile') else None,
                'compared_to_average': result.compared_to_average if hasattr(result, 'compared_to_average') else 0.0,
                'questions_per_minute': result.questions_per_minute if hasattr(result, 'questions_per_minute') else 0.0,
                'average_time_per_question': result.average_time_per_question if hasattr(result, 'average_time_per_question') else 0.0,
                'time_efficiency': result.time_efficiency if hasattr(result, 'time_efficiency') else 0.0,
                'ai_analysis': result.ai_analysis if hasattr(result, 'ai_analysis') else {},
                'recommendations': result.recommendations if hasattr(result, 'recommendations') else [],
                'study_suggestions': result.study_suggestions if hasattr(result, 'study_suggestions') else [],
                'error_patterns': result.error_patterns if hasattr(result, 'error_patterns') else [],
                'learning_gaps': result.learning_gaps if hasattr(result, 'learning_gaps') else [],
                'performance_chart_data': result.performance_chart_data if hasattr(result, 'performance_chart_data') else {},
                'created_at': result.created_at if hasattr(result, 'created_at') else None,
                'updated_at': result.updated_at if hasattr(result, 'updated_at') else None,
            }
            collection.insert_one(doc)
            migrated += 1
        
        print(f"  ✓ {migrated} résultats migrés")
        return migrated
    
    def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        print("\n🔍 Création des index MongoDB...")
        
        # Index pour les utilisateurs
        self.mongo_db['auth_user'].create_index('username', unique=True)
        self.mongo_db['auth_user'].create_index('email')
        
        # Index pour les profils
        self.mongo_db['evaluation_userprofile'].create_index('user_id', unique=True)
        self.mongo_db['evaluation_userprofile'].create_index('student_id')
        
        # Index pour les tests
        self.mongo_db['evaluation_test'].create_index('created_by_id')
        self.mongo_db['evaluation_test'].create_index('subject')
        self.mongo_db['evaluation_test'].create_index([('is_active', 1), ('start_date', 1)])
        
        # Index pour les questions
        self.mongo_db['evaluation_question'].create_index('test_id')
        
        # Index pour les soumissions
        self.mongo_db['evaluation_submission'].create_index('student_id')
        self.mongo_db['evaluation_submission'].create_index('test_id')
        self.mongo_db['evaluation_submission'].create_index([('student_id', 1), ('test_id', 1)])
        
        # Index pour les résultats
        self.mongo_db['evaluation_result'].create_index('submission_id', unique=True)
        self.mongo_db['evaluation_result'].create_index('student_id')
        self.mongo_db['evaluation_result'].create_index('test_id')
        
        print("  ✓ Index créés avec succès")
    
    def verify_migration(self):
        """Vérifier que la migration s'est bien passée"""
        print("\n✅ Vérification de la migration...")
        
        comparisons = [
            ('Users', User.objects.count(), self.mongo_db['auth_user'].count_documents({})),
            ('Profiles', UserProfile.objects.count(), self.mongo_db['evaluation_userprofile'].count_documents({})),
            ('Tests', Test.objects.count(), self.mongo_db['evaluation_test'].count_documents({})),
            ('Questions', Question.objects.count(), self.mongo_db['evaluation_question'].count_documents({})),
            ('Submissions', Submission.objects.count(), self.mongo_db['evaluation_submission'].count_documents({})),
            ('Results', Result.objects.count(), self.mongo_db['evaluation_result'].count_documents({})),
        ]
        
        all_ok = True
        for name, sqlite_count, mongo_count in comparisons:
            status = "✓" if sqlite_count == mongo_count else "✗"
            print(f"  {status} {name}: SQLite={sqlite_count}, MongoDB={mongo_count}")
            if sqlite_count != mongo_count:
                all_ok = False
        
        if all_ok:
            print("\n🎉 Migration réussie ! Tous les comptages correspondent.")
        else:
            print("\n⚠️ Attention : Certains comptages ne correspondent pas.")
        
        return all_ok
    
    def run_full_migration(self):
        """Exécuter la migration complète"""
        print("=" * 60)
        print("🔄 MIGRATION SQLite → MongoDB")
        print("=" * 60)
        
        # 1. Sauvegarde
        backup_dir = self.backup_sqlite_data()
        
        # 2. Migration des données
        self.migrate_users()
        self.migrate_profiles()
        self.migrate_tests()
        self.migrate_questions()
        self.migrate_submissions()
        self.migrate_results()
        
        # 3. Création des index
        self.create_indexes()
        
        # 4. Vérification
        success = self.verify_migration()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ MIGRATION TERMINÉE AVEC SUCCÈS !")
            print("=" * 60)
            print("\n📝 Prochaines étapes :")
            print("1. Modifier backend/settings.py pour utiliser MongoDB")
            print("2. Redémarrer le serveur Django")
            print("3. Tester l'application")
            print(f"4. Si tout fonctionne, vous pouvez supprimer {backup_dir}/")
        else:
            print("⚠️ MIGRATION TERMINÉE AVEC AVERTISSEMENTS")
            print("=" * 60)
            print(f"\nVérifiez les données dans {backup_dir}/")
        
        return success


def main():
    print("\n⚠️  AVERTISSEMENT ⚠️")
    print("Cette migration va :")
    print("1. Sauvegarder vos données SQLite")
    print("2. Les copier dans MongoDB")
    print("3. Créer les index nécessaires")
    print("\nAssurez-vous que MongoDB est démarré et accessible !")
    
    response = input("\nContinuer ? (oui/non) : ")
    
    if response.lower() not in ['oui', 'yes', 'o', 'y']:
        print("Migration annulée.")
        return
    
    try:
        migrator = SQLiteToMongoMigration()
        migrator.run_full_migration()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration : {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
