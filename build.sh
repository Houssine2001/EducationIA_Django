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

# Appliquer les migrations (fake pour MongoDB Atlas existant)
echo "🗄️ Application des migrations..."
# MongoDB Atlas a déjà les données, on "fake" les migrations
python manage.py migrate --fake-initial --noinput || python manage.py migrate --fake --noinput

echo "====================================="
echo "✅ Build terminé avec succès!"
echo "====================================="
