#!/usr/bin/env bash
# build.sh - Script de déploiement pour Render
# Exit on error
set -o errexit

echo "🚀 Début du déploiement..."

# Installer les dépendances
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

# Créer le dossier logs s'il n'existe pas
echo "📝 Création du dossier logs..."
mkdir -p logs

echo "✅ Build terminé avec succès!"
