# Configuración de Ollama con VSCode GitHub Copilot

Guía paso a paso para integrar modelos locales de Ollama con GitHub Copilot en VSCode.

## 📋 Requisitos Previos

- VSCode instalado
- GitHub Copilot extension instalada y activa
- Windows 10/11
- 16GB RAM mínimo

## 🚀 Instalación

### Paso 1: Instalar Ollama

1. Descargar Ollama para Windows: https://ollama.com/download/windows
2. Ejecutar el instalador
3. Verificar instalación:
   ```powershell
   ollama --version
   ```

### Paso 2: Descargar Modelos Recomendados

```powershell
# Modelo principal para chat/debugging (7B - ~4.7GB)
ollama pull qwen2.5-coder:7b

# Modelo rápido para autocompletado (1.5B - ~1GB)
ollama pull qwen2.5-coder:1.5b

# Embeddings para búsqueda en codebase (~274MB)
ollama pull nomic-embed-text
```

**Tiempo estimado de descarga:** 10-20 minutos dependiendo de tu conexión.

### Paso 3: Verificar que Ollama está Corriendo

```powershell
# Listar modelos instalados
ollama list

# Probar un modelo
ollama run qwen2.5-coder:7b "Write a hello world in Python"
```

## ⚙️ Configuración de VSCode

### Opción A: Configuración Manual

1. **Abrir settings.json:**
   - Presiona `Ctrl + Shift + P`
   - Escribe: `Preferences: Open User Settings (JSON)`
   - Presiona Enter

2. **Agregar configuración:**
   ```json
   {
     "github.copilot.chat.byok.ollamaEndpoint": "http://localhost:11434"
   }
   ```

3. **Guardar el archivo** (`Ctrl + S`)

### Opción B: Configuración desde UI

1. Presiona `Ctrl + ,` (abre Settings)
2. Busca: `copilot ollama`
3. En "Github > Copilot > Chat > Byok: Ollama Endpoint"
4. Ingresa: `http://localhost:11434`

## 🎯 Agregar Modelos en Copilot

1. **Abrir GitHub Copilot Chat** (ícono en barra lateral izquierda)
2. **Click en el selector de modelo** (parte superior del chat)
3. **Click en "Manage Models..."**
4. **Click en "Add Models"**
5. **Seleccionar "Ollama"**
6. Deberías ver tus modelos disponibles:
   - `qwen2.5-coder:7b`
   - `qwen2.5-coder:1.5b`
7. **Seleccionar el modelo** que quieres usar

## 🧪 Probar la Integración

1. En Copilot Chat, escribe:
   ```
   Write a Python function to calculate the factorial of a number
   ```

2. El modelo local debería responder (puede tardar 2-5 segundos en la primera respuesta)

## ⚠️ Problemas Conocidos

### Problema 1: Modelos Desaparecen Después de Recargar

**Síntoma:** Después de `Developer: Reload Window`, los modelos Ollama no aparecen en el selector.

**Workaround:**
1. `Ctrl + Shift + P`
2. `Developer: Reload Window`
3. Volver a agregar modelos: Manage Models → Add Models → Ollama

**Nota:** Este es un bug conocido en VSCode Copilot. Se espera que se solucione en futuras versiones.

### Problema 2: "Cannot connect to Ollama"

**Solución:**
```powershell
# Verificar que Ollama está corriendo
ollama serve

# En otra terminal, verificar endpoint
curl http://localhost:11434
```

### Problema 3: Modelo muy lento

**Causas comunes:**
- Modelo demasiado grande para tu hardware
- Otros programas consumiendo RAM

**Solución:**
- Usar modelo más pequeño: `qwen2.5-coder:1.5b`
- Cerrar aplicaciones que consumen RAM
- Verificar uso de RAM: `Task Manager → Performance → Memory`

## 🔧 Script de Verificación

Ejecuta el script de verificación para diagnosticar problemas:

```powershell
.\scripts\check-ollama.ps1
```

Este script verifica:
- ✅ Ollama instalado
- ✅ Servicio corriendo
- ✅ Modelos descargados
- ✅ Configuración de VSCode

## 📊 Rendimiento Esperado

Con tu hardware (Intel i7-1255U, 16GB RAM):

| Modelo | Tokens/seg | Latencia | RAM Usada |
|--------|------------|----------|-----------|
| qwen2.5-coder:1.5b | 40-60 | 1-2 seg | 2-3 GB |
| qwen2.5-coder:7b | 15-25 | 2-4 seg | 8-10 GB |

**Nota:** Primera respuesta siempre es más lenta (carga del modelo).

## 🎯 Uso Recomendado

### Para Chat/Debugging
- Usar: `qwen2.5-coder:7b`
- Mejor para: Explicaciones, refactoring, debugging

### Para Autocompletado Rápido
- Usar: `qwen2.5-coder:1.5b`
- Mejor para: Completar líneas, sugerencias inline

## 🔄 Actualizar Modelos

```powershell
# Ver modelos instalados
ollama list

# Actualizar un modelo
ollama pull qwen2.5-coder:7b

# Eliminar modelo antiguo (si es necesario)
ollama rm qwen2.5-coder:7b
```

## 📚 Recursos Adicionales

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qwen2.5-Coder Model Card](https://ollama.com/library/qwen2.5-coder)
- [VSCode Copilot Docs](https://code.visualstudio.com/docs/copilot/overview)

## 🆘 Soporte

Si encuentras problemas:
1. Ejecuta `.\scripts\check-ollama.ps1`
2. Revisa la sección "Problemas Conocidos"
3. Verifica logs de Ollama: `ollama logs`
