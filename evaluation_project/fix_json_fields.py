"""Script pour remplacer djongo_models.JSONField par models.JSONField"""
import os

file_path = r'C:\Users\Lenovo\Desktop\DjangoEducation\evaluation_project\evaluation\models.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer djongo_models.JSONField par models.JSONField
content = content.replace('djongo_models.JSONField', 'models.JSONField')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Tous les djongo_models.JSONField remplacés par models.JSONField")
