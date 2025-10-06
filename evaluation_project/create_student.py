"""
Script pour créer un compte étudiant
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_student(username, email, password, first_name="", last_name=""):
    """
    Crée un compte étudiant
    """
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"❌ L'utilisateur '{username}' existe déjà!")
            return None
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_superuser=False
        )
        
        # Ajouter au groupe "Étudiant" (créer le groupe s'il n'existe pas)
        student_group, created = Group.objects.get_or_create(name='Étudiant')
        user.groups.add(student_group)
        
        print(f"✅ Compte étudiant créé avec succès!")
        print(f"   - Username: {username}")
        print(f"   - Email: {email}")
        print(f"   - Nom: {first_name} {last_name}")
        print(f"   - Groupe: Étudiant")
        
        return user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du compte: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("CRÉATION D'UN COMPTE ÉTUDIANT")
    print("=" * 60)
    
    # Créer quelques comptes étudiants de test
    students = [
        {
            'username': 'etudiant1',
            'email': 'etudiant1@example.com',
            'password': 'password123',
            'first_name': 'Marie',
            'last_name': 'Dupont'
        },
        {
            'username': 'etudiant2',
            'email': 'etudiant2@example.com',
            'password': 'password123',
            'first_name': 'Pierre',
            'last_name': 'Martin'
        },
        {
            'username': 'etudiant3',
            'email': 'etudiant3@example.com',
            'password': 'password123',
            'first_name': 'Sophie',
            'last_name': 'Bernard'
        }
    ]
    
    print("\nCréation de 3 comptes étudiants de test...\n")
    
    for student_data in students:
        create_student(**student_data)
        print()
    
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Total d'étudiants: {User.objects.filter(groups__name='Étudiant').count()}")
    print("\nVous pouvez maintenant vous connecter avec:")
    print("  - Username: etudiant1 / Password: password123")
    print("  - Username: etudiant2 / Password: password123")
    print("  - Username: etudiant3 / Password: password123")
