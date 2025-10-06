# Script de démarrage rapide pour le générateur d'exercices IA
# Windows PowerShell

Write-Host "🚀 Démarrage du Générateur d'Exercices IA" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# 1. Vérifier si PyPDF2 est installé
Write-Host "📦 Vérification des dépendances..." -ForegroundColor Yellow
try {
    python -c "import PyPDF2" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PyPDF2 est installé" -ForegroundColor Green
    } else {
        throw "PyPDF2 non installé"
    }
} catch {
    Write-Host "⚠️  PyPDF2 n'est pas installé. Installation en cours..." -ForegroundColor Yellow
    pip install PyPDF2
    Write-Host "✅ PyPDF2 installé avec succès" -ForegroundColor Green
}

Write-Host ""

# 2. Créer les migrations
Write-Host "🗄️  Création des tables en base de données..." -ForegroundColor Yellow
python manage.py makemigrations exercise_generator
python manage.py migrate exercise_generator

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Base de données créée avec succès" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de la création de la base de données" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Vérifier si un superuser existe
Write-Host "👤 Vérification du compte administrateur..." -ForegroundColor Yellow
$userCount = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).count())" 2>$null

if ($userCount -eq "0") {
    Write-Host "⚠️  Aucun compte administrateur trouvé" -ForegroundColor Yellow
    Write-Host "📝 Création d'un compte administrateur..." -ForegroundColor Yellow
    python manage.py createsuperuser
} else {
    Write-Host "✅ Compte administrateur existant" -ForegroundColor Green
}

Write-Host ""

# 4. Informations de démarrage
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Installation terminée !" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Accès au générateur :" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/generator/" -ForegroundColor White
Write-Host ""
Write-Host "📍 Génération rapide :" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/generator/quick-generate/" -ForegroundColor White
Write-Host ""
Write-Host "📍 Interface admin :" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation :" -ForegroundColor Cyan
Write-Host "   exercise_generator/README.md" -ForegroundColor White
Write-Host "   exercise_generator/QUICKSTART.md" -ForegroundColor White
Write-Host ""

# 5. Démarrer le serveur
Write-Host "🚀 Démarrage du serveur Django..." -ForegroundColor Green
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver
