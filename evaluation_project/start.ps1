# Script de Demarrage Automatique - EduIA# 🚀 Script de Démarrage Automatique - EduIA

# Ce script demarre MongoDB et le serveur Django automatiquement# Ce script démarre MongoDB et le serveur Django automatiquement



Write-Host "Demarrage de EduIA..." -ForegroundColor CyanWrite-Host "🚀 Démarrage de EduIA..." -ForegroundColor Cyan

Write-Host ""Write-Host ""



# Etape 1 : Verifier et demarrer MongoDB# Étape 1 : Vérifier et démarrer MongoDB

Write-Host "Etape 1/3 : Verification de MongoDB..." -ForegroundColor YellowWrite-Host "📊 Étape 1/3 : Vérification de MongoDB..." -ForegroundColor Yellow

$mongod = Get-Process -Name mongod -ErrorAction SilentlyContinue$mongod = Get-Process -Name mongod -ErrorAction SilentlyContinue



if ($mongod) {if ($mongod) {

    Write-Host "MongoDB est deja en cours d'execution (PID: $($mongod.Id))" -ForegroundColor Green    Write-Host "✅ MongoDB est déjà en cours d'exécution (PID: $($mongod.Id))" -ForegroundColor Green

} else {} else {

    Write-Host "Demarrage de MongoDB..." -ForegroundColor Yellow    Write-Host "⚡ Démarrage de MongoDB..." -ForegroundColor Yellow

    Start-Process mongod -ArgumentList "--dbpath", "C:\data\db" -WindowStyle Minimized    Start-Process mongod -ArgumentList "--dbpath", "C:\data\db" -WindowStyle Minimized

    Start-Sleep -Seconds 3    Start-Sleep -Seconds 3

        

    $mongod = Get-Process -Name mongod -ErrorAction SilentlyContinue    $mongod = Get-Process -Name mongod -ErrorAction SilentlyContinue

    if ($mongod) {    if ($mongod) {

        Write-Host "MongoDB demarre avec succes (PID: $($mongod.Id))" -ForegroundColor Green        Write-Host "✅ MongoDB démarré avec succès (PID: $($mongod.Id))" -ForegroundColor Green

    } else {    } else {

        Write-Host "Erreur : MongoDB n'a pas pu demarrer" -ForegroundColor Red        Write-Host "❌ Erreur : MongoDB n'a pas pu démarrer" -ForegroundColor Red

        Write-Host "Verifiez que le dossier C:\data\db existe" -ForegroundColor Yellow        Write-Host "   Vérifiez que le dossier C:\data\db existe" -ForegroundColor Yellow

        exit 1        exit 1

    }    }

}}



Write-Host ""Write-Host ""



# Etape 2 : Activer l'environnement virtuel# Étape 2 : Activer l'environnement virtuel

Write-Host "Etape 2/3 : Activation de l'environnement virtuel..." -ForegroundColor YellowWrite-Host "🐍 Étape 2/3 : Activation de l'environnement virtuel..." -ForegroundColor Yellow

if (Test-Path "..\venv\Scripts\Activate.ps1") {if (Test-Path "..\venv\Scripts\Activate.ps1") {

    & ..\venv\Scripts\Activate.ps1    & ..\venv\Scripts\Activate.ps1

    Write-Host "Environnement virtuel active" -ForegroundColor Green    Write-Host "✅ Environnement virtuel activé" -ForegroundColor Green

} else {} else {

    Write-Host "Erreur : Environnement virtuel non trouve" -ForegroundColor Red    Write-Host "❌ Erreur : Environnement virtuel non trouvé" -ForegroundColor Red

    exit 1    exit 1

}}



Write-Host ""Write-Host ""



# Etape 3 : Lancer le serveur Django# Étape 3 : Lancer le serveur Django

Write-Host "Etape 3/3 : Demarrage du serveur Django..." -ForegroundColor YellowWrite-Host "🌐 Étape 3/3 : Démarrage du serveur Django..." -ForegroundColor Yellow

Write-Host ""Write-Host ""

Write-Host "=============================================" -ForegroundColor CyanWrite-Host "=============================================" -ForegroundColor Cyan

Write-Host "Serveur pret !" -ForegroundColor GreenWrite-Host "🎉 Serveur prêt !" -ForegroundColor Green

Write-Host ""Write-Host ""

Write-Host "Ouvrez votre navigateur : http://127.0.0.1:8000/" -ForegroundColor YellowWrite-Host "📱 Ouvrez votre navigateur : http://127.0.0.1:8000/" -ForegroundColor Yellow

Write-Host ""Write-Host ""

Write-Host "Comptes de test :" -ForegroundColor CyanWrite-Host "🔑 Comptes de test :" -ForegroundColor Cyan

Write-Host "  etudiant1 / pass123  (Score: 86.7%)" -ForegroundColor WhiteWrite-Host "   • etudiant1 / pass123  (Score: 86.7%)" -ForegroundColor White

Write-Host "  etudiant2 / pass123  (Score: 63.3%)" -ForegroundColor WhiteWrite-Host "   • etudiant2 / pass123  (Score: 63.3%)" -ForegroundColor White

Write-Host "  etudiant3 / pass123  (Score: 96.7%)" -ForegroundColor WhiteWrite-Host "   • etudiant3 / pass123  (Score: 96.7%)" -ForegroundColor White

Write-Host "  prof1 / pass123      (Professeur)" -ForegroundColor WhiteWrite-Host "   • prof1 / pass123      (Professeur)" -ForegroundColor White

Write-Host ""Write-Host ""

Write-Host "Pour arreter : CTRL + C" -ForegroundColor YellowWrite-Host "⏹️  Pour arrêter : CTRL + C" -ForegroundColor Yellow

Write-Host "=============================================" -ForegroundColor CyanWrite-Host "=============================================" -ForegroundColor Cyan

Write-Host ""Write-Host ""



python manage.py runserverpython manage.py runserver

