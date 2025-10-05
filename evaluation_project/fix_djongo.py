"""
Script pour corriger le bug de djongo 1.3.6 avec Python 3.10+
Ce script modifie le fichier base.py de djongo pour corriger l'erreur NotImplementedError
"""

import os
import sys

# Trouver le chemin de djongo
try:
    import djongo
    djongo_path = os.path.dirname(djongo.__file__)
    base_py_path = os.path.join(djongo_path, 'base.py')
    
    print(f"📁 Fichier djongo trouvé : {base_py_path}")
    
    # Lire le fichier
    with open(base_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la ligne problématique
    old_code = "        if self.connection:"
    new_code = "        if self.connection is not None:"
    
    if old_code in content:
        # Remplacer le code
        content = content.replace(old_code, new_code)
        
        # Sauvegarder
        with open(base_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Correction appliquée avec succès !")
        print(f"   Ligne modifiée : 'if self.connection:' → 'if self.connection is not None:'")
    else:
        print("⚠️  Le code a déjà été corrigé ou la structure a changé.")
        
except Exception as e:
    print(f"❌ Erreur : {e}")
    sys.exit(1)
