# 🛒 TechShop Agent — Interfaz Streamlit

Interfaz web interactiva para el agente TechShop del curso LLMOps, construida con Streamlit y la paleta de marca **Hiberus Tecnología**.

> Requiere que el agente esté configurado en el directorio raíz (`src/techshop_agent`).

---

## Requisitos previos

| Requisito | Versión mínima | Verificar |
|-----------|---------------|-----------|
| Python | 3.11+ | `python --version` |
| uv | 0.5+ | `uv --version` |
| Variables de entorno AWS | — | ver sección siguiente |

---

## Paso a paso: primera ejecución

### 1. Clonar e instalar dependencias del proyecto principal

```bash
# Desde la raíz del repositorio
cd llmops-for-ai-engineering
uv sync
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del repositorio (o en `streamlit_app/`):

```bash
cp .env.example .env     # si existe, o créalo manualmente
```

Edita `.env` con tus credenciales:

```env
# ── AWS Bedrock (obligatorio) ─────────────────────────────────────────
AWS_REGION=us-east-1
# Opción A — perfil IAM:
AWS_PROFILE=your-profile
# Opción B — credenciales directas (no recomendado para producción):
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...

# Modelo (usa el inference profile correcto para tu región)
MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0

# ── Langfuse (opcional, activa observabilidad) ────────────────────────
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

> **Sin Langfuse:** la app funciona igualmente; el sidebar mostrará "⚠️ Langfuse no configurado".

### 3. Instalar dependencias de la UI

```bash
cd streamlit_app/
uv sync          # instala streamlit y las dependencias del subpaquete
```

### 4. Ejecutar la aplicación

```bash
# Desde streamlit_app/
streamlit run app.py

# O con puerto específico:
streamlit run app.py --server.port 8501

# O desde la raíz del repo:
cd ..
streamlit run streamlit_app/app.py
```

La app estará disponible en **http://localhost:8501** ✅

---

## Acceso rápido con Make

Desde la raíz del repositorio puedes añadir este alias:

```bash
make ui       # arranca la interfaz Streamlit
```

> *Si `make ui` no está definido, ejecuta directamente:*
> ```bash
> cd streamlit_app && streamlit run app.py
> ```

---

## Estructura de la interfaz

```
┌────────────────────────────────────────────────────────┐
│  SIDEBAR               │  COLUMNA PRINCIPAL (3/4)      │
│  ─────────────────────  │  ─────────────────────────── │
│  🛒 TechShop Brand     │  Hero banner (modelo/región)  │
│  📋 Sesión activa      │  Métricas (consultas/latencia) │
│  ↻  Nueva sesión       │  Chat con Alex                │
│  📊 Langfuse status   │                               │
│  🤖 Modelo AWS         │  COLUMNA INFO (1/4)           │
│  💡 Preguntas ejemplo  │  🧪 Fallos F1-F4              │
│                        │  🔧 Stack técnico             │
│                        │  📚 Módulos del curso         │
└────────────────────────────────────────────────────────┘
```

---

## Funcionalidades

| Función | Descripción |
|---------|-------------|
| **Chat con Alex** | Interfaz conversacional con el agente TechShop |
| **Métricas en tiempo real** | Consultas, latencia media, turnos y errores |
| **Preguntas de ejemplo** | Atajos en el sidebar para probar el agente rápidamente |
| **Nueva sesión** | Limpia el historial y genera un nuevo `session_id` |
| **Observabilidad** | Si Langfuse está configurado, cada consulta genera una traza |
| **Indicador de latencia** | Cada respuesta muestra el tiempo en ms |

---

## Opciones de configuración avanzadas

### Puerto y host

```bash
streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \   # exponer en red local
  --server.headless true        # sin abrir navegador automáticamente
```

### Tema Streamlit (`.streamlit/config.toml`)

El archivo `.streamlit/config.toml` ya está configurado con la paleta Hiberus:

```toml
[theme]
primaryColor        = "#E84610"   # Naranja Hiberus
backgroundColor     = "#FFFFFF"
secondaryBackgroundColor = "#F4F7FB"
textColor           = "#0F172A"
font                = "sans serif"
```

### Variables de entorno adicionales

| Variable | Valor por defecto | Descripción |
|----------|-----------|-------------|
| `MODEL_ID` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | Modelo Bedrock |
| `AWS_REGION` | `us-east-1` | Región AWS |
| `LANGFUSE_PUBLIC_KEY` | — | Activa tracing si está definida |
| `LANGFUSE_SECRET_KEY` | — | Par de la clave pública |
| `LANGFUSE_HOST` | `cloud.langfuse.com` | URL de la instancia Langfuse |

---

## Solución de problemas

### `ModuleNotFoundError: techshop_agent`

El paquete del agente no está instalado. Desde la **raíz** del repo:

```bash
uv sync
```

O instala el paquete de la UI con el agente como fuente editable:

```bash
cd streamlit_app && uv sync
```

### `botocore.exceptions.NoCredentialsError`

Las credenciales AWS no están configuradas. Comprueba:

```bash
aws sts get-caller-identity   # debe devolver tu Account/UserId
```

O asegúrate de que `.env` tiene `AWS_PROFILE` o `AWS_ACCESS_KEY_ID`.

### El agente responde lento (>5 s)

- Comprueba la región AWS; `us-east-1` suele tener menor latencia.
- Verifica que no hay throttling en Bedrock (panel AWS → Service Quotas).

### Puerto 8501 en uso

```bash
streamlit run app.py --server.port 8502
```

---

## Dependencias principales

```toml
# streamlit_app/pyproject.toml
dependencies = [
    "streamlit>=1.40.0",
    "techshop-agent",       # paquete local del repositorio
    "langfuse>=3.0.0",
    "python-dotenv>=1.0.0",
]
```

---

## Relacionado

- [README principal del curso](../README.md)
- [Código del agente](../src/techshop_agent/)
- [Notebooks del curso](../notebooks/README.md)
- [Documentación completa](../docs/README.md)
