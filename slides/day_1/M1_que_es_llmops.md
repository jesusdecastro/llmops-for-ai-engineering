# M1 — ¿Qué es LLMOps? El Ciclo. El Agente TechShop.
## Día 1 · Bloque 1 · 09:00 – 10:30

> **Prompt para Gamma.app:** Crea una presentación educativa para ingenieros junior sobre LLMOps. Estilo profesional y moderno, con fondos oscuros. Tema: "Del prototipo al producto con agentes de IA". Audiencia: ingenieros recién graduados con conocimiento de GenAI pero sin experiencia en producción. Tono: directo, profesional, con ejemplos reales. Incluye diagramas y tablas, pocas palabras por slide.

---

## Slide 1: Portada

**LLMOps para AI Engineering**
Día 1: ¿Qué está fallando y cómo me entero?

*Nombre del instructor*
*Fecha*

---

## Slide 2: El elefante en la habitación

**Tu agente funciona en local. ¿Y ahora qué?**

- Funciona en tu notebook ✅
- Funciona con tus datos de prueba ✅
- Funciona cuando lo usa alguien que no eres tú... ❓
- Funciona cuando lo usan 1.000 personas a la vez... ❓
- Funciona cuando el modelo cambia de versión... ❓

> 📊 **Dato:** El 73% de los deployments de LLMs no llegan a producción o fallan en los primeros 90 días.

*Speaker notes: Arranca con esta pregunta. Deja que los alumnos respondan. La idea es que sientan que hasta ahora han vivido en un entorno controlado.*

---

## Slide 3: Casos reales — Esto pasa en empresas de verdad

**Zalando** — Pipeline de análisis de postmortems
- El LLM culpaba a una tecnología por mencionarse en el texto, no por causarlo
- ~10% de errores de atribución persisten incluso con Claude Sonnet

**Stripe** — Detección de fraude
- 1.3% del GDP global procesado
- Card-testing fraud: de 59% a 97% accuracy

**Banco anónimo** — Chatbot customer service con GPT-4 + RAG
- Planificado en 3 meses, tardó el triple
- Problemas: domain knowledge, latencia, compliance

*Speaker notes: Estos casos anclan el por qué. No son hipotéticos — son de 2024-2025.*

---

## Slide 4: ¿Qué es LLMOps?

**LLMOps = las prácticas, herramientas y procesos para llevar sistemas basados en LLMs a producción y mantenerlos ahí.**

No es:
- Entrenar modelos (eso es MLOps)
- Solo hacer prompts (eso es prompt engineering)
- DevOps con un LLM encima

Es:
- Observar qué hace tu agente en producción
- Evaluar antes de deployar
- Proteger input y output
- Versionar prompts como código
- Iterar con datos reales

---

## Slide 5: MLOps ≠ LLMOps

| Dimensión | MLOps | LLMOps |
|-----------|-------|--------|
| **Outputs** | Espacio finito, determinista | Texto libre, estocástico |
| **Tipo de fallo** | Error medible (F1, RMSE) | Respuesta plausible pero incorrecta |
| **Costo principal** | Entrenamiento | Inferencia por token |
| **Artefacto** | Model weights + datos | Modelo + **prompt** + contexto |
| **Evaluación** | Métricas numéricas | Métricas + juicio semántico |
| **Versionado** | Modelo + datos | Modelo + prompt + config RAG |

> 💡 La diferencia clave: en MLOps el modelo falla con un error numérico. En LLMOps el modelo falla con una respuesta convincente pero incorrecta.

---

## Slide 6: El Ciclo LLMOps

```
[Develop] → [Evaluate] → [Deploy] → [Observe]
    ↑                                    │
    └──────── [Iterate] ◀───────────────┘

Transversal: GUARDRAILS (protección en tiempo real)
```

| Fase | Pregunta clave | Herramienta del curso |
|------|----------------|----------------------|
| Develop | ¿El prompt hace lo que quiero? | Langfuse Prompt Management |
| Evaluate | ¿Funciona antes de deployar? | Evaluaciones Python + LLM-as-judge |
| Deploy | ¿Cómo lo pongo en producción? | (Conceptual) |
| Observe | ¿Qué pasa en producción? | Langfuse Tracing |
| Guardrails | ¿Qué protejo? | Amazon Bedrock Guardrails |

---

## Slide 7: Las 4 categorías de métricas LLMOps

| Categoría | Ejemplos | Se mide con |
|-----------|----------|-------------|
| 🔧 **Operacionales** | Latencia P50/P99, throughput, errors | APM + Langfuse |
| 💰 **Coste** | Tokens in/out, € por request | Langfuse (auto) |
| ⭐ **Calidad** | Alucinaciones, relevancia, fidelidad | Evaluaciones + LLM-as-judge |
| 📊 **Uso** | Queries/hora, temas frecuentes | Langfuse Analytics |

> Las categorías 1-2 se miden con herramientas clásicas.
> Las categorías 3-4 **necesitan herramientas LLMOps específicas**.
> La categoría 3 — calidad — es la más importante y la más difícil.

---

## Slide 8: El agente TechShop — Nuestro caso práctico

**TechShop** = Tienda online de electrónica

El agente tiene:
- 🔍 **search_catalog** — Buscar productos (portátiles, smartphones, auriculares...)
- ❓ **get_faq_answer** — Consultar políticas (envíos, devoluciones, garantías...)

Stack:
- **Strands Agents** (framework)
- **Amazon Bedrock** (modelo de lenguaje)
- **Langfuse** (observabilidad)
- **Python** (todo)

> En los notebooks vais a construir este agente de cero y añadirle capas LLMOps.

---

## Slide 9: Roadmap de los 3 días

| Día | Pregunta | Qué construimos |
|-----|----------|-----------------|
| **1** | ¿Qué está fallando y cómo me entero? | Agente + Observabilidad |
| **2** | ¿Cómo sé que no rompe antes de producción? | Prompt versioning + Evaluación |
| **3** | ¿Cómo lo protejo y junto todo? | Guardrails + Pipeline completo |

**Formato:** Mañanas de teoría → Tardes de notebooks prácticos

---

## Slide 10: ¿Preguntas antes de empezar?

**Siguiente bloque:** Observabilidad — ¿por qué y cómo?

**Siguiente práctica:** Notebook 1 — Construir el agente TechShop

---

## 🎯 KAHOOT — Después de M1 (5 min)

**Q1:** ¿Qué porcentaje de deployments de LLMs fallan en los primeros 90 días según datos de industria?
- A) 25%
- B) 50%
- C) 73% ✅
- D) 90%

**Q2:** ¿Cuál es la PRINCIPAL diferencia entre un fallo en MLOps y uno en LLMOps?
- A) MLOps es más caro
- B) En LLMOps el fallo parece una respuesta correcta ✅
- C) MLOps usa Python y LLMOps no
- D) No hay diferencia

**Q3:** ¿Cuál de estas NO es una fase del ciclo LLMOps?
- A) Observe
- B) Evaluate
- C) Train ✅
- D) Deploy

**Q4:** ¿Qué categoría de métricas LLMOps es la MÁS difícil de medir?
- A) Operacionales
- B) Coste
- C) Calidad ✅
- D) Uso

---

## 📝 PADLET — Después de M1

**Prompt para el Padlet:** "¿Qué puede fallar en un agente de IA en producción? Pon un ejemplo real o imaginado."

*Objetivo: recoger ideas antes de introducir observabilidad. Después podemos referir a estas respuestas cuando veamos las trazas.*
