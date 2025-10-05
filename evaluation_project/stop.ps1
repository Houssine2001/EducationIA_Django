# 🛑 Script d'Arrêt - EduIA
# Ce script arrête proprement MongoDB et le serveur Django

Write-Host "🛑 Arrêt de EduIA..." -ForegroundColor Red
Write-Host ""

# Arrêter MongoDB
Write-Host "📊 Arrêt de MongoDB..." -ForegroundColor Yellow
$mongod = Get-Process -Name mongod -ErrorAction SilentlyContinue

if ($mongod) {
    Stop-Process -Name mongod -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ MongoDB arrêté" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB n'était pas en cours d'exécution" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Arrêt terminé" -ForegroundColor Green
Write-Host ""
