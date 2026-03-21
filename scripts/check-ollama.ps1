# Script para verificar que Ollama está corriendo y configurado
# Uso: .\scripts\check-ollama.ps1

Write-Host "🔍 Verificando configuración de Ollama..." -ForegroundColor Cyan

# 1. Verificar si Ollama está instalado
Write-Host "`n1. Verificando instalación de Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama instalado: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://ollama.com/download/windows" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar si Ollama está corriendo
Write-Host "`n2. Verificando servicio de Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Ollama está corriendo en http://localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama no está corriendo" -ForegroundColor Red
    Write-Host "   Ejecuta: ollama serve" -ForegroundColor Yellow
    exit 1
}

# 3. Listar modelos disponibles
Write-Host "`n3. Modelos disponibles:" -ForegroundColor Yellow
$models = ollama list
Write-Host $models

# 4. Verificar modelos recomendados
Write-Host "`n4. Verificando modelos recomendados..." -ForegroundColor Yellow
$recommendedModels = @("qwen2.5-coder:7b", "qwen2.5-coder:1.5b", "nomic-embed-text")

foreach ($model in $recommendedModels) {
    if ($models -match $model) {
        Write-Host "✅ $model está instalado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $model NO está instalado" -ForegroundColor Yellow
        Write-Host "   Ejecuta: ollama pull $model" -ForegroundColor Cyan
    }
}

# 5. Verificar configuración de VSCode
Write-Host "`n5. Verificando configuración de VSCode..." -ForegroundColor Yellow
$vscodeSettingsPath = "$env:APPDATA\Code\User\settings.json"

if (Test-Path $vscodeSettingsPath) {
    $settings = Get-Content $vscodeSettingsPath -Raw | ConvertFrom-Json
    
    if ($settings.'github.copilot.chat.byok.ollamaEndpoint') {
        $endpoint = $settings.'github.copilot.chat.byok.ollamaEndpoint'
        Write-Host "✅ Endpoint configurado: $endpoint" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Endpoint NO configurado en settings.json" -ForegroundColor Yellow
        Write-Host "   Agrega: `"github.copilot.chat.byok.ollamaEndpoint`": `"http://localhost:11434`"" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️  No se encontró settings.json de VSCode" -ForegroundColor Yellow
}

Write-Host "`n✨ Verificación completa!" -ForegroundColor Green
Write-Host "`n📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Abre VSCode" -ForegroundColor White
Write-Host "   2. Abre GitHub Copilot Chat" -ForegroundColor White
Write-Host "   3. Click en selector de modelo → Manage Models → Add Models → Ollama" -ForegroundColor White
Write-Host "   4. Selecciona tu modelo" -ForegroundColor White
