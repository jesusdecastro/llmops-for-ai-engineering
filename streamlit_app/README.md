# ðŸ›’ TechShop Agent â€” Interfaz Streamlit

Interfaz web interactiva para el agente TechShop del curso LLMOps, construida con Streamlit y la paleta de marca **Hiberus TecnologÃ­a**.

> Requiere que el agente estÃ© configurado en el directorio raÃ­z (`src/techshop_agent`).

---

## Requisitos previos

| Requisito | VersiÃ³n mÃ­nima | Verificar |
|-----------|---------------|-----------|
| Python | 3.11+ | `python --version` |
| uv | 0.5+ | `uv --version` |
| AWS credentials | â€” | `aws sts get-caller-identity` |

---

## Primera ejecuciÃ³n â€” paso a paso

### 1. Instalar dependencias del proyecto principal

```bash
# Desde la raÃ­z del repositorio
uv sync
```

> Esto instala `techshop-agent` en modo editable dentro del entorno `.venv/`.

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raÃ­z del repositorio:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# â”€â”€ AWS Bedrock (obligatorio) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AWS_REGION=eu-west-1
# OpciÃ³n A â€” perfil IAM:
AWS_PROFILE=your-profile
# OpciÃ³n B â€” credenciales directas:
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
# AWS_SESSION_TOKEN=...   # solo si son temporales (SSO/AssumeRole)

# Modelo (inference profile cross-region):
MODEL_ID=eu.anthropic.claude-haiku-4-5-20251001-v1:0

# â”€â”€ Langfuse (opcional, activa observabilidad) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

> **Sin Langfuse:** la app funciona igualmente. El modo Instrumentado seguirÃ¡ enviando queries al agente, pero sin registrar trazas.

### 3. Instalar dependencias de la UI

```bash
cd streamlit_app/
uv sync
```

> `uv sync` dentro de `streamlit_app/` lee su propio `pyproject.toml` y resuelve
> `techshop-agent` como editable desde el directorio padre (gracias a
> `[tool.uv.sources]`). Solo es necesario ejecutarlo una vez (o tras aÃ±adir
> nuevas dependencias al `pyproject.toml` de la UI).

### 4. Ejecutar la aplicaciÃ³n

```bash
# Desde streamlit_app/:
uv run streamlit run app.py

# Con puerto especÃ­fico:
uv run streamlit run app.py --server.port 8501

# Desde la raÃ­z del repo con make:
make streamlit
```

La app estarÃ¡ disponible en **http://localhost:8501** âœ…

---

## Modos del agente

El sidebar incluye un selector para alternar entre dos modos de ejecuciÃ³n:

| Modo | DescripciÃ³n | Trazas en Langfuse |
|------|-------------|-------------------|
| ðŸ¤– **Base** | `create_agent()` directo. Tracing mÃ­nimo si Langfuse estÃ¡ configurado. | Solo span raÃ­z `streamlit_query` |
| ðŸ“Š **Instrumentado** | `process_query()` de `solution/observability.py`. Tracing completo con spans de herramientas. | Ãrbol completo: `techshop_query` â†’ `tool_search_catalog` / `tool_get_faq_answer` â†’ LLM generation |

> Al cambiar de modo el historial se reinicia y se genera una nueva sesiÃ³n.

### Â¿QuÃ© ver en Langfuse?

Con el modo **Instrumentado** activo:
1. Abre tu instancia Langfuse â†’ **Traces**
2. Busca trazas con nombre `techshop_query`
3. Despliega el Ã¡rbol de spans: verÃ¡s los spans de herramientas con metadatos (`results_count`, `matched`) y la generaciÃ³n LLM con tokens

Con el modo **Base** activo:
1. Solo verÃ¡s un span raÃ­z `streamlit_query` con input/output
2. No hay spans de herramientas â†’ ideal para comparar la diferencia de observabilidad

---

## CuÃ¡ndo y cÃ³mo relanzar el servidor

Streamlit **recarga automÃ¡ticamente** el archivo `app.py` cuando lo guardas.  
Sin embargo, hay cambios en el agente que requieren **reiniciar el servidor manualmente**:

### Recarga automÃ¡tica (sin reiniciar)
Streamlit detecta automÃ¡ticamente cambios en `app.py` y recarga la pÃ¡gina.  
**Aplica a:** cambios en la UI (texto, layout, lÃ³gica de la interfaz).

### Reinicio manual necesario

Detener con `Ctrl+C` y relanzar con `uv run streamlit run app.py` cuando:

| SituaciÃ³n | Motivo |
|-----------|--------|
| Modificaste `src/techshop_agent/agent.py` | El agente se cachea con `@st.cache_resource`. La cachÃ© persiste hasta que el servidor se reinicia. |
| Modificaste `src/techshop_agent/config.py` | El `SYSTEM_PROMPT` y la configuraciÃ³n se leen una sola vez al importar el mÃ³dulo. |
| Modificaste `src/techshop_agent/tools.py` | Las herramientas se registran en el agente al momento de crearlo. |
| Modificaste `src/techshop_agent/solution/observability.py` | Mismo motivo: los singletons `_langfuse` y la configuraciÃ³n del agente observado se inicializan al importar. |
| AÃ±adiste una nueva dependencia a `pyproject.toml` | La dependencia no estÃ¡ instalada en el `sys.path` activo hasta que se reeje `uv sync`. |
| Cambiaste variables en `.env` | `.env` se carga una sola vez al arrancar la app. |

### Flujo recomendado al modificar el agente

```bash
# 1. Edita el archivo que necesitas cambiar
#    (agent.py, config.py, tools.py, etc.)

# 2. Si aÃ±adiste dependencias, sincroniza primero:
uv sync   # desde la raÃ­z del repo

# 3. DetÃ©n el servidor Streamlit (Ctrl+C en la terminal)

# 4. Relanza:
cd streamlit_app && uv run streamlit run app.py --server.port 8501
# o desde la raÃ­z:
make streamlit
```

> **Tip:** Con VS Code abierto, puedes usar el panel de terminal integrado para
> tener siempre visible el servidor. Al modificar el cÃ³digo, para el servidor
> desde el terminal (`Ctrl+C`) y relÃ¡nzalo con `â†‘ Enter`.

---

## Acceso rÃ¡pido con Make

Desde la raÃ­z del repositorio:

```bash
make streamlit-install   # primera vez: cd streamlit_app && uv sync
make streamlit           # arrancar en http://localhost:8501
```

---

## Estructura de la interfaz

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  SIDEBAR                       â”‚  CHAT (principal)     â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ â”‚
â”‚  ðŸ›’ TechShop Agent             â”‚  Historial de mensajesâ”‚
â”‚  ðŸ“‹ SesiÃ³n activa              â”‚                       â”‚
â”‚  â†»  Nueva sesiÃ³n               â”‚  Input del usuario    â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚                       â”‚
â”‚  ðŸ”§ Modo del agente            â”‚                       â”‚
â”‚    â—‹ ðŸ¤– Base (sin tracing)     â”‚                       â”‚
â”‚    â—‹ ðŸ“Š Instrumentado          â”‚                       â”‚
â”‚  (estado Langfuse)             â”‚                       â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚                       â”‚
â”‚  ðŸ’¡ Preguntas de ejemplo       â”‚                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Opciones de configuraciÃ³n avanzadas

### Puerto y host

```bash
uv run streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true
```

### Tema Streamlit (`.streamlit/config.toml`)

```toml
[theme]
primaryColor             = "#E84610"   # Naranja Hiberus
backgroundColor          = "#FFFFFF"
secondaryBackgroundColor = "#F4F7FB"
textColor                = "#0F172A"
font                     = "sans serif"
```

### Variables de entorno

| Variable | Valor por defecto | DescripciÃ³n |
|----------|-----------|-------------|
| `MODEL_ID` | `eu.anthropic.claude-haiku-4-5-20251001-v1:0` | Modelo Bedrock |
| `AWS_REGION` | `eu-west-1` | RegiÃ³n AWS |
| `LANGFUSE_PUBLIC_KEY` | â€” | Activa tracing si estÃ¡ definida |
| `LANGFUSE_SECRET_KEY` | â€” | Par de la clave pÃºblica |
| `LANGFUSE_BASE_URL` | `https://cloud.langfuse.com` | URL instancia Langfuse |

---

## SoluciÃ³n de problemas

### `ModuleNotFoundError: techshop_agent`

El paquete del agente no estÃ¡ instalado. Desde la **raÃ­z** del repo:

```bash
uv sync
```

O instala el paquete de la UI (que incluye el agente como editable):

```bash
cd streamlit_app && uv sync
```

### `botocore.exceptions.NoCredentialsError`

Las credenciales AWS no estÃ¡n configuradas:

```bash
aws sts get-caller-identity   # verifica credenciales activas
```

O asegÃºrate de que `.env` tiene `AWS_PROFILE` o `AWS_ACCESS_KEY_ID`.

### El agente no refleja cambios recientes

Reinicia el servidor (ver secciÃ³n **"CuÃ¡ndo y cÃ³mo relanzar el servidor"** arriba).

### El agente responde lento (>5 s)

- Comprueba la regiÃ³n AWS; `eu-west-1` suele tener menor latencia.
- Verifica que no hay throttling en Bedrock (panel AWS â†’ Service Quotas).

### Puerto 8501 en uso

```bash
# Ver quÃ© proceso ocupa el puerto:
netstat -ano | findstr :8501   # Windows
lsof -i :8501                  # macOS/Linux

# Usar otro puerto:
uv run streamlit run app.py --server.port 8502
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
- [CÃ³digo del agente](../src/techshop_agent/)
- [Notebooks del curso](../notebooks/README.md)
- [DocumentaciÃ³n completa](../docs/README.md)
