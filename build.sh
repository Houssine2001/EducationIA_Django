#!/usr/bin/env bash
# Script de build pour Render
set -o errexit  # Arrêter si une commande échoue

echo "====================================="
echo "🚀 Build EducationIA Django sur Render"
echo "====================================="

# Installer les dépendances Python
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r evaluation_project/requirements.txt

# Aller dans le dossier du projet Django
cd evaluation_project

# Collecter les fichiers statiques
echo "📂 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input --clear

# Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate --noinput

echo "====================================="
echo "✅ Build terminé avec succès!"
echo "====================================="
