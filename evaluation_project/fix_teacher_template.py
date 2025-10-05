"""
Script pour ajouter le namespace evaluation: aux URLs du template teacher/dashboard.html
"""

import re

# Lire le fichier
file_path = r'C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project\templates\evaluation\teacher\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer {% url 'XXX' %} par {% url 'evaluation:XXX' %}
# Sauf si le namespace existe déjà
pattern = r"{% url '([^':]+)'"
replacement = r"{% url 'evaluation:\1'"

# Ne remplacer que si le namespace n'est pas déjà présent
content = re.sub(r"{% url '(?!evaluation:)([^']+)'", replacement, content)

# Écrire le fichier
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Fichier {file_path} mis à jour avec les namespaces evaluation:")
