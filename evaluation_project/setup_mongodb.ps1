# Script PowerShell pour migration vers MongoDB
# Exécution: .\setup_mongodb.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION MONGODB POUR DJANGO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si MongoDB est installé
Write-Host "1. Vérification de MongoDB..." -ForegroundColor Yellow
$mongoCheck = Get-Command mongod -ErrorAction SilentlyContinue

if ($null -eq $mongoCheck) {
    Write-Host "   [X] MongoDB n'est PAS installé" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Téléchargez MongoDB depuis:" -ForegroundColor Cyan
    Write-Host "   https://www.mongodb.com/try/download/community" -ForegroundColor Green
    Write-Host ""
    $continue = Read-Host "   Continuer sans MongoDB ? (o/n)"
    if ($continue -ne "o") {
        exit
    }
} else {
    Write-Host "   [OK] MongoDB installé: " -NoNewline -ForegroundColor Green
    mongod --version | Select-Object -First 1
}

# Vérifier si MongoDB Compass est installé
Write-Host ""
Write-Host "2. MongoDB Compass (optionnel)..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\MongoDB Compass\MongoDBCompass.exe") {
    Write-Host "   [OK] MongoDB Compass installé" -ForegroundColor Green
} else {
    Write-Host "   [!] MongoDB Compass recommandé pour interface graphique" -ForegroundColor Yellow
    Write-Host "   Télécharger: https://www.mongodb.com/try/download/compass" -ForegroundColor Cyan
}

# Installation des dépendances Python
Write-Host ""
Write-Host "3. Installation des packages Python..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements_mongodb.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "   [X] Erreur lors de l'installation" -ForegroundColor Red
    exit 1
}

Write-Host "   [OK] Packages Python installés" -ForegroundColor Green

# Copier le fichier .env
Write-Host ""
Write-Host "4. Configuration de l'environnement..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.mongodb" -Destination ".env"
    Write-Host "   [OK] Fichier .env créé depuis .env.mongodb" -ForegroundColor Green
    Write-Host "   [!] Modifiez .env avec vos credentials MongoDB" -ForegroundColor Yellow
} else {
    Write-Host "   [!] Fichier .env existe déjà, non modifié" -ForegroundColor Yellow
}

# Créer le dossier de backup
Write-Host ""
Write-Host "5. Préparation des backups..." -ForegroundColor Yellow
if (!(Test-Path "backup_sqlite")) {
    New-Item -ItemType Directory -Path "backup_sqlite" | Out-Null
    Write-Host "   [OK] Dossier backup_sqlite créé" -ForegroundColor Green
}

# Afficher les prochaines étapes
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION TERMINÉE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Démarrer MongoDB:" -ForegroundColor Yellow
Write-Host "   net start MongoDB" -ForegroundColor White
Write-Host ""
Write-Host "2. Vérifier la connexion MongoDB:" -ForegroundColor Yellow
Write-Host "   mongosh" -ForegroundColor White
Write-Host ""
Write-Host "3. Exécuter le script de migration:" -ForegroundColor Yellow
Write-Host "   python migrate_to_mongodb.py" -ForegroundColor White
Write-Host ""
Write-Host "4. Modifier backend/settings.py:" -ForegroundColor Yellow
Write-Host "   Remplacer le contenu par backend/settings_mongodb.py" -ForegroundColor White
Write-Host ""
Write-Host "5. Démarrer le serveur Django:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "DOCUMENTATION:" -ForegroundColor Green
Write-Host "   Voir MIGRATION_MONGODB_GUIDE.md" -ForegroundColor White
Write-Host ""
