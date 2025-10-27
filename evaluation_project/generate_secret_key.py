#!/usr/bin/env python
"""
Script pour générer une SECRET_KEY Django sécurisée
Utilisez cette clé dans vos variables d'environnement Render
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    print("=" * 80)
    print("🔐 GÉNÉRATION DE SECRET_KEY DJANGO")
    print("=" * 80)
    print()
    
    secret_key = get_random_secret_key()
    
    print("Votre nouvelle SECRET_KEY:")
    print()
    print(secret_key)
    print()
    print("=" * 80)
    print("📋 INSTRUCTIONS:")
    print("=" * 80)
    print()
    print("1. Copiez la clé ci-dessus")
    print("2. Allez dans Render Dashboard > Votre service > Environment")
    print("3. Ajoutez/Modifiez la variable: SECRET_KEY")
    print("4. Collez cette valeur")
    print("5. Cliquez sur 'Save Changes'")
    print()
    print("⚠️  IMPORTANT: Ne partagez JAMAIS cette clé publiquement!")
    print("⚠️  Ne la commitez JAMAIS dans Git!")
    print()
