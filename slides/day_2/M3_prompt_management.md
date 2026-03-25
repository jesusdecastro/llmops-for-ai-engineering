# M3 — Prompt Management: Versionado, Labels y Control
## Día 2 · Bloque 1 · 09:00 – 10:30

> **Prompt para Gamma.app:** Crea una presentación educativa sobre Prompt Management para LLMs en producción. Estilo profesional, fondos oscuros. Tema: "El prompt es un artefacto de producción". Audiencia: ingenieros junior. Incluye diagramas de flujo de versionado, tablas comparativas, ejemplos de prompt drift. Pocas palabras, muchos visuales.

---

## Slide 1: Portada

**Prompt Management**
El prompt es código. Trátalo como tal.

*Día 2: ¿Cómo sé que no rompe antes de producción?*

---

## Slide 2: Recap del Día 1

**Ayer aprendimos:**
- El agente TechShop funciona con Strands + Bedrock
- Langfuse nos da visibilidad: trazas, spans, generations
- Podemos ver exactamente qué pasa en cada query

**Hoy respondemos:** ¿Qué pasa cuando alguien cambia el prompt?

---

## Slide 3: El prompt es el nuevo código

**En sistemas LLM, el prompt determina:**
- Qué hace el agente
- Cómo se comporta
- Qué rechaza
- Qué formato usa

Pero a diferencia del código:
- ❌ No se versiona (suele estar hardcodeado)
- ❌ No se testea antes de deployar
- ❌ No tiene rollback
- ❌ Cualquiera puede editarlo sin review

> **¿Harías push to main sin revisión en tu código?** Con los prompts pasa constantemente.

---

## Slide 4: Prompt Drift — El enemigo invisible

**Prompt drift** = El comportamiento del agente cambia por modificaciones no controladas del prompt.

Escenario real:
1. Lunes: El prompt dice "responde en español, máximo 3 frases"
2. Martes: Alguien añade "sé amigable y detallado"
3. Miércoles: El agente responde párrafos largos en vez de 3 frases
4. Jueves: Los usuarios se quejan de respuestas largas
5. Viernes: Nadie sabe qué cambió ni cuándo

**Sin versionado, no hay manera de saber qué prompt estaba activo cuando surgió el problema.**

---

## Slide 5: La solución — Prompt como artefacto

| Código | Prompt (debería ser igual) |
|--------|---------------------------|
| Git: historia completa | Langfuse: versiones numeradas |
| Branches: feature/fix | Labels: production, staging |
| PR review antes de merge | Evaluación antes de promote |
| Rollback: git revert | Rollback: cambiar label |
| CI/CD: tests automáticos | Eval gate: tests de prompt |

---

## Slide 6: Langfuse Prompt Management

**Flujo de trabajo:**

```
Crear prompt v1 → Label "production" → El agente lo usa
    │
    ├── Crear prompt v2 → Label "latest" → Solo testing
    │   │
    │   ├── Evaluar v2 vs v1
    │   │
    │   └── Si v2 es mejor → Mover "production" a v2
    │
    └── Si v2 falla → v1 sigue como "production" (sin cambios)
```

**Conceptos clave:**
- **Versión**: Número inmutable (v1, v2, v3...)
- **Label**: Puntero movible ("production", "latest", "staging")
- **Rollback**: Mover label "production" de vuelta a una versión anterior

---

## Slide 7: Código — Obtener prompt de Langfuse

```python
from langfuse import Langfuse

langfuse = Langfuse()

# Obtener el prompt que tenga label "production"
prompt = langfuse.get_prompt(
    "techshop-system-prompt",
    label="production",
    type="text",
)

# Usarlo en el agente
agent = Agent(
    model=model,
    tools=tools,
    system_prompt=prompt.prompt,  # El texto del prompt
)
```

**Cambiar de v1 a v2 en producción = cambiar el label. Sin tocar código.**

---

## Slide 8: Variables en prompts

```
Eres un asistente de {{company_name}}.
Categorías disponibles: {{catalog_categories}}
Temas de FAQ: {{faq_topics}}
```

```python
prompt.compile(
    company_name="TechShop",
    catalog_categories="portátiles, smartphones, audio",
    faq_topics="envíos, devoluciones, garantías",
)
```

**Ventaja:** Un prompt, múltiples tiendas. Cambiar datos sin versionar el prompt.

---

## Slide 9: Alternativas de Prompt Management

| Herramienta | Tipo | Ventaja |
|-------------|------|---------|
| **Langfuse** | Plataforma LLMOps | Integrado con tracing, labels, API |
| **promptfoo** | CLI evaluación | YAML config, comparación visual, CI |
| **Git** | Archivos en repo | Familiar, PR reviews, CI/CD estándar |
| **Hardcodeado** | En el código | Simple pero sin control |

> **promptfoo** es especialmente bueno para CI/CD — define test cases en YAML, ejecuta contra múltiples versiones, genera reportes comparativos. Ideal cuando quieres un gate automático en GitHub Actions.

---

## Slide 10: ¿Cuándo cambiar el prompt?

**Razones válidas para versionar:**
- Añadir/quitar capacidades del agente
- Mejorar formato de respuesta
- Corregir un fallo detectado por observabilidad
- Cambiar boundaries (qué puede/no puede hacer)
- Optimizar tokens (prompts más cortos = más baratos)

**Siempre con el mismo proceso:**
1. Crear nueva versión
2. Evaluar contra la anterior
3. Promover solo si mejora (o no empeora)

---

## Slide 11: Resumen

| Concepto | Takeaway |
|----------|----------|
| **Prompt drift** | Sin control, el comportamiento cambia sin que nadie sepa |
| **Versionado** | Cada cambio = nueva versión inmutable |
| **Labels** | Punteros movibles: production, latest, staging |
| **Rollback** | Cambiar label = rollback instantáneo |
| **Evaluación** | Nunca promover sin comparar con la versión anterior |

> **Concepto clave:** Del "edito el prompt y rezo" al "versiono, comparo, y despliego con confianza".

---

## 🎯 KAHOOT — Después de M3 (5 min)

**Q1:** ¿Qué es "prompt drift"?
- A) Cuando el modelo se actualiza
- B) Cuando el prompt cambia sin control y el comportamiento varía ✅
- C) Cuando el prompt es muy largo
- D) Cuando el usuario escribe mal

**Q2:** En Langfuse, ¿qué es un "label" de prompt?
- A) Un número de versión fijo
- B) Un puntero movible que apunta a una versión ✅
- C) El nombre del prompt
- D) Un tag de Git

**Q3:** ¿Cuál es la forma más segura de hacer rollback de un prompt?
- A) Editar el prompt en producción directamente
- B) Borrar la versión nueva
- C) Mover el label "production" a la versión anterior ✅
- D) Reiniciar el servidor

**Q4:** ¿Cuál de estas herramientas se especializa en evaluación de prompts con config YAML y CI/CD?
- A) Langfuse
- B) promptfoo ✅
- C) OpenTelemetry
- D) boto3

---

## 📝 PADLET — Después de M3

**Prompt para el Padlet:** "Piensa en el system prompt de TechShop (v1). ¿Qué le falta? ¿Qué regla o instrucción añadirías para mejorarlo? Escribe tu sugerencia."

*Objetivo: los alumnos proponen mejoras al prompt v1 ANTES de ver el v2. Después comparamos sus ideas con lo que implementamos.*
