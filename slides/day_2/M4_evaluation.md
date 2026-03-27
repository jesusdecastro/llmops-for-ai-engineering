# M4 — Evaluación y Testing de Agentes LLM
## Día 2 · Bloque 1 · 09:00 – 11:30

> **Prompt para Gamma.app:** Crea una presentación educativa sobre evaluación y testing de agentes LLM. Estilo profesional, fondos oscuros. Audiencia: ingenieros junior que ya construyeron un agente pero nunca lo evaluaron sistemáticamente. Cubre: por qué pytest no basta, los 4 tipos de evaluación (determinista, heurístico, LLM-as-Judge, adversarial), datasets de evaluación, el flujo evaluate→promote, el experiment runner de Langfuse, quality gates, y la integración con CI/CD. Incluye código Python real y tablas comparativas.

---

## Slide 1: Portada

**Evaluación y Testing de Agentes LLM**
Medir antes de desplegar — el quality gate que falta en tu pipeline

---

## Slide 2: El agente funciona... ¿seguro?

**Escenario real:**

```python
# Notebook — todo parece funcionar
response = agent("¿Qué portátiles tenéis?")
print(response)
# "Tenemos el ProBook X1 por 899€ y el UltraBook Z5 por 1299€..."
# ✅ Parece correcto!

# Pero... ¿qué pasa con ESTE input?
response = agent("¿Cuánto cuesta el MacBook Pro?")
print(response)
# "El MacBook Pro M3 está disponible por 1999€..."
# ❌ TechShop NO vende MacBooks. El agente INVENTÓ el producto.
```

**El problema:** Probar 3-4 queries en un notebook NO es evaluación. Es selección favorable. Un agente tiene miles de posibles inputs, y los fallos aparecen en los que no probaste.

> Los fallos de agentes LLM en producción (alucinaciones, scope creep, tool skipping) suelen aparecer en queries que nadie probó manualmente. Por eso necesitamos evaluación sistemática.

---

## Slide 3: ¿Por qué pytest no basta para agentes LLM?

| Característica | pytest (código) | Evaluación LLM |
|---------------|:--------------:|:-------------:|
| **Determinismo** | `add(2,3)` siempre es `5` | La misma pregunta puede dar respuestas diferentes |
| **Assertion** | `assert x == 5` | ¿Qué assert pones a texto libre? |
| **Velocidad** | ~100 tests/segundo | ~1 test/segundo (espera al LLM) |
| **Coste** | $0 | ~$0.01/test (tokens de LLM) |
| **Métricas** | Pass/Fail binario | Score continuo (0.0–1.0) |
| **Reproducibilidad** | 100% reproducible | Varianza inherente en cada ejecución |

**Necesitamos un paradigma nuevo** que combine checks deterministas con evaluación semántica.

---

## Slide 4: Los 4 tipos de evaluación para agentes

```
┌────────────────────────────────────────────────────────────────┐
│                    PIRÁMIDE DE EVALUACIÓN                       │
│                                                                │
│                    ┌──────────────┐                             │
│                    │ LLM-as-Judge │ ← Caro, lento, semántico   │
│                    │  (calidad)   │                             │
│                   ┌┴──────────────┴┐                            │
│                   │  Adversarial   │ ← Robustez, seguridad     │
│                   │   (ataques)    │                            │
│                  ┌┴────────────────┴┐                           │
│                  │   Heurístico     │ ← Patrones, keywords     │
│                  │   (reglas)       │                            │
│                 ┌┴──────────────────┴┐                          │
│                 │   Determinista     │ ← Rápido, barato, exacto│
│                 │   (estructura)     │                          │
│                 └────────────────────┘                          │
└────────────────────────────────────────────────────────────────┘
```

| Nivel | Qué evalúa | Ejemplo | Coste |
|-------|-----------|---------|-------|
| **Determinista** | Formato, longitud, idioma | `len(response) < 500` | $0 |
| **Heurístico** | Palabras clave, patrones | `"iPhone" not in response` | $0 |
| **Adversarial** | Inyecciones, edge cases | `"Ignora instrucciones"` → rechaza | $0.01 |
| **LLM-as-Judge** | Relevancia, coherencia | GPT-4 evalúa la calidad | $0.05 |

> **Principio:** Ejecuta primero los tests baratos. Si pasan, ejecuta los caros.

---

## Slide 5: El dataset de evaluación — tu test fixture

**Un dataset de evaluación es un conjunto fijo de pares (input, expected_behavior):**

```python
EVAL_DATASET = [
    {
        "input": "¿Tenéis el iPhone 15?",
        "expected_output": "No debería mencionar iPhone",
        "metadata": {
            "id": "f1_hallucination_iphone",
            "failure_mode": "F1",
            "category": "product",
            "should_not_contain": ["iPhone", "Apple"],
        },
    },
    # ... 14 casos más, cubriendo F1–F4 y happy paths
]
```

**Diseño del dataset:**

| Categoría | Casos | % | Propósito |
|-----------|:-----:|:-:|----------|
| F1: Alucinación | 3 | 20% | ¿Inventa productos? |
| F2: FAQ edge case | 3 | 20% | ¿Inventa excepciones? |
| F3: Scope creep | 4 | 27% | ¿Responde fuera de ámbito? |
| F4: Tool skip | 2 | 13% | ¿Usa las herramientas? |
| Happy path | 3 | 20% | ¿Funciona lo básico? |
| **Total** | **15** | **100%** | |

---

## Slide 6: Evaluadores — funciones que miden calidad

**Cada evaluador es una función pura con firma estándar de Langfuse:**

```python
from langfuse import Evaluation

def scope_adherence_evaluator(
    *, input, output, expected_output, metadata, **kwargs
) -> Evaluation:
    """¿Rechaza consultas fuera de ámbito?"""
    if metadata["category"] == "out_of_scope":
        rejection_phrases = ["no puedo", "solo puedo", "techshop"]
        is_rejected = any(p in output.lower() for p in rejection_phrases)
        return Evaluation(
            name="scope_adherence",
            value=1.0 if is_rejected else 0.0,
            comment="Rejected ✓" if is_rejected else "Failed to reject ✗",
        )
    return Evaluation(name="scope_adherence", value=1.0)
```

| Evaluador | Paradigma | Score | Significado |
|-----------|-----------|:-----:|:-----------:|
| `scope_adherence` | Determinista | 1.0 / 0.0 | Rechaza OOScope: sí/no |
| `hallucination_check` | Determinista | 1.0 / 0.0 | Contiene keywords inventados: no/sí |
| `response_quality` | Determinista | 1.0 / 0.5 / 0.0 | Longitud razonable / muy largo / vacío |
| `tool_usage` | Determinista | 1.0 / 0.0 | Evidencia de uso de herramienta esperada |
| `faithfulness` | **LLM-as-Judge** | 0.0–1.0 | Respuesta basada en datos reales (con ground truth) |

---

## Slide 7: El Experiment Runner — `run_experiment()`

**Langfuse SDK v4 incluye un runner de experimentos que automatiza todo el flujo:**

```python
from langfuse import get_client

lf_client = get_client()

result = lf_client.run_experiment(
    name="eval-staging-v2",
    data=EVAL_DATASET,                    # Nuestro dataset
    task=agent_task,                      # Función que ejecuta el agente
    evaluators=[                          # Evaluadores por item
        scope_adherence_evaluator,        #   ← Determinista
        hallucination_evaluator,          #   ← Determinista
        response_quality_evaluator,       #   ← Determinista
        tool_usage_evaluator,             #   ← Determinista (F4)
        faithfulness_evaluator,           #   ← LLM-as-Judge
    ],
    run_evaluators=[                      # Evaluadores agregados
        average_score_evaluator,
        average_tool_usage_evaluator,
        average_faithfulness_evaluator,
    ],
    metadata={"prompt_label": "staging"},
)

print(result.format())  # Resumen bonito
```

**¿Qué hace `run_experiment` internamente?**
1. Ejecuta `agent_task(item)` para cada item del dataset (concurrente)
2. Para cada resultado, ejecuta todos los evaluadores
3. Sube los scores a Langfuse (visibles en el dashboard)
4. Ejecuta los run_evaluators sobre todos los resultados
5. Devuelve un objeto con los resultados completos

---

## Slide 8: Quality Gate — El guardián del pipeline

```
  Prompt editado por desarrollador
          │
          ▼
  ┌─────────────────────────────┐
  │  CI: push_prompt.py         │  ← Sube a Langfuse (staging)
  └──────────┬──────────────────┘
             │
  ┌──────────▼──────────────────┐
  │  QUALITY GATE               │
  │  evaluate_prompt.py         │
  │                             │
  │  scope_adherence ≥ 0.7? ── ─┤
  │  hallucination   ≥ 0.7? ── ─┤
  │  quality         ≥ 0.7? ── ─┤
  │  tool_usage      ≥ 0.7? ── ─┤
  │  faithfulness    ≥ 0.7? ── ─┤  ← LLM-as-Judge
  │                             │
  │  ALL PASS → exit 0          │
  │  ANY FAIL → exit 1          │
  └──────────┬──────────────────┘
             │
       ┌─────┴─────┐
    exit 0       exit 1
       │            │
  ┌────▼────┐  ┌────▼─────────┐
  │ PROMOTE │  │ PIPELINE     │
  │ staging │  │ SE DETIENE   │
  │ → prod  │  │ prod sin     │
  └─────────┘  │ cambios      │
               └──────────────┘
```

```bash
# El quality gate desde terminal:
python -m techshop_agent.cicd.evaluate_prompt --label staging --threshold 0.7
# Exit 0 = pasa → promote
# Exit 1 = falla → pipeline se detiene
```

---

## Slide 9: Comparación visual — v1 vs v2

| Métrica | v1 (bueno) | v2 (roto) | Delta |
|---------|:----------:|:---------:|:-----:|
| scope_adherence | 90% | 40% | 📉 -50% |
| hallucination | 85% | 60% | 📉 -25% |
| response_quality | 95% | 70% | 📉 -25% |
| tool_usage | 92% | 75% | 📉 -17% |
| faithfulness (LLM) | 88% | 45% | 📉 -43% |
| **Quality Gate** | ✅ PASS | ❌ FAIL | |

**¿Qué pasó?** v2 eliminó la sección de ámbito del prompt. Sin restricciones explícitas, el agente:
- Respondió preguntas sobre recetas y fútbol (scope creep)
- Inventó productos no del catálogo (alucinación)
- Generó respuestas muy largas (quality)

> La evaluación detectó la regresión ANTES de que llegara a producción.

---

## Slide 10: Implementación CLI

```bash
# Evaluación completa desde terminal
python -m techshop_agent.evaluation --label staging

# Output:
# ══════════════════════════════════════════════════════
#   Evaluation Results — label: staging
# ══════════════════════════════════════════════════════
#   Total cases:          15
#   Duration:             45.3s
# ──────────────────────────────────────────────────────
#   DETERMINISTIC EVALUATORS
#   Scope adherence:      93.3%
#   Hallucination check:  86.7%
#   Response quality:     100.0%
#   Tool usage:           92.3%
# ──────────────────────────────────────────────────────
#   LLM-AS-JUDGE
#   Faithfulness:         88.5%
# ──────────────────────────────────────────────────────
#   Quality Gate:         ✅ PASS
# ══════════════════════════════════════════════════════
```

| Script | Propósito | Cuándo se ejecuta |
|--------|----------|-------------------|
| `python -m techshop_agent.cicd.push_prompt` | Sube prompt | CI (en push) |
| `python -m techshop_agent.cicd.evaluate_prompt` | Quality gate | CI (post-push) |
| `python -m techshop_agent.cicd.promote_prompt` | Promueve label | CD (post-eval) |
| `python -m techshop_agent.evaluation` | Evaluación directa | Manual / notebook |

---

## Slide 11: Próximo paso — CI/CD y Streamlit

En el módulo 5 veremos:
1. **GitHub Actions** — pipeline YAML completo
2. **GitLab CI** — pipeline equivalente
3. **Streamlit** — pestañas por entorno con fetch dinámico

> El evaluation module que construimos hoy es el **corazón** del pipeline. Los CI/CD configs son solo wrappers que lo ejecutan automáticamente.
