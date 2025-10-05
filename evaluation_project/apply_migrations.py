"""
Script pour appliquer les migrations MongoDB en contournant les problèmes de djongo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("🔧 Application des migrations MongoDB avec djongo...\n")

# Liste des migrations à fake (migrations Django problématiques pour djongo)
migrations_to_fake = [
    ('contenttypes', '0002_remove_content_type_name'),
    ('auth', '0002_alter_permission_name_max_length'),
    ('auth', '0003_alter_user_email_max_length'),
    ('auth', '0004_alter_user_username_opts'),
    ('auth', '0005_alter_user_last_login_null'),
    ('auth', '0006_require_contenttypes_0002'),
    ('auth', '0007_alter_validators_add_error_messages'),
    ('auth', '0008_alter_user_username_max_length'),
    ('auth', '0009_alter_user_last_name_max_length'),
    ('auth', '0010_alter_group_name_max_length'),
    ('auth', '0011_update_proxy_permissions'),
    ('auth', '0012_alter_user_first_name_max_length'),
]

print("📋 Étape 1: Fake des migrations Django incompatibles avec djongo...")
for app, migration in migrations_to_fake:
    try:
        call_command('migrate', app, migration, '--fake', verbosity=0)
        print(f"  ✅ Fake: {app}.{migration}")
    except Exception as e:
        print(f"  ⚠️  Skip: {app}.{migration} - {str(e)[:50]}")

print("\n📋 Étape 2: Application des vraies migrations de l'app 'evaluation'...")
try:
    call_command('migrate', 'evaluation', verbosity=2)
    print("  ✅ Migrations 'evaluation' appliquées avec succès")
except Exception as e:
    print(f"  ❌ Erreur: {e}")

print("\n📋 Étape 3: Fake du reste des migrations Django...")
try:
    call_command('migrate', '--fake', verbosity=0)
    print("  ✅ Toutes les migrations marquées comme appliquées")
except Exception as e:
    print(f"  ⚠️  Erreur: {e}")

print("\n✅ TERMINÉ ! Vérification...")

# Vérifier les collections MongoDB
cursor = connection.cursor()
db = cursor.db_conn['evaluation_db']
collections = db.list_collection_names()

print(f"\n📊 Collections MongoDB créées:")
for coll in collections:
    count = db[coll].count_documents({})
    print(f"  - {coll}: {count} documents")

print("\n🎉 Migration terminée ! Vous pouvez maintenant exécuter create_test_data.py")
