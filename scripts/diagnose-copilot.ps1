# Script de diagnóstico para GitHub Copilot + Ollama
# Uso: .\scripts\diagnose-copilot.ps1

Write-Host "🔍 Diagnóstico de GitHub Copilot + Ollama" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# 1. Verificar VSCode
Write-Host "`n1️⃣  Verificando VSCode..." -ForegroundColor Yellow
$vscodeCommand = Get-Command code -ErrorAction SilentlyContinue
if ($vscodeCommand) {
    $vscodeVersion = code --version 2>&1 | Select-Object -First 1
    Write-Host "✅ VSCode instalado: $vscodeVersion" -ForegroundColor Green
    
    # Verificar si es versión suficiente (1.85.0+)
    $versionNumber = [version]$vscodeVersion
    $minVersion = [version]"1.85.0"
    
    if ($versionNumber -ge $minVersion) {
        Write-Host "✅ Versión compatible con BYOK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Versión antigua. Actualiza a 1.85.0+" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ VSCode no encontrado en PATH" -ForegroundColor Red
}

# 2. Verificar extensiones de Copilot
Write-Host "`n2️⃣  Verificando extensiones de GitHub Copilot..." -ForegroundColor Yellow
$extensionsOutput = code --list-extensions --show-versions 2>&1

$copilotExtensions = @{
    "GitHub.copilot" = "GitHub Copilot (principal)"
    "GitHub.copilot-chat" = "GitHub Copilot Chat"
}

foreach ($ext in $copilotExtensions.Keys) {
    $found = $extensionsOutput | Select-String -Pattern $ext
    if ($found) {
        Write-Host "✅ $($copilotExtensions[$ext]): $found" -ForegroundColor Green
    } else {
        Write-Host "❌ $($copilotExtensions[$ext]) NO instalado" -ForegroundColor Red
        Write-Host "   Instala desde: https://marketplace.visualstudio.com/items?itemName=$ext" -ForegroundColor Cyan
    }
}

# 3. Verificar Ollama
Write-Host "`n3️⃣  Verificando Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama instalado: $ollamaVersion" -ForegroundColor Green
    
    # Verificar si está corriendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 3 -ErrorAction Stop
        Write-Host "✅ Ollama corriendo en http://localhost:11434" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Ollama instalado pero NO está corriendo" -ForegroundColor Yellow
        Write-Host "   Ejecuta: ollama serve" -ForegroundColor Cyan
    }
    
    # Listar modelos
    Write-Host "`n   Modelos instalados:" -ForegroundColor Cyan
    $models = ollama list 2>&1
    Write-Host "   $models" -ForegroundColor White
    
} catch {
    Write-Host "❌ Ollama NO instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://ollama.com/download/windows" -ForegroundColor Cyan
}

# 4. Verificar configuración de VSCode
Write-Host "`n4️⃣  Verificando configuración de VSCode..." -ForegroundColor Yellow

# Intentar leer settings.json de VSCode
$possiblePaths = @(
    "$env:APPDATA\Code\User\settings.json",
    "$env:APPDATA\Code - Insiders\User\settings.json",
    "$HOME\.vscode\settings.json"
)

$settingsFound = $false
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "✅ Encontrado settings.json: $path" -ForegroundColor Green
        $settingsFound = $true
        
        try {
            $settings = Get-Content $path -Raw | ConvertFrom-Json
            
            # Verificar configuración de Ollama
            if ($settings.'github.copilot.chat.byok.ollamaEndpoint') {
                $endpoint = $settings.'github.copilot.chat.byok.ollamaEndpoint'
                Write-Host "✅ Ollama endpoint configurado: $endpoint" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Ollama endpoint NO configurado" -ForegroundColor Yellow
                Write-Host "   Agrega en settings.json:" -ForegroundColor Cyan
                Write-Host '   "github.copilot.chat.byok.ollamaEndpoint": "http://localhost:11434"' -ForegroundColor White
            }
            
            # Verificar si Copilot está habilitado
            if ($settings.'github.copilot.enable') {
                Write-Host "✅ GitHub Copilot habilitado" -ForegroundColor Green
            } else {
                Write-Host "⚠️  GitHub Copilot podría estar deshabilitado" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "⚠️  Error al leer settings.json (puede tener comentarios)" -ForegroundColor Yellow
        }
        break
    }
}

if (-not $settingsFound) {
    Write-Host "⚠️  No se encontró settings.json de VSCode" -ForegroundColor Yellow
}

# 5. Verificar conectividad de red
Write-Host "`n5️⃣  Verificando conectividad..." -ForegroundColor Yellow
try {
    $githubTest = Test-Connection github.com -Count 1 -Quiet
    if ($githubTest) {
        Write-Host "✅ Conexión a GitHub OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No se puede conectar a GitHub" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error verificando conexión" -ForegroundColor Yellow
}

# Resumen y recomendaciones
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "📋 RESUMEN Y RECOMENDACIONES" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

Write-Host "`n🔧 Si 'Add Models' está desactivado, verifica:" -ForegroundColor Yellow
Write-Host "   1. ¿Estás logueado en GitHub Copilot?" -ForegroundColor White
Write-Host "      → Ctrl+Shift+P → 'GitHub Copilot: Sign In'" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. ¿Tienes una suscripción activa?" -ForegroundColor White
Write-Host "      → Verifica en: https://github.com/settings/copilot" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. ¿Tu plan soporta BYOK (Bring Your Own Key)?" -ForegroundColor White
Write-Host "      → Puede requerir Copilot Business/Enterprise" -ForegroundColor Cyan
Write-Host ""
Write-Host "   4. ¿Extensiones actualizadas?" -ForegroundColor White
Write-Host "      → Ctrl+Shift+P → 'Extensions: Check for Extension Updates'" -ForegroundColor Cyan
Write-Host ""
Write-Host "   5. ¿Ollama corriendo?" -ForegroundColor White
Write-Host "      → Ejecuta: ollama serve" -ForegroundColor Cyan

Write-Host "`n✨ Diagnóstico completo!" -ForegroundColor Green
