# ========================================
# Script PowerShell de déploiement Render
# ========================================
# Ce script automatise certaines étapes du déploiement
# ========================================

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "              🚀 PRÉPARATION DU DÉPLOIEMENT RENDER" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

# 1. Vérifier que nous sommes dans le bon dossier
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: manage.py introuvable!" -ForegroundColor Red
    Write-Host "   Assurez-vous d'exécuter ce script depuis le dossier du projet." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Dossier du projet détecté" -ForegroundColor Green
Write-Host ""

# 2. Vérifier Python
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "1️⃣  VÉRIFICATION DE PYTHON" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python installé: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python non trouvé!" -ForegroundColor Red
    Write-Host "   Installez Python depuis https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 3. Vérifier Git
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "2️⃣  VÉRIFICATION DE GIT" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

$gitVersion = git --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Git installé: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Git non trouvé" -ForegroundColor Yellow
    Write-Host "   Installez Git depuis https://git-scm.com/" -ForegroundColor Yellow
}
Write-Host ""

# 4. Exécuter le script de vérification
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "3️⃣  VÉRIFICATION DE LA CONFIGURATION" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

if (Test-Path "verifier_deploiement.py") {
    python verifier_deploiement.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "⚠️  Certaines vérifications ont échoué" -ForegroundColor Yellow
        Write-Host "   Corrigez les erreurs avant de continuer" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
} else {
    Write-Host "⚠️  Script de vérification introuvable" -ForegroundColor Yellow
}
Write-Host ""

# 5. Générer SECRET_KEY
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "4️⃣  GÉNÉRATION DE SECRET_KEY" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

$response = Read-Host "Voulez-vous générer une nouvelle SECRET_KEY? (o/N)"
if ($response -eq "o" -or $response -eq "O") {
    if (Test-Path "generate_secret_key.py") {
        python generate_secret_key.py
    } else {
        Write-Host "⚠️  Script generate_secret_key.py introuvable" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "💡 Copiez cette clé - vous en aurez besoin pour Render!" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour continuer"
}
Write-Host ""

# 6. Statut Git
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "5️⃣  STATUT GIT" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""

if (Test-Path ".git") {
    Write-Host "📁 Repository Git détecté" -ForegroundColor Green
    Write-Host ""
    git status --short
    Write-Host ""
    
    $response = Read-Host "Voulez-vous commiter et pousser les changements? (o/N)"
    if ($response -eq "o" -or $response -eq "O") {
        Write-Host ""
        $commitMessage = Read-Host "Message du commit"
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "Configuration pour déploiement Render"
        }
        
        Write-Host ""
        Write-Host "➡️  git add ." -ForegroundColor Cyan
        git add .
        
        Write-Host "➡️  git commit -m `"$commitMessage`"" -ForegroundColor Cyan
        git commit -m "$commitMessage"
        
        Write-Host "➡️  git push" -ForegroundColor Cyan
        git push
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Code poussé sur Git avec succès!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⚠️  Erreur lors du push Git" -ForegroundColor Yellow
            Write-Host "   Vérifiez votre configuration Git et réessayez" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⚠️  Pas de repository Git détecté" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Voulez-vous initialiser un repository Git? (o/N)"
    if ($response -eq "o" -or $response -eq "O") {
        Write-Host ""
        Write-Host "➡️  git init" -ForegroundColor Cyan
        git init
        
        Write-Host "➡️  git add ." -ForegroundColor Cyan
        git add .
        
        Write-Host "➡️  git commit -m `"Configuration pour déploiement Render`"" -ForegroundColor Cyan
        git commit -m "Configuration pour déploiement Render"
        
        Write-Host ""
        Write-Host "✅ Repository Git initialisé!" -ForegroundColor Green
        Write-Host ""
        Write-Host "💡 N'oubliez pas de:" -ForegroundColor Cyan
        Write-Host "   1. Créer un repository sur GitHub/GitLab" -ForegroundColor Yellow
        Write-Host "   2. Ajouter le remote: git remote add origin <URL>" -ForegroundColor Yellow
        Write-Host "   3. Pousser le code: git push -u origin main" -ForegroundColor Yellow
    }
}
Write-Host ""

# 7. Instructions finales
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "6️⃣  PROCHAINES ÉTAPES" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "📋 Pour déployer sur Render:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Allez sur: https://dashboard.render.com" -ForegroundColor White
Write-Host "   2. Cliquez sur: New + → Web Service" -ForegroundColor White
Write-Host "   3. Connectez votre repository Git" -ForegroundColor White
Write-Host "   4. Configurez le service:" -ForegroundColor White
Write-Host "      - Build Command: ./build.sh" -ForegroundColor Gray
Write-Host "      - Start Command: gunicorn backend.wsgi:application" -ForegroundColor Gray
Write-Host "   5. Ajoutez les variables d'environnement" -ForegroundColor White
Write-Host "   6. Lancez le déploiement!" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation complète: DEPLOIEMENT_RAPIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host "                         ✨ PRÉPARATION TERMINÉE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Bon déploiement! 🚀" -ForegroundColor Green
Write-Host ""
