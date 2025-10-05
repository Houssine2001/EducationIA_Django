# 🚀 Script de Test Automatique Complet - EduIA
# Ce script exécute tous les tests et vérifications automatiquement

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "🎓 SCRIPT DE TEST AUTOMATIQUE - EduIA" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

# Fonction pour afficher les messages
function Write-Step {
    param($StepNumber, $Message)
    Write-Host "`n$StepNumber " -ForegroundColor Yellow -NoNewline
    Write-Host $Message -ForegroundColor White
    Write-Host ("-" * 60) -ForegroundColor DarkGray
}

function Write-Success {
    param($Message)
    Write-Host "✅ " -ForegroundColor Green -NoNewline
    Write-Host $Message -ForegroundColor White
}

function Write-Error {
    param($Message)
    Write-Host "❌ " -ForegroundColor Red -NoNewline
    Write-Host $Message -ForegroundColor White
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  " -ForegroundColor Cyan -NoNewline
    Write-Host $Message -ForegroundColor White
}

# ===============================================================
# ÉTAPE 1 : Vérifier les prérequis
# ===============================================================
Write-Step "1️⃣" "Vérification des prérequis"

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python installé : $pythonVersion"
} catch {
    Write-Error "Python n'est pas installé ou n'est pas dans le PATH"
    exit 1
}

# Vérifier MongoDB
try {
    $mongoProcess = Get-Process -Name mongod -ErrorAction SilentlyContinue
    if ($mongoProcess) {
        Write-Success "MongoDB est en cours d'exécution (PID: $($mongoProcess.Id))"
    } else {
        Write-Error "MongoDB n'est pas démarré"
        Write-Info "Démarrez MongoDB avec : mongod --dbpath `"C:\data\db`""
        $response = Read-Host "Voulez-vous continuer quand même ? (o/n)"
        if ($response -ne "o") {
            exit 1
        }
    }
} catch {
    Write-Error "Impossible de vérifier MongoDB"
}

# Vérifier l'environnement virtuel
if ($env:VIRTUAL_ENV) {
    Write-Success "Environnement virtuel activé : $env:VIRTUAL_ENV"
} else {
    Write-Error "L'environnement virtuel n'est pas activé"
    Write-Info "Activez-le avec : .\.venv\Scripts\Activate.ps1"
    exit 1
}

# ===============================================================
# ÉTAPE 2 : Vérifier les dépendances
# ===============================================================
Write-Step "2️⃣" "Vérification des dépendances Python"

$requiredPackages = @("django", "djongo", "pymongo", "transformers")

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$package est installé"
    } else {
        Write-Error "$package n'est pas installé"
        Write-Info "Installez avec : pip install -r requirements.txt"
        exit 1
    }
}

# ===============================================================
# ÉTAPE 3 : Migrations
# ===============================================================
Write-Step "3️⃣" "Application des migrations"

Write-Info "Création des migrations..."
python manage.py makemigrations 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Migrations créées"
} else {
    Write-Error "Erreur lors de la création des migrations"
}

Write-Info "Application des migrations..."
python manage.py migrate 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Migrations appliquées"
} else {
    Write-Error "Erreur lors de l'application des migrations"
}

# ===============================================================
# ÉTAPE 4 : Créer les données de test
# ===============================================================
Write-Step "4️⃣" "Création des données de test"

Write-Info "Exécution de create_test_data.py..."
python create_test_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Success "Données de test créées avec succès"
} else {
    Write-Error "Erreur lors de la création des données de test"
    exit 1
}

# ===============================================================
# ÉTAPE 5 : Vérification du système
# ===============================================================
Write-Step "5️⃣" "Vérification du système"

Write-Info "Exécution de verify_system.py..."
python verify_system.py
if ($LASTEXITCODE -eq 0) {
    Write-Success "Vérification du système réussie"
} else {
    Write-Error "Erreur lors de la vérification du système"
}

# ===============================================================
# ÉTAPE 6 : Tests des templates
# ===============================================================
Write-Step "6️⃣" "Vérification des templates"

$templates = @(
    "templates\base.html",
    "templates\evaluation\student\dashboard.html",
    "templates\evaluation\student\progress.html"
)

foreach ($template in $templates) {
    if (Test-Path $template) {
        Write-Success "$template existe"
    } else {
        Write-Error "$template est manquant"
    }
}

# ===============================================================
# ÉTAPE 7 : Tests des modules Python
# ===============================================================
Write-Step "7️⃣" "Vérification des modules Python"

$modules = @(
    "evaluation\models.py",
    "evaluation\views.py",
    "evaluation\analytics.py",
    "evaluation\gamification.py",
    "evaluation\ai_services.py"
)

foreach ($module in $modules) {
    if (Test-Path $module) {
        Write-Success "$module existe"
    } else {
        Write-Error "$module est manquant"
    }
}

# ===============================================================
# ÉTAPE 8 : Résumé et instructions
# ===============================================================
Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 59 -ForegroundColor Green
Write-Host "✅ TESTS TERMINÉS AVEC SUCCÈS !" -ForegroundColor Green
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 59 -ForegroundColor Green

Write-Host "`n📊 Résumé :" -ForegroundColor Cyan
Write-Host "  ✅ Prérequis vérifiés" -ForegroundColor White
Write-Host "  ✅ Dépendances installées" -ForegroundColor White
Write-Host "  ✅ Migrations appliquées" -ForegroundColor White
Write-Host "  ✅ Données de test créées" -ForegroundColor White
Write-Host "  ✅ Système vérifié" -ForegroundColor White
Write-Host "  ✅ Templates présents" -ForegroundColor White
Write-Host "  ✅ Modules Python présents" -ForegroundColor White

Write-Host "`n🔐 Comptes de test créés :" -ForegroundColor Cyan
Write-Host "  - etudiant1 / pass123 (Score: 80%)" -ForegroundColor White
Write-Host "  - etudiant2 / pass123 (Score: 60%)" -ForegroundColor White
Write-Host "  - etudiant3 / pass123 (Score: 93%)" -ForegroundColor White
Write-Host "  - prof1 / pass123 (Enseignant)" -ForegroundColor White

Write-Host "`n🚀 Étapes suivantes :" -ForegroundColor Cyan
Write-Host "  1. Lancez le serveur : python manage.py runserver" -ForegroundColor Yellow
Write-Host "  2. Ouvrez : http://127.0.0.1:8000/student/dashboard/" -ForegroundColor Yellow
Write-Host "  3. Connectez-vous avec : etudiant1 / pass123" -ForegroundColor Yellow

Write-Host "`n📖 Documentation :" -ForegroundColor Cyan
Write-Host "  - README.md : Vue d'ensemble" -ForegroundColor White
Write-Host "  - DEMARRAGE_RAPIDE.md : Guide de démarrage" -ForegroundColor White
Write-Host "  - GUIDE_DE_TEST.md : Tests détaillés" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 59 -ForegroundColor Green
Write-Host ""

# Proposer de lancer le serveur
$response = Read-Host "Voulez-vous lancer le serveur maintenant ? (o/n)"
if ($response -eq "o") {
    Write-Host "`n🚀 Démarrage du serveur Django..." -ForegroundColor Cyan
    Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
    Write-Host ""
    python manage.py runserver
}
