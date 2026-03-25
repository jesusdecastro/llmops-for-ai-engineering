# M1 — ¿Qué es LLMOps? El Ciclo. El Agente TechShop.
## Día 1 · Bloque 1 · 09:00 – 10:30

> **Prompt para Gamma.app:** Crea una presentación educativa para ingenieros junior sobre LLMOps. Estilo profesional y moderno, con fondos oscuros. Tema: "Del prototipo al producto con agentes de IA". Audiencia: ingenieros recién graduados con conocimiento de GenAI pero sin experiencia en producción. Tono: directo, profesional, con ejemplos concretos del propio proyecto del curso. Incluye diagramas y tablas, pocas palabras por slide. Hilo narrativo: "tu agente funciona en local → hay un tipo de fallo nuevo que no detectas con herramientas clásicas → LLMOps es la disciplina → el ciclo es el marco → TechShop es donde lo practicamos".

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
- Funciona cuando el modelo cambia de versión... ❓
- Funciona cuando alguien intenta romperlo a propósito... ❓

> La mayoría de agentes LLM nunca llegan a producción. No por falta de modelo, sino por falta de proceso.

*Speaker notes: Arranca con esta pregunta. Deja que los alumnos respondan. La idea es que sientan que hasta ahora han vivido en un entorno controlado. No es un problema de inteligencia del modelo — es un problema de ingeniería.*

---

## Slide 3: Dos tipos de fallos — y solo detectas uno

**Bug de código — lo detectas con herramientas que ya conoces:**
```python
# La herramienta search_catalog tiene un bug en el filtro de precio
results = search_catalog("portátiles baratos")
# → Devuelve [], aunque hay 2 portátiles < 1000€
# → pytest lo detecta. Fix, commit, done.
```

**Fallo de comportamiento del modelo — invisible para tus herramientas:**
```python
user: "¿Qué portátiles tenéis para diseño gráfico?"
agent: "Te recomiendo el MacBook Pro M3 con pantalla Retina..."
# → TechShop NO vende MacBook. El agente lo inventó.
# → No hay error. No hay excepción. pytest pasa.
# → El usuario recibe información falsa con total confianza.
```

> **Este segundo tipo de fallo es el problema central de LLMOps.** El modelo falla con respuestas convincentes pero incorrectas — y tus herramientas clásicas no lo detectan.

*Speaker notes: Este es el slide más importante del bloque. Asegúrate de que entiendan la diferencia. Pregunta directamente: "¿cómo detectarías el segundo fallo con un assert?" La respuesta es que no puedes — o al menos no con un assert clásico. Eso justifica todo lo que viene después.*

---

## Slide 4: ¿Qué es LLMOps?

**LLMOps = las prácticas y herramientas para llevar sistemas basados en LLMs a producción y mantenerlos ahí.**

No es:
- Entrenar modelos (eso es MLOps)
- Solo hacer prompts (eso es prompt engineering)
- DevOps con un LLM encima

Es:
- **Observar** qué hace tu agente en producción (trazas, no solo logs)
- **Evaluar** antes de deployar (con tests que entienden lenguaje)
- **Proteger** input y output (guardrails en tiempo real)
- **Versionar** prompts como código (el prompt es un artefacto)
- **Iterar** con datos reales (feedback loop continuo)

*Speaker notes: Conecta cada punto con el fallo del slide anterior. "Observar" = detectar que el agente inventó un MacBook. "Evaluar" = tener un test que lo atrape antes del deploy. "Proteger" = que si alguien intenta hacer prompt injection, el sistema lo bloquee.*

---

## Slide 5: El Ciclo LLMOps

```
[Develop] → [Evaluate] → [Deploy] → [Observe]
    ↑                                    │
    └──────── [Iterate] ◀───────────────┘

Transversal: GUARDRAILS (protección en tiempo real)
```

| Fase | Pregunta clave | Lo construimos en |
|------|----------------|-------------------|
| **Develop** | ¿El prompt hace lo que quiero? | Día 1 |
| **Evaluate** | ¿Pasa los tests antes de mergear? | Día 2 |
| **Deploy** | ¿Puedo hacer rollback seguro? | Día 2 |
| **Observe** | ¿Qué pasa en producción? | Día 1 |
| **Guardrails** | ¿Qué protejo en tiempo real? | Día 3 |

> Cada fase responde a una pregunta concreta. **El ciclo completo es lo que convierte un prototipo en producto.**

*Speaker notes: Este es el marco organizador de los 3 días. Señálalo con claridad: "todo lo que hagamos encaja en una de estas fases." La observabilidad cierra el ciclo porque los fallos en producción generan nuevos tests.*

---

## Slide 6: Testear un agente no es como testear software

**El output es estocástico y texto libre. Un assert clásico no alcanza.**

```python
# Software clásico — funciona
assert calculate_tax(100) == 21.0

# Agente LLM — esto es insuficiente
response = agent.run("¿Cuánto cuesta el VoltPhone S?")
assert response == "El VoltPhone S cuesta 749€."  # ❌ Nunca va a ser exacto

# Agente LLM — lo que realmente necesitas
assert "749" in response           # ¿contiene el dato correcto?
assert "MacBook" not in response    # ¿no inventa productos que no vendemos?
# ¿el tono es profesional? → eso no lo puede hacer un assert
```

> **Los unit tests no desaparecen** — siguen cubriendo la lógica de tu código. Pero no son suficientes para cubrir el comportamiento del modelo. En el Día 2 veremos cómo añadir esa capa.

*Speaker notes: No entres en detalle sobre tipos de evaluación aquí — eso es contenido de M3. El objetivo es solo que entiendan que hay un gap entre lo que pytest cubre y lo que necesitan. Que se queden con la pregunta, no con la respuesta completa.*

---

## Slide 7: Del notebook a producción

**El camino que construimos en los 3 días:**

```
 Notebook
 (pruebas manuales)
         │
         ▼
 Tests automáticos
 (lógica de código + comportamiento del modelo)
         │
         ▼
 Quality gate en CI
 (si no pasa los tests, no se mergea)
         │
         ▼
 Producción con observabilidad
 (trazas → detectar fallos → nuevos tests)
         │
         └───────────── feedback loop ───┘
```

> Cada capa añade una garantía. **La observabilidad cierra el ciclo:** los fallos en producción se convierten en nuevos test cases.

*Speaker notes: Este diagrama es un mapa de ruta — los alumnos lo verán crecer día a día. No entres en detalles de implementación ahora: el CI gate se construye en el Día 2, los guardrails en el Día 3. Aquí solo importa que vean el destino.*

---

## Slide 8: El agente TechShop — Nuestro caso práctico

**TechShop** = Tienda online de electrónica

El agente tiene:
- 🔍 **search_catalog** — Buscar productos (portátiles, smartphones, auriculares...)
- ❓ **get_faq_answer** — Consultar políticas (envíos, devoluciones, garantías...)

Stack:
- **Strands Agents** (framework de agentes)
- **Amazon Bedrock** (modelo de lenguaje)
- **Langfuse** (observabilidad + prompt management)
- **Python** (todo)

> En los notebooks vais a construir este agente de cero y añadirle cada capa del ciclo LLMOps.

*Speaker notes: Presenta el agente como algo sencillo a propósito. Dos herramientas, un catálogo pequeño, preguntas frecuentes. La complejidad no está en el agente — está en todo lo que le ponemos alrededor para que funcione de forma fiable.*

---

## Slide 9: Roadmap de los 3 días

| Día | Fases del ciclo | Qué construimos |
|-----|-----------------|------------------|
| **1** | **Develop + Observe** | Agente con trazabilidad + Prompt versionado |
| **2** | **Evaluate + Deploy** | Suite de evaluación + CI/CD quality gate |
| **3** | **Guardrails + Iterate** | Protección + Pipeline completo |

**Formato:** Mañanas de teoría → Tardes de notebooks prácticos

> Cada día avanza en el ciclo LLMOps. No saltamos entre fases.

---

## Slide 10: ¿Preguntas antes de empezar?

**Siguiente bloque:** Desarrollo profesional — Observabilidad, prompts y herramientas

**Siguiente práctica:** Notebook 1 — Construir el agente TechShop con instrumentación

