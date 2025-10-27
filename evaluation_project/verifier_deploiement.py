#!/usr/bin/env python
"""
Script de vérification avant déploiement sur Render
Vérifie que tous les fichiers et configurations sont prêts
"""

import os
import sys
from pathlib import Path

# Couleurs pour le terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def check_file_exists(filepath, required=True):
    """Vérifie si un fichier existe"""
    if os.path.exists(filepath):
        print_success(f"Fichier trouvé: {filepath}")
        return True
    else:
        if required:
            print_error(f"Fichier manquant (REQUIS): {filepath}")
        else:
            print_warning(f"Fichier manquant (optionnel): {filepath}")
        return not required

def check_file_content(filepath, search_strings, required=True):
    """Vérifie si un fichier contient certaines chaînes"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            all_found = True
            for search_string in search_strings:
                if search_string in content:
                    print_success(f"  → Contient: {search_string}")
                else:
                    print_error(f"  → Manque: {search_string}")
                    all_found = False
            return all_found
    except Exception as e:
        print_error(f"Erreur lors de la lecture de {filepath}: {e}")
        return False

def main():
    print_header("🔍 VÉRIFICATION PRÉ-DÉPLOIEMENT RENDER")
    
    all_checks_passed = True
    BASE_DIR = Path(__file__).resolve().parent
    
    # 1. Fichiers de configuration Render
    print_header("1️⃣  FICHIERS DE CONFIGURATION RENDER")
    
    checks = [
        (BASE_DIR / "build.sh", True),
        (BASE_DIR / "render.yaml", False),
        (BASE_DIR / "runtime.txt", False),
        (BASE_DIR / "requirements.txt", True),
        (BASE_DIR / ".gitignore", True),
    ]
    
    for filepath, required in checks:
        if not check_file_exists(filepath, required):
            all_checks_passed = False
    
    # 2. Vérification de requirements.txt
    print_header("2️⃣  DÉPENDANCES PYTHON")
    
    req_file = BASE_DIR / "requirements.txt"
    if req_file.exists():
        required_packages = [
            "Django",
            "gunicorn",
            "whitenoise",
            "djongo",
            "pymongo",
        ]
        if not check_file_content(req_file, required_packages):
            all_checks_passed = False
    else:
        print_error("requirements.txt manquant!")
        all_checks_passed = False
    
    # 3. Vérification de settings.py
    print_header("3️⃣  CONFIGURATION DJANGO (settings.py)")
    
    settings_file = BASE_DIR / "backend" / "settings.py"
    if settings_file.exists():
        required_settings = [
            "os.getenv('SECRET_KEY'",
            "os.getenv('DEBUG'",
            "ALLOWED_HOSTS",
            "whitenoise",
            "MONGODB_URI",
            "STATIC_ROOT",
        ]
        if not check_file_content(settings_file, required_settings):
            print_warning("Certaines configurations pourraient manquer dans settings.py")
    else:
        print_error("backend/settings.py manquant!")
        all_checks_passed = False
    
    # 4. Vérification de .gitignore
    print_header("4️⃣  SÉCURITÉ (.gitignore)")
    
    gitignore_file = BASE_DIR / ".gitignore"
    if gitignore_file.exists():
        critical_ignores = [
            ".env",
            "*.log",
            "__pycache__",
        ]
        if not check_file_content(gitignore_file, critical_ignores):
            print_warning("Assurez-vous que .env est ignoré par Git!")
    else:
        print_warning(".gitignore manquant - créez-en un!")
    
    # 5. Vérification des apps Django
    print_header("5️⃣  STRUCTURE DJANGO")
    
    django_checks = [
        (BASE_DIR / "manage.py", True),
        (BASE_DIR / "backend" / "wsgi.py", True),
        (BASE_DIR / "backend" / "urls.py", True),
    ]
    
    for filepath, required in django_checks:
        if not check_file_exists(filepath, required):
            all_checks_passed = False
    
    # 6. Documentation
    print_header("6️⃣  DOCUMENTATION")
    
    doc_files = [
        "GUIDE_DEPLOIEMENT_RENDER.md",
        "DEPLOIEMENT_RAPIDE.md",
        "CHECKLIST_DEPLOIEMENT.md",
    ]
    
    for doc in doc_files:
        check_file_exists(BASE_DIR / doc, required=False)
    
    # 7. Variables d'environnement
    print_header("7️⃣  VARIABLES D'ENVIRONNEMENT")
    
    print_warning("À configurer manuellement dans Render Dashboard:")
    env_vars = [
        "SECRET_KEY",
        "DEBUG",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "MONGODB_URI",
        "MONGODB_NAME",
    ]
    
    for var in env_vars:
        print(f"  • {var}")
    
    print(f"\n{YELLOW}💡 Utilisez generate_secret_key.py pour générer SECRET_KEY{RESET}")
    
    # 8. Résumé final
    print_header("📊 RÉSUMÉ DE LA VÉRIFICATION")
    
    if all_checks_passed:
        print_success("Tous les fichiers requis sont présents!")
        print_success("Votre projet est prêt pour le déploiement sur Render! 🚀")
        print()
        print(f"{BLUE}Prochaines étapes:{RESET}")
        print("  1. Poussez le code sur Git: git push origin main")
        print("  2. Créez un Web Service sur Render")
        print("  3. Configurez les variables d'environnement")
        print("  4. Lancez le déploiement!")
        print()
        print(f"{BLUE}Consultez: DEPLOIEMENT_RAPIDE.md pour les instructions détaillées{RESET}")
        return 0
    else:
        print_error("Certains fichiers requis sont manquants!")
        print_warning("Corrigez les erreurs ci-dessus avant de déployer.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Vérification interrompue par l'utilisateur.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Erreur inattendue: {e}{RESET}")
        sys.exit(1)
