# Configuración de Continue.dev con Ollama

Continue.dev es una alternativa completa a GitHub Copilot que funciona con modelos locales de Ollama, sin restricciones corporativas.

## 🎯 ¿Por qué Continue.dev?

- ✅ **Independiente de GitHub Copilot** - No afectado por políticas corporativas
- ✅ **Agent Mode completo** - Tool calling, multi-step reasoning
- ✅ **Gratis y open source** - Sin suscripciones
- ✅ **Mejor integración con Ollama** - Diseñado específicamente para modelos locales
- ✅ **Autocompletado inline** - Como Copilot pero con tus modelos
- ✅ **Chat contextual** - Entiende tu codebase completo
- ✅ **Edición de código** - Puede modificar archivos directamente

## 🚀 Instalación (5 minutos)

### Paso 1: Instalar Extensión

1. Abrir VSCode
2. `Ctrl + Shift + X` (Extensiones)
3. Buscar: **"Continue"**
4. Click en **"Install"** en la extensión de Continue (by Continue)

### Paso 2: Instalar Ollama y Modelos

```powershell
# Si no tienes Ollama instalado
# Descargar de: https://ollama.com/download/windows

# Descargar modelos recomendados
ollama pull qwen2.5-coder:7b        # Chat principal (~4.7GB)
ollama pull qwen2.5-coder:1.5b      # Autocompletado rápido (~1GB)
ollama pull nomic-embed-text        # Embeddings (~274MB)
```

### Paso 3: Configurar Continue

1. Después de instalar, Continue abrirá automáticamente su panel
2. Click en el ícono de **engranaje** (⚙️) en la parte inferior del panel Continue
3. Se abrirá el archivo `config.json`
4. Reemplaza todo el contenido con esta configuración:

```json
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
```

5. Guardar el archivo (`Ctrl + S`)

## 🎮 Uso de Continue

### Chat (Como Copilot Chat)

1. Click en el ícono de Continue en la barra lateral (o `Ctrl + L`)
2. Escribe tu pregunta o solicitud
3. El modelo local responderá

**Ejemplos:**
```
Explica esta función
Refactoriza este código para usar async/await
Encuentra bugs en este archivo
Escribe tests para esta clase
```

### Autocompletado Inline (Como Copilot)

- Simplemente empieza a escribir código
- Continue sugerirá completaciones automáticamente
- Presiona `Tab` para aceptar
- Presiona `Esc` para rechazar

### Editar Código Directamente

1. Selecciona código en el editor
2. `Ctrl + I` (o `Cmd + I` en Mac)
3. Escribe qué quieres cambiar
4. Continue editará el código directamente

**Ejemplo:**
```
Seleccionar función → Ctrl + I → "Add error handling"
```

### Comandos Slash

En el chat de Continue, puedes usar comandos especiales:

- `/edit` - Editar código seleccionado
- `/comment` - Agregar comentarios al código
- `/cmd` - Generar comando de terminal
- `/commit` - Generar mensaje de commit
- `/explain` - Explicar código seleccionado

### Context Providers

Continue puede acceder a diferentes contextos:

- `@code` - Código específico
- `@docs` - Documentación
- `@terminal` - Output del terminal
- `@problems` - Errores y warnings
- `@folder` - Archivos en carpeta
- `@codebase` - Todo el codebase

**Ejemplo:**
```
@terminal Explica este error
@codebase ¿Dónde se define la función authenticate?
```

## ⚙️ Configuración Avanzada

### Múltiples Modelos

Puedes configurar diferentes modelos para diferentes tareas:

```json
{
  "models": [
    {
      "title": "Qwen 7B (General)",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b"
    },
    {
      "title": "DeepSeek 6.7B (Debugging)",
      "provider": "ollama",
      "model": "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
    },
    {
      "title": "CodeLlama 7B (Python)",
      "provider": "ollama",
      "model": "codellama:7b-python"
    }
  ]
}
```

Luego puedes cambiar entre modelos en el chat.

### Optimización de Rendimiento

```json
{
  "tabAutocompleteOptions": {
    "debounceDelay": 500,
    "maxPromptTokens": 1024,
    "prefixPercentage": 0.5
  }
}
```

### Desactivar Autocompletado (si es muy lento)

```json
{
  "tabAutocompleteModel": null
}
```

## 🧪 Probar la Instalación

### Test 1: Chat Básico

1. Abrir Continue panel
2. Escribir: `Write a Python function to calculate fibonacci`
3. Debería responder en 2-5 segundos

### Test 2: Autocompletado

1. Crear archivo `test.py`
2. Escribir: `def hello_`
3. Debería sugerir completar la función

### Test 3: Edición de Código

1. Escribir código simple:
```python
def add(a, b):
    return a + b
```
2. Seleccionar la función
3. `Ctrl + I`
4. Escribir: "Add type hints and docstring"
5. Continue debería editar el código

## 📊 Rendimiento Esperado

Con tu hardware (Intel i7-1255U, 16GB RAM):

| Acción | Tiempo | Modelo |
|--------|--------|--------|
| Chat response | 2-4 seg | qwen2.5-coder:7b |
| Autocompletado | 0.5-1 seg | qwen2.5-coder:1.5b |
| Edición de código | 3-6 seg | qwen2.5-coder:7b |
| Búsqueda en codebase | 1-2 seg | nomic-embed-text |

## 🆚 Continue vs GitHub Copilot

| Característica | Continue + Ollama | GitHub Copilot |
|----------------|-------------------|----------------|
| Costo | Gratis | $10-20/mes |
| Privacidad | 100% local | Cloud |
| Restricciones corporativas | ❌ Ninguna | ✅ Puede tener |
| Modelos | Cualquiera (Ollama) | Solo OpenAI |
| Autocompletado | ✅ | ✅ |
| Chat | ✅ | ✅ |
| Edición directa | ✅ | ⚠️ Limitado |
| Context providers | ✅ Más opciones | ✅ |
| Offline | ✅ | ❌ |

## 🔧 Troubleshooting

### "Cannot connect to Ollama"

```powershell
# Verificar que Ollama está corriendo
ollama serve

# En otra terminal
ollama list
```

### Autocompletado muy lento

1. Cambiar a modelo más pequeño:
```json
{
  "tabAutocompleteModel": {
    "model": "qwen2.5-coder:1.5b"
  }
}
```

2. O desactivar temporalmente:
```json
{
  "tabAutocompleteModel": null
}
```

### Chat no responde

1. Verificar que el modelo está descargado:
```powershell
ollama list
```

2. Probar el modelo directamente:
```powershell
ollama run qwen2.5-coder:7b "Hello"
```

## 🎯 Atajos de Teclado

| Acción | Atajo |
|--------|-------|
| Abrir Continue Chat | `Ctrl + L` |
| Editar código seleccionado | `Ctrl + I` |
| Aceptar autocompletado | `Tab` |
| Rechazar autocompletado | `Esc` |
| Siguiente sugerencia | `Alt + ]` |
| Anterior sugerencia | `Alt + [` |

## 📚 Recursos

- [Continue Documentation](https://docs.continue.dev)
- [Continue GitHub](https://github.com/continuedev/continue)
- [Ollama Models](https://ollama.com/library)
- [Qwen2.5-Coder](https://ollama.com/library/qwen2.5-coder)

## 🚀 Próximos Pasos

1. ✅ Instalar Continue extension
2. ✅ Configurar con Ollama
3. ✅ Probar chat y autocompletado
4. 📖 Explorar comandos slash
5. 🎨 Personalizar configuración

---

**¡Listo!** Ahora tienes un copilot completamente funcional sin restricciones corporativas.
