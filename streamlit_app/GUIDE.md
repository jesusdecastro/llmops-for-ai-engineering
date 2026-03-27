# Guía para alumnos — Personalizar y probar la app Streamlit

Esta guía explica **qué ficheros modificar**, **por qué**, **cuándo hay que reiniciar** y **qué integración LLMOps tiene la app**.

---

## Arquitectura rápida

```
streamlit_app/
├── app.py            ← Interfaz principal (Streamlit) con 3 tabs
├── app_config.py     ← ⭐ Config personalizable (nombre, ejemplos, entornos…)
├── pyproject.toml    ← Dependencias de la app
└── GUIDE.md          ← Este fichero

src/techshop_agent/
├── agent.py          ← Crea el agente base (modelo, tools, system prompt)
├── config.py         ← System prompt por defecto + loaders de datos
├── tools.py          ← Herramientas del agente (catálogo, FAQs…)
├── evaluation/       ← Suite de evaluación (dataset, evaluadores, runner)
├── cicd/             ← Scripts CI/CD (push_prompt, evaluate_prompt, promote_prompt)
└── solution/
    ├── observability.py    ← Agente instrumentado con Langfuse
    └── prompt_provider.py  ← Gestión de prompts versionados + scoring online

prompts/
└── system_prompt.txt ← Texto del prompt para subir a Langfuse
```

---

## Ciclo LLMOps integrado en Streamlit

La app implementa el ciclo completo de desarrollo de prompts **sin salir del navegador**:

```
 ┌─────────────────────────────────────────────────────────┐
 │                   💬 Tab: Chat                          │
 │  1. Selecciona un prompt (sidebar: Production/Staging)  │
 │  2. Chatea con el agente                                │
 │  3. Observa scores online en cada respuesta             │
 │  4. Las trazas se envían a Langfuse automáticamente     │
 └──────────────────────────┬──────────────────────────────┘
                            │ ¿El prompt funciona bien?
                            ▼
 ┌─────────────────────────────────────────────────────────┐
 │                   🧪 Tab: Evaluación                    │
 │  5. Ejecuta la suite de evaluación contra una label     │
 │  6. Ve los scores de 5 evaluadores (deterministas +     │
 │     LLM-as-Judge) y el veredicto PASS/FAIL              │
 │  7. Los resultados se registran como experimento en     │
 │     Langfuse para comparar entre versiones              │
 └──────────────────────────┬──────────────────────────────┘
                            │ Quality gate OK?
                            ▼
 ┌─────────────────────────────────────────────────────────┐
 │               🚀 Tab: Prompt CI/CD                      │
 │  8. Push: sube una nueva versión de prompt a Langfuse   │
 │     con las labels que elijas                           │
 │  9. Promote: promueve un prompt de staging → production │
 │     (o entre cualquier par de labels)                   │
 └─────────────────────────────────────────────────────────┘
```

### Qué se ve en cada traza de Langfuse (modo Instrumentado)

| Elemento | Detalle |
|----------|---------|
| **Trace** | `techshop_query_with_prompt` — una por interacción |
| **Metadata** | `prompt_label`, `prompt_version`, `is_fallback_prompt`, `source`, `session_id`, `user_id` |
| **Spans hijos** | Tool calls (`search_catalog`, `get_faq_answer`, etc.) + LLM generation (auto vía OTEL) |
| **Scores online** | `response_quality` (0–1), `scope_adherence` (0–1) — evaluadores deterministas, ~1ms |

### Qué se ve en los experimentos de Langfuse (tab Evaluación)

| Evaluador | Tipo | Qué mide |
|-----------|------|----------|
| Scope Adherence | Determinista | ¿Rechaza queries fuera de ámbito? ¿No rechaza las legítimas? |
| Hallucination Check | Determinista | ¿Inventa productos/datos que no existen en el catálogo? |
| Response Quality | Determinista | ¿Respuesta vacía, demasiado corta o excesivamente larga? |
| Tool Usage | Determinista | ¿Usa las herramientas cuando debe (catálogo, FAQ)? |
| Faithfulness | LLM-as-Judge | ¿La respuesta es fiel a los datos devueltos por las tools? |

---

## 1. Cambios que se recargan automáticamente (hot-reload)

Streamlit vigila los ficheros dentro de `streamlit_app/`. Cuando detecta un cambio en disco, refresca el navegador automáticamente.

| Fichero | Qué puedes cambiar | Reiniciar? |
|---------|---------------------|:----------:|
| `streamlit_app/app_config.py` | Nombre del agente, icono, ejemplos, entornos de prompt, user_id de tracing | **No** |
| `streamlit_app/app.py` | Lógica de la UI, layout, sidebar | **No** |

### Ejemplo: cambiar el nombre del agente

Edita `streamlit_app/app_config.py`:

```python
AGENT_NAME = "Mi Super Agente"
AGENT_ICON = "🤖"
AGENT_SUBTITLE = "Asistente personalizado — Equipo Alfa"
```

Guarda el fichero. Streamlit recarga automáticamente en el navegador.

### Ejemplo: añadir preguntas de ejemplo

```python
EXAMPLES: list[str] = [
    "¿Tenéis ratones gaming?",
    "Quiero un monitor 4K por menos de 500€",
    # ...añade las tuyas aquí
]
```

### Ejemplo: añadir un entorno de prompt custom

Si has creado una label nueva en Langfuse (ej. `variant-a`):

```python
ENVIRONMENTS: dict[str, str] = {
    "🟢 Production": "production",
    "🟡 Staging": "staging",
    "🔵 Development": "development",
    "🟣 Variante A": "variant-a",  # ← tu label custom
}
```

---

## 2. Cambios que requieren reiniciar el servidor

Streamlit **no** vigila los paquetes instalados. Si modificas el código fuente del agente (`src/techshop_agent/`), necesitas parar y relanzar.

| Fichero | Qué afecta | Acción |
|---------|-----------|--------|
| `src/techshop_agent/agent.py` | Modelo, tools, prompt base | `Ctrl+C` + relanzar |
| `src/techshop_agent/config.py` | System prompt por defecto, datos | `Ctrl+C` + relanzar |
| `src/techshop_agent/tools.py` | Herramientas del agente | `Ctrl+C` + relanzar |
| `src/techshop_agent/solution/observability.py` | Tracing Langfuse | `Ctrl+C` + relanzar |
| `src/techshop_agent/solution/prompt_provider.py` | Prompt versionado + scoring | `Ctrl+C` + relanzar |
| `src/techshop_agent/evaluation/*` | Evaluadores, dataset, runner | `Ctrl+C` + relanzar |
| `.env` | Credenciales AWS / Langfuse | `Ctrl+C` + relanzar |

**¿Por qué?** El paquete `techshop-agent` se importa una vez al arrancar. Las ediciones en `src/` no se reflejan hasta que Python vuelve a importar el módulo (= reiniciar).

### Cómo reiniciar

```bash
# En la terminal donde corre Streamlit:
Ctrl+C

# Relanzar:
uv run streamlit run app.py
```

---

## 3. Flujo de trabajo completo (paso a paso)

### Paso 1: Desarrollar el prompt

1. Edita `prompts/system_prompt.txt` con tu nuevo prompt.
2. Ve a la tab **🚀 Prompt CI/CD** → **📤 Push Prompt**.
3. Pega o carga el prompt, selecciona label `staging`, pulsa **Push**.
4. En la sidebar, selecciona **🟡 Staging** → **Aplicar cambio**.

### Paso 2: Probar manualmente en el chat

1. En la tab **💬 Chat**, haz preguntas al agente.
2. Cada respuesta muestra los **scores online** (Calidad + Ámbito).
3. La traza completa se envía a Langfuse con la versión del prompt vinculada.

### Paso 3: Evaluar con la suite completa

1. Ve a la tab **🧪 Evaluación**.
2. Selecciona label `staging`, threshold 0.7, pulsa **Ejecutar evaluación**.
3. Espera a que ejecute los ~15 casos del dataset contra el agente.
4. Revisa el veredicto (**PASS**/**FAIL**) y los scores por evaluador.
5. El experimento queda registrado en Langfuse para comparar versiones.

### Paso 4: Promover (o iterar)

- **Si PASS**: Tab **🚀 Prompt CI/CD** → **🔄 Promote** → `staging` → `production`.
- **Si FAIL**: Vuelve al paso 1, mejora el prompt, vuelve a evaluar.

### Botón de ver prompt

En cualquier momento, pulsa **👁 Ver prompt activo** en la sidebar para ver exactamente qué prompt está usando el agente.

---

## 4. Elementos LLMOps integrados

| Feature | Dónde | Descripción |
|---------|-------|-------------|
| **Prompt versionado** | Sidebar → Prompt Management | Seleciona entre `production`, `staging`, `development`. Muestra versión y disponibilidad. |
| **Prompt linking** | Automático (cada interacción) | La traza de Langfuse incluye `prompt_label` + `prompt_version` en metadata. |
| **Online scoring** | Chat (bajo cada respuesta) | `response_quality` + `scope_adherence` se calculan en ~1ms y se envían a Langfuse como scores del trace. |
| **Quality gate** | Tab Evaluación | 5 evaluadores + veredicto PASS/FAIL. Resultados como experimento en Langfuse. |
| **Push prompt** | Tab CI/CD → Push | Crea versión inmutable en Langfuse con labels a elegir. |
| **Promote prompt** | Tab CI/CD → Promote | Copia contenido de una label a otra (ej. `staging` → `production`). |
| **View prompt** | Sidebar + CI/CD Promote | Modal con contenido completo del prompt activo o de cualquier label. |

---

## 5. Checklist para la prueba

- [ ] Edita `app_config.py` → cambia `AGENT_NAME` → comprueba que Streamlit recarga.
- [ ] Añade una pregunta de ejemplo → comprueba que aparece en la sidebar.
- [ ] Sube un prompt a Langfuse con label `staging` (tab CI/CD → Push).
- [ ] En Streamlit, cambia a **Staging** → pulsa **Aplicar cambio** → chatea.
- [ ] Pulsa **"Ver prompt activo"** → verifica que ves el prompt de staging.
- [ ] Ejecuta la evaluación contra `staging` (tab Evaluación).
- [ ] Si pasa, promueve a `production` (tab CI/CD → Promote).
- [ ] Cambia a **Production** → verifica que el agente usa el nuevo prompt.

---

## 6. Resumen de ficheros clave

| Fichero | Para qué lo tocas | Hot-reload? |
|---------|-------------------|:-----------:|
| `streamlit_app/app_config.py` | Personalizar nombre, ejemplos, entornos | ✅ Sí |
| `streamlit_app/app.py` | Modificar la UI | ✅ Sí |
| `prompts/system_prompt.txt` | Editar el texto del prompt (para subir a Langfuse) | N/A |
| `src/techshop_agent/config.py` | Prompt por defecto del modo Base | ❌ Reiniciar |
| `src/techshop_agent/tools.py` | Añadir/modificar herramientas | ❌ Reiniciar |
| `src/techshop_agent/evaluation/dataset.py` | Casos de evaluación | ❌ Reiniciar |
| `src/techshop_agent/evaluation/evaluators.py` | Keywords de evaluadores | ❌ Reiniciar |
| `src/techshop_agent/solution/*.py` | Observabilidad y prompt provider | ❌ Reiniciar |
| `.env` | Credenciales (AWS, Langfuse) | ❌ Reiniciar |
