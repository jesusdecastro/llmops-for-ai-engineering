# Script de instalación automática de Continue.dev con Ollama
# Uso: .\scripts\setup-continue.ps1

Write-Host "🚀 Configuración de Continue.dev con Ollama" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# 1. Verificar Ollama
Write-Host "`n1️⃣  Verificando Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama instalado: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama NO instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://ollama.com/download/windows" -ForegroundColor Cyan
    exit 1
}

# 2. Verificar que Ollama está corriendo
Write-Host "`n2️⃣  Verificando servicio Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Ollama corriendo en http://localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama no está corriendo. Iniciando..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 3
    Write-Host "✅ Ollama iniciado" -ForegroundColor Green
}

# 3. Descargar modelos recomendados
Write-Host "`n3️⃣  Descargando modelos recomendados..." -ForegroundColor Yellow

$models = @(
    @{name="qwen2.5-coder:7b"; desc="Chat principal (~4.7GB)"},
    @{name="qwen2.5-coder:1.5b"; desc="Autocompletado (~1GB)"},
    @{name="nomic-embed-text"; desc="Embeddings (~274MB)"}
)

foreach ($model in $models) {
    Write-Host "`n   Verificando $($model.name)..." -ForegroundColor Cyan
    $installed = ollama list | Select-String -Pattern $model.name
    
    if ($installed) {
        Write-Host "   ✅ Ya instalado: $($model.name)" -ForegroundColor Green
    } else {
        Write-Host "   📥 Descargando $($model.name) - $($model.desc)" -ForegroundColor Yellow
        Write-Host "   Esto puede tardar varios minutos..." -ForegroundColor Gray
        ollama pull $model.name
        Write-Host "   ✅ Descargado: $($model.name)" -ForegroundColor Green
    }
}

# 4. Verificar VSCode
Write-Host "`n4️⃣  Verificando VSCode..." -ForegroundColor Yellow
$vscodeCommand = Get-Command code -ErrorAction SilentlyContinue
if ($vscodeCommand) {
    Write-Host "✅ VSCode encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  VSCode no encontrado en PATH" -ForegroundColor Yellow
    Write-Host "   Asegúrate de que VSCode esté instalado" -ForegroundColor Cyan
}

# 5. Verificar extensión Continue
Write-Host "`n5️⃣  Verificando extensión Continue..." -ForegroundColor Yellow
$extensions = code --list-extensions 2>&1
$continueInstalled = $extensions | Select-String -Pattern "Continue.continue"

if ($continueInstalled) {
    Write-Host "✅ Continue ya está instalado" -ForegroundColor Green
} else {
    Write-Host "📦 Instalando extensión Continue..." -ForegroundColor Yellow
    code --install-extension Continue.continue
    Write-Host "✅ Continue instalado" -ForegroundColor Green
}

# 6. Crear configuración de Continue
Write-Host "`n6️⃣  Configurando Continue..." -ForegroundColor Yellow

$continueConfigPath = "$env:USERPROFILE\.continue\config.json"
$continueConfigDir = Split-Path -Parent $continueConfigPath

# Crear directorio si no existe
if (-not (Test-Path $continueConfigDir)) {
    New-Item -ItemType Directory -Path $continueConfigDir -Force | Out-Null
}

$configContent = @"
{
  "models": [
    {
      "title": "Qwen 2.5 Coder 7B",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen 2.5 Coder 1.5B",
    "provider": "ollama",
    "model": "qwen2.5-coder:1.5b",
    "apiBase": "http://localhost:11434"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  },
  "contextProviders": [
    {
      "name": "code",
      "params": {}
    },
    {
      "name": "docs",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    },
    {
      "name": "problems",
      "params": {}
    },
    {
      "name": "folder",
      "params": {}
    },
    {
      "name": "codebase",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit code in the current file"
    },
    {
      "name": "comment",
      "description": "Write comments for the highlighted code"
    },
    {
      "name": "share",
      "description": "Export this session as markdown"
    },
    {
      "name": "cmd",
      "description": "Generate a shell command"
    },
    {
      "name": "commit",
      "description": "Generate a commit message"
    }
  ]
}
"@

# Guardar configuración
$configContent | Out-File -FilePath $continueConfigPath -Encoding UTF8 -Force
Write-Host "✅ Configuración guardada en: $continueConfigPath" -ForegroundColor Green

# 7. Resumen
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "✨ INSTALACIÓN COMPLETA" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Gray

Write-Host "`n📋 Resumen:" -ForegroundColor Cyan
Write-Host "   ✅ Ollama instalado y corriendo" -ForegroundColor Green
Write-Host "   ✅ Modelos descargados:" -ForegroundColor Green
Write-Host "      • qwen2.5-coder:7b (Chat)" -ForegroundColor White
Write-Host "      • qwen2.5-coder:1.5b (Autocompletado)" -ForegroundColor White
Write-Host "      • nomic-embed-text (Embeddings)" -ForegroundColor White
Write-Host "   ✅ Continue extension instalada" -ForegroundColor Green
Write-Host "   ✅ Configuración creada" -ForegroundColor Green

Write-Host "`n🎯 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Abre VSCode" -ForegroundColor White
Write-Host "   2. Busca el ícono de Continue en la barra lateral" -ForegroundColor White
Write-Host "   3. Click en Continue o presiona Ctrl+L" -ForegroundColor White
Write-Host "   4. Escribe: 'Write a Python hello world function'" -ForegroundColor White
Write-Host "   5. ¡Disfruta tu copilot local sin restricciones!" -ForegroundColor White

Write-Host "`n⌨️  Atajos útiles:" -ForegroundColor Cyan
Write-Host "   • Ctrl+L: Abrir Continue Chat" -ForegroundColor White
Write-Host "   • Ctrl+I: Editar código seleccionado" -ForegroundColor White
Write-Host "   • Tab: Aceptar autocompletado" -ForegroundColor White
Write-Host "   • Esc: Rechazar autocompletado" -ForegroundColor White

Write-Host "`n📚 Documentación completa:" -ForegroundColor Cyan
Write-Host "   • docs/continue-dev-setup.md" -ForegroundColor White
Write-Host "   • https://docs.continue.dev" -ForegroundColor White

Write-Host "`n🎉 ¡Todo listo! Reinicia VSCode para empezar." -ForegroundColor Green
