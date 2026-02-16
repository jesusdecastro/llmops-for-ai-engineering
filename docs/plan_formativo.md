# Plan de Formación: LLMOps para GenAI

## Módulo: LLMOps — Operaciones para Aplicaciones de IA Generativa

**Duración:** 3 días (24 horas)
**Formato:** Bloques de 90 minutos, ratio 20/80 teoría-práctica
**Nivel:** Junior developers con base en Python avanzado, primer contacto serio con GenAI
**Stack:** AWS Bedrock (Claude Haiku 4.5) + Langfuse + promptfoo + LLM Guard + GitHub Actions + SAM

---

## Infraestructura necesaria

| Componente | Especificación | Coste estimado (3 días) |
|---|---|---|
| AWS Bedrock | Claude Haiku 4.5 via inference profiles globales, quota increase pre-solicitada | $50–130 |
| Langfuse | Docker Compose en EC2 t3.xlarge (4 vCPU, 16 GiB), 100 GiB gp3 | ~$13–15 |
| Lambda | Function URLs con RESPONSE_STREAM, SAM para IaC | ~$1 |
| GitHub | Organization + Classroom + Actions (OIDC auth con AWS) | $0 (free tier) |
| **Total estimado** | | **$75–200** |

**Pre-requisitos instructor (2 semanas antes):**

- Enviar formulario FTU de Anthropic en Bedrock
- Solicitar quota increase en Service Quotas ("training event, 20 students")
- Configurar IAM Identity Center con 20 usuarios (student01–student20)
- Desplegar Langfuse en EC2 con headless init (proyecto y API keys pre-creados)
- Crear GitHub Org, configurar OIDC provider en AWS, crear template repo
- Configurar AWS Budget ($500 cap) con alertas a 50/75/90/100%
- Forzar `max_tokens: 1024` en todo el código starter

---

## Estructura diaria

| Hora | Actividad |
|---|---|
| 09:00 – 10:30 | Bloque 1 (90 min) |
| 10:30 – 10:45 | Descanso |
| 10:45 – 12:15 | Bloque 2 (90 min) |
| 12:15 – 13:15 | Almuerzo |
| 13:15 – 14:45 | Bloque 3 (90 min) |
| 14:45 – 15:00 | Descanso |
| 15:00 – 16:30 | Bloque 4 (90 min) |
| 16:30 – 17:00 | Wrap-up / Buffer |

---

## Narrativa del módulo

Los 3 días siguen un hilo conductor: construir un asistente de atención al cliente para una empresa ficticia ("TechShop") que vende productos tecnológicos. Los alumnos lo operacionalizan progresivamente: primero lo observan (Día 1), luego lo evalúan y protegen (Día 2), y finalmente lo despliegan con CI/CD profesional (Día 3). Al final del módulo, cada equipo tiene un pipeline completo: código → evals → deploy → observabilidad → mejora.

---

# DÍA 1: Observabilidad y Prompt Management

**Objetivo del día:** Entender que en LLMOps el centro de gravedad no es el modelo (que no controlas) sino cómo lo usas, cómo lo observas y cómo gestionas los prompts como artefactos de software.

---

## Bloque 1.1 — El cambio de paradigma: de MLOps a LLMOps

**09:00 – 10:30 (90 min)**

### Teoría (20 min)

**¿Por qué LLMOps no es MLOps?**

En MLOps clásico, el equipo de ML entrena, versiona y despliega modelos. El flujo central es: datos → entrenamiento → evaluación del modelo → registro → serving → monitoreo de drift. Todo gira alrededor del modelo como artefacto que tú produces y controlas.

En LLMOps, el modelo es un servicio externo consumido via API. No lo entrenas, no lo versionas, no controlas sus actualizaciones. Claude Haiku 4.5 puede cambiar su comportamiento con una actualización del proveedor sin que tú hagas nada. Esto desplaza el centro de gravedad hacia tres ejes nuevos:

1. **El prompt** — Es tu "código" que controla el comportamiento del modelo. Un cambio de 3 palabras puede romper toda tu aplicación.
2. **La evaluación continua** — Sin métricas de training, necesitas formas de medir si tu sistema funciona bien de forma continua, no solo al desplegar.
3. **La observabilidad** — Cada llamada es no determinista. Sin trazas detalladas estás completamente a ciegas en producción.

**Conceptos clave a interiorizar:**

- **No determinismo:** La misma entrada puede producir salidas diferentes. Esto rompe las asunciones de testing tradicional.
- **Latencia variable:** Una llamada a LLM puede tardar 500ms o 15s dependiendo del contexto y la carga.
- **Costes proporcionales al uso:** Cada token cuesta dinero. Un prompt mal diseñado puede multiplicar x10 tu factura.
- **Caja negra:** No puedes debuggear el modelo internamente. Solo puedes observar inputs y outputs.

**El loop de LLMOps:**

```
Observar (Langfuse) → Evaluar (promptfoo) → Mejorar (prompt/config) → Desplegar (CI/CD) → Observar...
```

### Práctica (70 min)

**Ejercicio 1.1.1 — Setup del entorno y primera llamada instrumentada (30 min)**

Objetivo: Que cada alumno tenga su entorno funcional con Bedrock + Langfuse desde el minuto uno.

Pasos guiados:

1. Configurar credenciales AWS via IAM Identity Center (login en portal SSO, copiar temporary credentials).
2. Crear virtualenv con `uv`, instalar `boto3`, `langfuse`.
3. Configurar variables de entorno para Langfuse (public key, secret key, base URL del EC2).
4. Primera llamada a Bedrock via `boto3.client("bedrock-runtime").converse()` con Claude Haiku 4.5.
5. Verificar la llamada en la consola de Langfuse — explorar la traza: input, output, tokens, latencia, coste.

Código starter proporcionado con TODO markers para que completen las partes clave (no copiar-pegar entero).

**Ejercicio 1.1.2 — Exploración del no determinismo (20 min)**

Objetivo: Experimentar visceralmente por qué el testing tradicional no funciona con LLMs.

1. Hacer la misma llamada 10 veces con el mismo prompt.
2. Comparar respuestas: ¿son idénticas? ¿Varían en longitud? ¿En contenido?
3. Intentar escribir un `assert` de pytest que pase para las 10 respuestas.
4. Discusión en grupo: ¿Por qué es esto un problema? ¿Cómo testearías algo así?

**Ejercicio 1.1.3 — Calculadora de costes (20 min)**

Objetivo: Desarrollar intuición sobre la economía de tokens.

1. Calcular el coste de una conversación de 10 turnos con Haiku 4.5 vs Sonnet 4.5.
2. Estimar el coste mensual de un servicio con 10,000 usuarios haciendo 5 consultas/día.
3. Experimentar: ¿Qué pasa con el coste si cambias `max_tokens`? ¿Y si añades system prompt largo?
4. Registrar todas las llamadas en Langfuse y verificar los costes calculados vs los reportados.

---

## Bloque 1.2 — Observabilidad profunda con Langfuse

**10:45 – 12:15 (90 min)**

### Teoría (15 min)

**Anatomía de una traza en Langfuse:**

Langfuse organiza la observabilidad en una jerarquía de tres niveles:

- **Trace:** Representa una ejecución completa end-to-end (ej: una petición de usuario completa).
- **Span:** Un paso lógico dentro de la traza (ej: "recuperar contexto", "validar input").
- **Generation:** Una llamada específica a un LLM dentro de un span (ej: la invocación a Claude).

Esta estructura refleja cómo se construyen las aplicaciones GenAI reales: un usuario envía una pregunta → se busca contexto relevante (span) → se construye el prompt (span) → se llama al modelo (generation) → se valida la respuesta (span) → se devuelve al usuario. Cada paso tiene su propia latencia, posibles errores, y métricas.

**Métricas que importan en producción:**

- **Latencia por step:** ¿Dónde se gasta el tiempo? ¿En la llamada al modelo, en el retrieval, en post-procesamiento?
- **Token usage:** Input vs output tokens. El output suele ser 5x más caro.
- **Coste acumulado:** Por usuario, por funcionalidad, por hora del día.
- **Tasa de errores:** Timeouts, rate limits, respuestas malformadas.
- **Metadata y tags:** Versión del prompt, user_id, tipo de consulta — para filtrar y analizar en la UI.

**El decorador `@observe`:**

Langfuse proporciona un decorador que automatiza la creación de traces y spans. En vez de instrumentar manualmente cada llamada, envuelves funciones y Langfuse captura automáticamente la jerarquía, timing, inputs y outputs.

### Práctica (75 min)

**Ejercicio 1.2.1 — Instrumentar un flujo multi-step (40 min)**

Objetivo: Construir la primera versión del asistente de TechShop con trazabilidad completa.

El flujo tiene 3 pasos:

1. **Clasificar la intención** del usuario (consulta de producto, reclamación, pregunta general) — llamada a LLM.
2. **Generar respuesta** usando el system prompt apropiado según la intención — segunda llamada a LLM.
3. **Validar formato** — verificar que la respuesta es coherente (step de Python puro).

Los alumnos deben:

- Implementar cada paso como una función decorada con `@observe`.
- Capturar metadata relevante: `user_id`, `intent_type`, `session_id`.
- Registrar la usage (tokens in/out) manualmente en el step de generation.
- Ejecutar 15-20 consultas variadas.

Código starter proporcionado con la estructura de funciones, los alumnos completan la instrumentación y la lógica de cada paso.

**Ejercicio 1.2.2 — Análisis en el dashboard de Langfuse (20 min)**

Objetivo: Aprender a leer las trazas y extraer insights operativos.

Con las trazas generadas en el ejercicio anterior:

1. Filtrar por `user_id` para ver las trazas propias.
2. Identificar cuál de los 3 steps consume más tiempo.
3. Calcular el coste medio por consulta.
4. Encontrar una traza donde la respuesta fue mala y analizar qué prompt se envió.
5. Comparar latencias entre consultas de clasificación simples vs complejas.

**Ejercicio 1.2.3 — Scores y feedback en Langfuse (15 min)**

Objetivo: Entender cómo se conecta la observabilidad con la evaluación.

1. Añadir un score manual (1-5) a 5 trazas usando la API de Langfuse.
2. Implementar un auto-score basado en longitud de respuesta (heurística simple).
3. Visualizar la distribución de scores en el dashboard.
4. Discusión: ¿Qué limitaciones tiene el scoring manual? ¿Qué scoring automático sería más útil?

---

## Bloque 1.3 — Prompt Management como ingeniería de software

**13:15 – 14:45 (90 min)**

### Teoría (20 min)

**El prompt es tu artefacto principal. Trátalo como tal.**

En desarrollo de software, nadie hardcodea configuración crítica dentro del código fuente. Usamos archivos de configuración, variables de entorno, feature flags. El prompt de un sistema LLM es la pieza de configuración más crítica que existe — un cambio de una línea puede alterar completamente el comportamiento de tu aplicación. Sin embargo, la mayoría de equipos tienen sus prompts embebidos como strings en el código.

**Prompt-as-config: los principios**

1. **Separar prompt del código:** El prompt vive fuera del código fuente, en un sistema de gestión dedicado.
2. **Versionar cada cambio:** Cada modificación del prompt queda registrada con autor, fecha y razón.
3. **Asociar versión a traza:** En producción, cada respuesta debe estar ligada a la versión exacta del prompt que la generó.
4. **Promover con labels:** Igual que en Git tienes branches, en prompt management tienes labels: `latest`, `staging`, `production`. Un prompt se promueve de un label a otro tras pasar evaluaciones.
5. **Evaluar antes de promover:** Cambiar un prompt sin evaluarlo es como hacer push a main sin tests.

**Anatomía de un buen system prompt de producción:**

Un system prompt profesional no es un párrafo suelto. Tiene una estructura clara:

- **Rol y contexto:** Quién es el asistente, para quién trabaja, cuál es su ámbito.
- **Instrucciones de comportamiento:** Tono, idioma, nivel de formalidad.
- **Restricciones explícitas:** Qué NO debe hacer (inventar datos, dar consejos legales, etc.).
- **Formato de salida:** Estructura esperada de la respuesta (JSON, markdown, texto libre con secciones).
- **Ejemplos (few-shot):** Pares input-output que demuestran el comportamiento deseado.
- **Manejo de edge cases:** Qué hacer cuando no sabe, cuando el usuario es agresivo, cuando la pregunta está fuera de ámbito.

**Langfuse Prompt Management:**

Langfuse incluye un sistema integrado de prompt management que conecta directamente con el tracing. Permite crear prompts con variables (ej: `{{user_query}}`, `{{context}}`), versionar automáticamente cada cambio, asignar labels (`production`, `staging`), y consumir el prompt desde el código via SDK. Cuando un prompt se consume desde producción, la traza queda automáticamente ligada a la versión exacta usada.

### Práctica (70 min)

**Ejercicio 1.3.1 — Migrar prompts a Langfuse (25 min)**

Objetivo: Convertir prompts hardcodeados en prompts gestionados.

1. Crear en Langfuse los prompts para el asistente de TechShop:
   - `techshop-classifier` — El prompt de clasificación de intención.
   - `techshop-responder-product` — Respuesta a consultas de producto.
   - `techshop-responder-complaint` — Respuesta a reclamaciones.
2. Usar variables de Langfuse (`{{user_query}}`, `{{product_catalog}}`) en los templates.
3. Modificar el código del Bloque 1.2 para consumir prompts desde Langfuse SDK en vez de strings hardcoded.
4. Verificar en las trazas que ahora aparece la referencia a la versión del prompt usada.

**Ejercicio 1.3.2 — Iterar un prompt con trazabilidad (25 min)**

Objetivo: Experimentar el workflow de mejora de prompts con versionado.

1. Ejecutar 10 consultas con la versión 1 del prompt `techshop-responder-product`.
2. Identificar un problema (ej: respuestas demasiado largas, tono incorrecto, falta formato).
3. Crear versión 2 del prompt en Langfuse corrigiendo el problema.
4. Ejecutar las mismas 10 consultas con la versión 2.
5. Comparar resultados en Langfuse filtrando por versión de prompt.
6. Promover la versión ganadora al label `production`.

**Ejercicio 1.3.3 — System prompt profesional (20 min)**

Objetivo: Escribir un system prompt de calidad producción para TechShop.

1. Aplicar la estructura vista en teoría: rol, instrucciones, restricciones, formato, ejemplos, edge cases.
2. Incluir al menos 2 few-shot examples.
3. Incluir restricciones explícitas (no inventar productos, no dar precios si no están en catálogo).
4. Peer review entre equipos: cada equipo revisa el prompt de otro equipo y sugiere mejoras.

---

## Bloque 1.4 — Monitorización de costes y patrones operativos

**15:00 – 16:30 (90 min)**

### Teoría (15 min)

**La economía de tokens es un skill operativo.**

A diferencia de APIs tradicionales donde el coste por request es fijo, con LLMs el coste varía drásticamente según el contenido. El mismo endpoint puede costar $0.001 o $0.05 por llamada dependiendo del prompt y la respuesta. Esto introduce un reto operativo nuevo: necesitas monitorizar y optimizar el coste como una métrica de primera clase, al nivel de la latencia y la disponibilidad.

**Factores que multiplican costes sin que te des cuenta:**

- **Context window stuffing:** Meter todo el historial de conversación en cada llamada. 100 turnos × 500 tokens = 50K tokens de input por llamada.
- **System prompts pesados:** Un system prompt de 2000 tokens se paga EN CADA LLAMADA.
- **Output sin límite:** Sin `max_tokens`, el modelo puede generar respuestas de 4000 tokens cuando 200 eran suficientes.
- **Reintentos sin backoff:** Un retry loop agresivo ante rate limits puede multiplicar x3 tu consumo.
- **Modelo incorrecto:** Usar Sonnet para tareas que Haiku resuelve igual de bien cuesta 3-5x más.

**Burndown rate en Bedrock:**

Detalle crítico y poco documentado: para Claude Haiku 4.5, Sonnet 4 y Sonnet 4.5, los output tokens consumen quota a un ratio de 5:1. Es decir, si tu quota es 100K TPM, 20K tokens de output agotan toda la quota. Esto afecta directamente al dimensionamiento de cuota para producción.

**Patrones de optimización:**

- Routing inteligente: clasificar primero con Haiku (barato), escalar a Sonnet solo si es necesario.
- Caching semántico: respuestas similares a preguntas similares sin re-invocar el modelo.
- Streaming: no reduce coste de tokens, pero mejora latencia percibida (time-to-first-token).
- Truncado de contexto: mantener solo los N últimos turnos + resumen de anteriores.

### Práctica (75 min)

**Ejercicio 1.4.1 — Implementar routing de modelos (35 min)**

Objetivo: Construir un patrón de routing que use el modelo más eficiente para cada tarea.

1. Implementar un router que:
   - Clasifica consultas como "simple" o "compleja" usando Haiku (llamada rápida y barata).
   - Envía consultas simples a Haiku para respuesta final.
   - Envía consultas complejas a Sonnet 4.5 (simular con Haiku + flag de metadata para el ejercicio).
2. Instrumentar con Langfuse para que cada traza registre qué modelo se usó y por qué.
3. Calcular el ahorro estimado comparando "todo a Sonnet" vs "routing inteligente".

**Ejercicio 1.4.2 — Optimización de tokens (20 min)**

Objetivo: Reducir el consumo de tokens sin degradar la calidad.

1. Tomar el system prompt de TechShop del ejercicio anterior.
2. Medir tokens del prompt actual (usar tokenizer o estimación).
3. Reducir el system prompt a la mitad de tokens manteniendo las instrucciones clave.
4. Ejecutar las mismas 10 consultas y comparar: ¿perdiste calidad? ¿Cuánto ahorraste?
5. Registrar ambas versiones en Langfuse para comparación.

**Ejercicio 1.4.3 — Dashboard de costes en Langfuse (20 min)**

Objetivo: Construir visibilidad operativa sobre el gasto.

1. Explorar la sección de Analytics de Langfuse.
2. Filtrar por modelo, por versión de prompt, por tipo de consulta.
3. Identificar cuál tipo de consulta es más cara y por qué.
4. Generar un report (screenshot/notas) con recomendaciones de optimización para TechShop.

---

### Wrap-up Día 1 (16:30 – 17:00)

**Recapitulación:**

- LLMOps ≠ MLOps. El prompt y la observabilidad son el centro, no el modelo.
- Langfuse como plataforma de observabilidad: traces, spans, generations, scores.
- Prompt management: versionar, asociar a trazas, promover con labels.
- Economía de tokens: monitorizar y optimizar como una métrica de primera clase.

**Para mañana:** Traer preparadas 3 consultas "trampa" para el asistente de TechShop — preguntas diseñadas para provocar respuestas incorrectas o peligrosas. Se usarán en los ejercicios de evaluación y guardrails.

---

# DÍA 2: Evaluación y Guardrails

**Objetivo del día:** Aprender a medir si tu aplicación LLM funciona bien (evals) y a protegerla contra comportamientos no deseados (guardrails). Pasar de "creo que funciona" a "puedo demostrar que funciona".

---

## Bloque 2.1 — Fundamentos de evaluación para LLMs

**09:00 – 10:30 (90 min)**

### Teoría (20 min)

**¿Por qué no puedes testear LLMs con `assertEqual`?**

En software clásico, un test unitario verifica una salida determinista: `assertEqual(sum(2, 3), 5)`. En aplicaciones LLM, la misma entrada produce salidas diferentes cada vez. Peor aún, múltiples salidas pueden ser "correctas" — hay cientos de formas válidas de responder "¿qué portátil me recomiendas?". Esto no significa que no puedas testear. Significa que necesitas **nuevos tipos de assertions**.

**El espectro de evaluación:**

Las evaluaciones de LLM se organizan en un espectro de automatización y rigor:

| Tipo | Ejemplo | Automatizable | Coste |
|---|---|---|---|
| **Determinista** | `assert "return" in response` | 100% | $0 |
| **Heurística** | Longitud entre 50-500 palabras, formato JSON válido | 100% | $0 |
| **LLM-as-judge** | Un LLM evalúa si la respuesta es útil y precisa | 95% | ~$0.001/eval |
| **Humana** | Un revisor puntúa la calidad | 0% | Alto |

La clave es combinar los cuatro tipos. Las evaluaciones deterministas y heurísticas son tu primera línea de defensa: rápidas, baratas y fiables. LLM-as-judge cubre la calidad subjetiva a escala. La evaluación humana calibra y valida los jueces automáticos.

**LLM-as-judge: el patrón dominante**

La idea es usar un LLM más potente (o el mismo) para evaluar las salidas de tu aplicación. Funciona sorprendentemente bien: la concordancia entre evaluadores LLM y evaluadores humanos ronda el 80%, similar a la concordancia entre dos humanos.

El patrón básico:

```
Input: [pregunta del usuario]
Output: [respuesta de tu sistema]
Rubric: "Evalúa si la respuesta es precisa, relevante y profesional. Score 1-5."
→ Judge LLM devuelve score + justificación
```

Claves para que funcione: rúbricas explícitas con criterios concretos (no "¿es buena?"), chain-of-thought en el judge prompt (que explique su razonamiento antes de dar el score), y calibración contra evaluaciones humanas para detectar sesgos del juez.

**Golden datasets: la base de todo**

Un golden dataset es un conjunto curado de pares input-output que define "cómo debe comportarse tu sistema". Es tu ground truth para evaluación. Debe incluir: happy paths (las consultas típicas), edge cases (preguntas ambiguas, fuera de ámbito), adversarial inputs (intentos de prompt injection, preguntas trampa) y fallos reales de producción.

Empieza con 50-100 ejemplos mínimo. Lo importante no es el tamaño inicial sino mantenerlo vivo: cada fallo de producción se convierte en un nuevo caso de test.

### Práctica (70 min)

**Ejercicio 2.1.1 — Primer eval con promptfoo (35 min)**

Objetivo: Configurar promptfoo y ejecutar la primera evaluación automatizada.

1. Instalar promptfoo: `npx promptfoo@latest init`.
2. Crear `promptfooconfig.yaml` con:
   - El prompt de TechShop como provider (Bedrock Haiku 4.5).
   - 5 test cases del asistente (consultas de producto, reclamaciones, fuera de ámbito).
   - Assertions deterministas: `contains`, `not-contains`, `is-json`.
   - Una assertion `llm-rubric` con rúbrica de calidad.
3. Ejecutar: `npx promptfoo eval`.
4. Explorar la UI de resultados: `npx promptfoo view`.
5. Interpretar: ¿Qué tests pasaron? ¿Cuáles fallaron? ¿Por qué?

Configuración YAML starter proporcionada con TODOs.

**Ejercicio 2.1.2 — Construir golden dataset de TechShop (20 min)**

Objetivo: Crear el golden dataset que se usará todo el día.

1. Cada equipo aporta las 3 "preguntas trampa" que prepararon ayer.
2. Consolidar en un dataset compartido con columnas: `query`, `expected_behavior`, `category`.
3. Categorías: `product_query`, `complaint`, `out_of_scope`, `adversarial`, `edge_case`.
4. Mínimo 25 casos entre todos los equipos.
5. Exportar como CSV para usar en promptfoo y en ejercicios posteriores.

**Ejercicio 2.1.3 — Comparar versiones de prompt (15 min)**

Objetivo: Usar evals para tomar decisiones de prompt basadas en datos.

1. Crear 2 versiones del prompt de TechShop en `promptfooconfig.yaml` (ej: conciso vs detallado).
2. Ejecutar ambas contra el golden dataset.
3. Comparar en la UI de promptfoo: matriz de resultados versión × test case.
4. Decidir cuál es mejor y argumentar con datos.

---

## Bloque 2.2 — Evaluación avanzada: LLM-as-judge y métricas custom

**10:45 – 12:15 (90 min)**

### Teoría (15 min)

**Diseñar rúbricas efectivas para LLM-as-judge:**

La calidad de tu evaluación automática depende directamente de la calidad de tu rúbrica. Una rúbrica vaga ("¿es buena la respuesta?") produce scores inconsistentes. Una rúbrica precisa con criterios observables produce evaluaciones que se correlacionan con el juicio humano.

Estructura de una rúbrica efectiva:

```
Criterio: Precisión factual
5 - Todos los hechos son correctos y verificables.
4 - Los hechos principales son correctos, errores menores en detalles.
3 - La mayoría de hechos son correctos pero hay una imprecisión significativa.
2 - Contiene errores factuales que podrían confundir al usuario.
1 - La respuesta contiene información inventada o claramente incorrecta.
```

Cada nivel debe ser distinguible del anterior. Si un evaluador humano no puede decidir entre un 3 y un 4 la mitad de las veces, tu rúbrica necesita más trabajo.

**Métricas compuestas:**

En producción, rara vez basta un único score. Para TechShop, querrías medir:

- **Precisión factual:** ¿Los datos sobre productos son correctos?
- **Relevancia:** ¿Responde a lo que preguntó el usuario?
- **Completitud:** ¿Cubre todos los aspectos de la pregunta?
- **Tono profesional:** ¿Mantiene el tono de marca?
- **Seguridad:** ¿Evita promesas que la empresa no puede cumplir?

Cada métrica puede ponderarse según prioridades del negocio. Si la precisión factual es crítica (ej: precios), tendrá peso alto y threshold estricto.

**Evaluación offline vs online:**

- **Offline (pre-deploy):** Ejecutar evals contra golden dataset antes de desplegar. Es tu gate de calidad.
- **Online (post-deploy):** Evaluar continuamente las respuestas en producción usando sampling + LLM-as-judge. Alimenta el golden dataset con nuevos fallos.

### Práctica (75 min)

**Ejercicio 2.2.1 — Rúbricas multi-dimensión (30 min)**

Objetivo: Implementar evaluación multi-métrica en promptfoo.

1. Definir 3 rúbricas para TechShop: `factual_accuracy`, `relevance`, `brand_tone`.
2. Implementar cada rúbrica como un assert `llm-rubric` con escala 1-5 y criterios detallados.
3. Añadir thresholds: accuracy ≥ 4, relevance ≥ 3, tone ≥ 3.
4. Ejecutar contra el golden dataset.
5. Analizar: ¿Qué dimensión falla más? ¿Qué tipos de consulta causan más problemas?

**Ejercicio 2.2.2 — Calibración humana del juez (25 min)**

Objetivo: Verificar que tu LLM-as-judge concuerda con el juicio humano.

1. Tomar 10 respuestas del golden dataset ya evaluadas por promptfoo.
2. Cada alumno evalúa manualmente las mismas 10 respuestas con las mismas rúbricas (1-5).
3. Comparar scores humanos vs LLM-as-judge.
4. Calcular concordancia simple: ¿en cuántas coinciden (±1 punto)?
5. Discusión: ¿Dónde falla el juez? ¿Cómo mejorarías la rúbrica?

**Ejercicio 2.2.3 — Regression testing de prompts (20 min)**

Objetivo: Implementar el patrón de regression testing para cambios de prompt.

1. Guardar resultados actuales como "baseline" (captura o exportación de promptfoo).
2. Hacer un cambio al prompt de TechShop (ej: añadir restricción nueva).
3. Re-ejecutar evals.
4. Comparar: ¿El cambio mejoró la métrica objetivo? ¿Rompió algún caso que antes pasaba?
5. Tomar decisión: ¿deploy o rollback?

---

## Bloque 2.3 — Guardrails: protegiendo tu aplicación

**13:15 – 14:45 (90 min)**

### Teoría (20 min)

**¿Por qué necesitas guardrails?**

Un LLM hará su mejor esfuerzo por ser útil, lo cual es un problema. Si un usuario le pide a tu asistente de TechShop información médica, el modelo intentará responder. Si le piden que ignore sus instrucciones, intentará complacerlo. Si envían PII en la consulta, el modelo lo procesará sin cuestionar. Los guardrails son la capa de defensa que tú controlas, independiente del modelo.

**Dos capas de defensa:**

1. **Input guardrails (pre-LLM):** Validan y filtran la entrada ANTES de enviarla al modelo.
   - Detección de prompt injection.
   - Detección y redacción de PII (emails, teléfonos, DNIs).
   - Filtro de contenido tóxico.
   - Detección de secrets (API keys, passwords).
   - Validación de longitud y formato.

2. **Output guardrails (post-LLM):** Validan la respuesta DESPUÉS de recibirla del modelo.
   - Validación de formato (¿es JSON válido cuando se esperaba JSON?).
   - Detección de alucinaciones (¿menciona productos que no existen?).
   - Filtro de contenido no deseado en la respuesta.
   - Verificación de adherencia al scope (¿respondió sobre temas fuera de su ámbito?).
   - Detección de información inventada (URLs, referencias bibliográficas).

**LLM Guard — la herramienta del taller:**

LLM Guard es open source (MIT), se instala con `pip install llm-guard` y ejecuta validaciones localmente sin llamadas API adicionales. Ofrece 15 scanners de input y 20 de output. Para el taller cubriremos los más relevantes:

- Input: `PromptInjection`, `Anonymize` (PII), `Toxicity`, `Secrets`.
- Output: `NoRefusal`, `Relevance`, `FactualConsistency`, `BanTopics`.

El patrón es simple: `scan_prompt()` antes del LLM, `scan_output()` después. Cada scanner devuelve un score de riesgo y opcionalmente modifica el texto (ej: redactando PII).

**Structured outputs como guardrail:**

Forzar al modelo a responder en un formato estructurado (JSON con schema Pydantic) es uno de los guardrails más efectivos. Si esperas `{"answer": str, "confidence": float, "sources": list}` y el modelo responde con texto libre, sabes inmediatamente que algo salió mal. Bedrock soporta esto nativamente con el campo `toolChoice` en la API.

### Práctica (70 min)

**Ejercicio 2.3.1 — Input guardrails con LLM Guard (30 min)**

Objetivo: Proteger el asistente de TechShop contra inputs maliciosos.

1. Instalar LLM Guard: `pip install llm-guard`.
2. Implementar pipeline de input scanning:
   - `PromptInjection` scanner para detectar intentos de jailbreak.
   - `Anonymize` scanner para redactar PII.
   - `Toxicity` scanner para contenido ofensivo.
3. Probar con las "preguntas trampa" del golden dataset.
4. Definir la estrategia: ¿bloquear la request? ¿Redactar y continuar? ¿Log y continuar?
5. Instrumentar con Langfuse para registrar las decisiones de los guardrails como spans.

**Ejercicio 2.3.2 — Output guardrails y structured outputs (25 min)**

Objetivo: Validar las respuestas del modelo antes de entregarlas al usuario.

1. Definir un modelo Pydantic para la respuesta de TechShop:

   ```python
   class TechShopResponse(BaseModel):
       answer: str
       confidence: Literal["high", "medium", "low"]
       category: Literal["product", "complaint", "general", "out_of_scope"]
       requires_human: bool
   ```

2. Implementar la llamada a Bedrock forzando structured output.
3. Añadir output scanning con LLM Guard: `Relevance`, `BanTopics`.
4. Implementar fallback: si la respuesta no pasa validación, responder con mensaje genérico + escalar a humano.
5. Registrar en Langfuse: response original, validación pass/fail, response final.

**Ejercicio 2.3.3 — Red teaming entre equipos (15 min)**

Objetivo: Intentar romper los guardrails del equipo contrario.

1. Cada equipo intenta romper el asistente de otro equipo usando prompt injection, PII, peticiones fuera de ámbito.
2. Registrar qué ataques funcionaron y cuáles fueron bloqueados.
3. Compartir resultados y discutir: ¿qué guardrails faltan?

---

## Bloque 2.4 — Bedrock Guardrails y patrones avanzados de protección

**15:00 – 16:30 (90 min)**

### Teoría (15 min)

**AWS Bedrock Guardrails — la opción managed:**

Además de guardrails a nivel de aplicación con LLM Guard (que ejecutas tú), Bedrock ofrece un servicio managed de guardrails que se aplica directamente sobre las llamadas al modelo. Las ventajas: no tienes que mantener la infra, se ejecuta en la llamada al modelo (no necesitas código extra), y se actualiza automáticamente. Las desventajas: menos control fino, dependencia del proveedor, coste adicional.

Bedrock Guardrails cubre:

- **Content filters:** Bloqueando o filtrando contenido por categorías (hate, violence, sexual, misconduct) con niveles configurables de severidad.
- **Denied topics:** Definir temas que el modelo NO debe abordar (ej: "no dar asesoría legal").
- **PII detection:** Redactar o bloquear información personal identificable.
- **Contextual grounding check:** Verificar que la respuesta está fundamentada en el contexto proporcionado (clave para RAG).
- **Word filters:** Bloquear palabras o frases específicas en input u output.

Se configura como un "guardrail" en la consola de Bedrock y se asocia a las llamadas via `guardrailIdentifier` y `guardrailVersion`.

**Cuándo usar qué:**

| Escenario | LLM Guard (app-level) | Bedrock Guardrails (managed) |
|---|---|---|
| Prototipo / startup | ✅ Open source, gratis, flexible | ❌ Coste adicional, overkill |
| Producción enterprise | ✅ Como primera capa | ✅ Como segunda capa |
| Compliance estricto | Complementario | ✅ Trazabilidad managed |
| Personalización fina | ✅ Scanners custom | ❌ Categorías predefinidas |

**Patrón defense-in-depth:**

En producción, las empresas aplican guardrails en múltiples capas:

1. Input validation (app level) → LLM Guard, Pydantic.
2. Model-level guardrails → Bedrock Guardrails.
3. Output validation (app level) → LLM Guard, Pydantic, business rules.
4. Monitoring → Langfuse scores para detectar bypasses.

### Práctica (75 min)

**Ejercicio 2.4.1 — Configurar Bedrock Guardrails (25 min)**

Objetivo: Crear y aplicar un guardrail managed de Bedrock.

1. (Demo del instructor si las policies no permiten creación por alumnos).
2. Configurar un guardrail con:
   - Content filter: bloquear hate speech y misconduct.
   - Denied topic: "No proporcionar asesoría legal o médica".
   - PII: redactar emails y teléfonos.
3. Asociar el guardrail a las llamadas del asistente de TechShop.
4. Probar con inputs que deben ser bloqueados.
5. Comparar el comportamiento con los guardrails de LLM Guard: ¿qué detecta cada uno?

**Ejercicio 2.4.2 — Patrón retry con fallback (25 min)**

Objetivo: Implementar manejo robusto de errores para producción.

1. Implementar el patrón:
   - Si la respuesta no pasa guardrails → reintentar 1 vez con prompt más restrictivo.
   - Si el segundo intento falla → devolver mensaje genérico + flag `requires_human: true`.
   - Si hay timeout o error de API → exponential backoff con 3 reintentos.
   - Si hay rate limit → queue la request o devolver "servicio ocupado".
2. Instrumentar cada path en Langfuse con metadata: `retry_count`, `fallback_used`, `error_type`.
3. Probar con inputs que provocan cada path.

**Ejercicio 2.4.3 — Integrar todo: pipeline completo del Día 2 (25 min)**

Objetivo: Ensamblar todos los componentes del día en un flujo coherente.

1. El asistente de TechShop ahora debe tener:
   - Input guardrails (LLM Guard): prompt injection, PII, toxicity.
   - Prompt gestionado desde Langfuse (del Día 1).
   - Llamada a Bedrock con guardrail managed.
   - Output validación: structured output + LLM Guard.
   - Fallback con retry.
   - Trazabilidad completa en Langfuse.
2. Ejecutar el golden dataset completo contra este pipeline.
3. Comparar métricas con las del Bloque 2.1 (antes de guardrails): ¿mejoró la seguridad? ¿Empeoró la latencia? ¿Cuánto coste añadieron los guardrails?

---

### Wrap-up Día 2 (16:30 – 17:00)

**Recapitulación:**

- Evals: promptfoo con assertions deterministas + LLM-as-judge + golden datasets.
- Rúbricas multi-dimensión y calibración humana.
- Guardrails: LLM Guard (app-level) + Bedrock Guardrails (managed) = defense-in-depth.
- Structured outputs como guardrail.
- Retry + fallback patterns para robustez.

**Para mañana:** Asegurar que tienen Git configurado y acceso al GitHub Org de la clase. Mañana desplegamos todo a producción.

---

# DÍA 3: Despliegue, CI/CD y proyecto integrador

**Objetivo del día:** Llevar el asistente de TechShop a producción con infraestructura como código, pipeline de CI/CD con evals automatizados, y un proyecto final que demuestre el loop completo de LLMOps.

---

## Bloque 3.1 — Despliegue serverless con Lambda y SAM

**09:00 – 10:30 (90 min)**

### Teoría (20 min)

**¿Por qué Lambda para aplicaciones LLM?**

Las aplicaciones GenAI que consumen modelos via API son candidatas perfectas para serverless. No sirves el modelo (Bedrock lo hace), así que tu función solo necesita: recibir request → construir prompt → llamar API → procesar respuesta → devolver. Esto es exactamente lo que Lambda hace bien.

Ventajas para el contexto de estos alumnos:

- **Zero infraestructura:** No gestionas servidores, containers, ni orchestrators.
- **Escalado automático:** De 0 a miles de requests sin configuración.
- **Pay-per-use real:** Solo pagas por el tiempo de ejecución, no por tiempo idle.
- **Integración nativa con Bedrock:** IAM roles, no API keys. La Lambda asume un role que tiene permiso de invocar Bedrock.

**Lambda Function URLs vs API Gateway:**

Para aplicaciones LLM con streaming, Lambda Function URLs son la mejor opción. API Gateway HTTP API no soporta streaming nativo. API Gateway REST API lo soporta desde finales de 2025 pero añade complejidad y coste. Function URLs son gratis, nativamente soportan `RESPONSE_STREAM`, y se configuran en una línea de SAM.

**SAM (Serverless Application Model):**

SAM es la extensión de CloudFormation para serverless. Un archivo `template.yaml` declara tu función Lambda, sus permisos, su URL, y sus variables de entorno. Luego `sam build && sam deploy` lo despliega todo. Para junior developers, SAM es más accesible que CDK (que requiere pensar en constructos, herencia, y programar la infra).

**Consideraciones para LLMs en Lambda:**

- **Timeout:** Hasta 15 minutos, pero para una llamada a Bedrock 60-300 segundos suele bastar.
- **Memory:** 256-512 MB es suficiente para llamadas API. Más memoria = más CPU = cold start más rápido.
- **Cold starts:** Boto3 está incluido en el runtime de Python. Para dependencias extra, usa Lambda Layers.
- **Streaming:** Requiere `InvokeMode: RESPONSE_STREAM` en la Function URL. En Python necesitas Lambda Web Adapter o usar Node.js.

### Práctica (70 min)

**Ejercicio 3.1.1 — Primera Lambda con SAM (35 min)**

Objetivo: Desplegar el asistente de TechShop como Lambda con Function URL.

1. Partir del template SAM proporcionado (con TODOs).
2. Completar:
   - Handler que recibe consulta, construye prompt, llama Bedrock, devuelve respuesta.
   - IAM policy que permite solo `bedrock:InvokeModel` para Haiku 4.5.
   - Function URL con `AuthType: NONE` (para el taller; en producción se usaría IAM auth).
   - Variables de entorno: model ID, Langfuse keys, max_tokens.
3. Build y deploy: `sam build && sam deploy --guided`.
4. Probar la URL con `curl` y verificar la traza en Langfuse.
5. Verificar que el stack aparece en CloudFormation.

El stack name incluye el nombre del alumno: `techshop-{student-name}` para aislamiento.

**Ejercicio 3.1.2 — Añadir streaming (20 min)**

Objetivo: Implementar streaming de respuestas para mejor UX.

1. Modificar el handler para usar `InvokeModelWithResponseStream`.
2. Configurar Function URL con `InvokeMode: RESPONSE_STREAM`.
3. Para Python: añadir Lambda Web Adapter como layer (o implementar con Node.js handler alternativo proporcionado).
4. Probar con `curl --no-buffer` para ver el streaming en terminal.
5. Medir time-to-first-token vs respuesta completa sin streaming.

**Ejercicio 3.1.3 — Integrar guardrails en Lambda (15 min)**

Objetivo: Desplegar el pipeline completo del Día 2 en Lambda.

1. Añadir las dependencias de guardrails como Lambda Layer o en requirements.txt.
2. Integrar el flujo: input validation → Bedrock call → output validation → response.
3. Instrumentar con Langfuse (el SDK se inicializa al importar, no requiere setup especial en Lambda).
4. Re-deploy y verificar que las trazas aparecen con todos los spans.

---

## Bloque 3.2 — CI/CD con GitHub Actions y evals automatizados

**10:45 – 12:15 (90 min)**

### Teoría (20 min)

**El pipeline de CI/CD para aplicaciones LLM:**

Un pipeline de CI/CD para una aplicación LLM tiene todo lo que esperarías de un pipeline normal (lint, tests unitarios, build, deploy) más un paso nuevo y crítico: **evals automatizados**.

El flujo es:

```
Push → Lint + Type check → Unit tests (lógica de app) →
LLM Evals (promptfoo contra golden dataset) → Build → Deploy
```

Si los evals fallan (algún caso del golden dataset no pasa los thresholds), el deploy se bloquea. Esto convierte el golden dataset en el equivalente funcional de un test suite para la capa LLM.

**OIDC: autenticación sin secrets**

El patrón clásico de guardar `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` como GitHub Secrets tiene problemas: las keys son permanentes, se pueden filtrar, y rotar es manual. OIDC (OpenID Connect) es el estándar actual.

El flujo OIDC: GitHub Actions solicita un token JWT temporal que identifica el repo y la ejecución → AWS verifica el JWT contra el OIDC provider configurado → AWS devuelve credenciales temporales (15 min a 1 hora) → el workflow usa esas credenciales. No hay secrets permanentes. Las credenciales expiran solas. La trust policy del role en AWS especifica exactamente qué repos pueden asumir qué permisos.

**promptfoo en CI:**

promptfoo ofrece una GitHub Action oficial (`promptfoo/promptfoo-action`) que ejecuta evals y publica los resultados como comentario en el PR. Esto permite que el review del código incluya revisar el impacto del cambio en la calidad de las respuestas del LLM. Si cambias un prompt y 3 test cases que antes pasaban ahora fallan, lo ves directamente en el PR.

El exit code 100 de promptfoo (algunos tests fallaron) se puede configurar para bloquear el merge, igual que un test unitario que falla.

### Práctica (70 min)

**Ejercicio 3.2.1 — Configurar OIDC y primer workflow (30 min)**

Objetivo: Desplegar desde GitHub Actions con autenticación OIDC.

1. (El instructor pre-configura el OIDC provider en AWS y el role con trust policy para el org).
2. En el repo del equipo, crear `.github/workflows/deploy.yml`:
   - Trigger: push a `main`.
   - Job `deploy`: checkout → configure-aws-credentials (con OIDC) → sam build → sam deploy.
3. Hacer push y verificar que el workflow ejecuta y despliega.
4. Verificar en CloudFormation que el stack se actualizó.

Workflow starter proporcionado con TODOs para completar.

**Ejercicio 3.2.2 — Añadir lint + tests al pipeline (15 min)**

Objetivo: Completar el pipeline con quality gates estándar.

1. Añadir job `quality` que ejecuta:
   - `ruff check` (linting).
   - `ruff format --check` (formatting).
   - `pytest` (tests unitarios de la lógica de app, no del LLM).
2. Configurar `deploy` con `needs: [quality]`.
3. Hacer push con un error de lint → verificar que el pipeline falla y no despliega.
4. Corregir y re-push → verificar deploy exitoso.

**Ejercicio 3.2.3 — Integrar evals en el pipeline (25 min)**

Objetivo: Añadir el gate de evals LLM al CI/CD.

1. Añadir el golden dataset al repo como `evals/golden-dataset.csv`.
2. Añadir `promptfooconfig.yaml` al repo con los evals del Día 2.
3. Añadir job `eval` usando `promptfoo/promptfoo-action`:
   - Ejecuta contra el golden dataset.
   - Publica resultados como comentario en PR.
4. Configurar `deploy` con `needs: [quality, eval]`.
5. Abrir un PR que modifique un prompt → verificar que los resultados de eval aparecen en el PR.
6. Si los evals pasan → merge → deploy automático.

---

## Bloque 3.3 — Proyecto integrador (parte 1): construcción

**13:15 – 14:45 (90 min)**

### Brief del proyecto (10 min)

**Escenario:** La empresa TechShop quiere lanzar una nueva funcionalidad para su asistente: **recomendaciones personalizadas de productos**. El usuario describe qué busca y el asistente recomienda 1-3 productos del catálogo con justificación.

**Requisitos:**

Cada equipo debe entregar un sistema funcional que incluya:

1. **Prompt versionado en Langfuse** para la funcionalidad de recomendación.
2. **Guardrails** de input y output (mínimo: prompt injection + structured output validation).
3. **Lambda desplegada** via SAM con Function URL.
4. **Golden dataset** con al menos 15 test cases para la funcionalidad.
5. **Pipeline CI/CD** en GitHub Actions: lint → tests → evals → deploy.
6. **Trazabilidad completa** en Langfuse: cada request trazada con prompt version, guardrail decisions, latencia, coste.

**Catálogo de TechShop proporcionado:** 20 productos con nombre, categoría, precio, especificaciones y descripción. Se incluye como JSON en el repo template.

**Evaluación:**

| Criterio | Peso |
|---|---|
| Calidad del prompt (estructura, restricciones, few-shot) | 15% |
| Guardrails funcionales (input + output) | 15% |
| Golden dataset (cobertura: happy, edge, adversarial) | 15% |
| Pipeline CI/CD completo y funcional | 20% |
| Trazabilidad en Langfuse (traces, scores, prompt versioning) | 15% |
| Calidad del código (limpieza, estructura, typing) | 10% |
| Demo y argumentación de decisiones | 10% |

### Trabajo de equipo (80 min)

Los equipos trabajan autónomamente. El instructor rota entre equipos resolviendo bloqueos.

**Checkpoints sugeridos:**

- Min 0-20: Diseño del prompt + golden dataset (dividir trabajo en el equipo).
- Min 20-50: Implementación de la Lambda + guardrails.
- Min 50-70: Configurar CI/CD + evals.
- Min 70-80: Primera iteración completa: push → eval → deploy → verificar en Langfuse.

---

## Bloque 3.4 — Proyecto integrador (parte 2): iteración y demo

**15:00 – 16:30 (90 min)**

### Iteración y mejora (50 min)

1. **Analizar resultados de evals:** ¿Qué tests fallaron? ¿Qué cambios de prompt los arreglan?
2. **Iterar prompt en Langfuse:** Crear versión 2, re-evaluar, comparar con versión 1.
3. **Verificar en producción:** Hacer llamadas a la Lambda desplegada, ver trazas en Langfuse.
4. **Refinar guardrails:** Si el red teaming del Día 2 reveló vulnerabilidades, añadir scanners.
5. **Pulir pipeline:** Asegurar que el workflow completo funciona de push a deploy.

### Demos de equipos (30 min)

Cada equipo tiene 5-7 minutos para presentar:

1. **Arquitectura:** Diagrama rápido del flujo (input → guardrails → LLM → validation → output).
2. **Demo en vivo:** Una consulta real al asistente desplegado.
3. **Trazabilidad:** Mostrar la traza de esa consulta en Langfuse.
4. **Pipeline:** Mostrar un PR con resultados de eval.
5. **Decisión argumentada:** ¿Qué cambio de prompt hicieron entre versión 1 y 2 y por qué?

### Retrospectiva del módulo (10 min)

Discusión guiada:

- ¿Qué fue lo más sorprendente del módulo?
- ¿Qué harían diferente ahora si empezaran desde cero?
- ¿Qué parte se llevan como más útil para su trabajo real?
- ¿Qué queda pendiente de aprender? (Conexión con módulos de RAG y Agentic.)

---

### Wrap-up Día 3 y cierre del módulo (16:30 – 17:00)

**Recapitulación del módulo completo:**

| Día | Tema central | Herramientas | Skill adquirido |
|---|---|---|---|
| 1 | Observabilidad + Prompts | Langfuse, Bedrock | "Puedo VER lo que hace mi sistema LLM" |
| 2 | Evaluación + Guardrails | promptfoo, LLM Guard, Bedrock Guardrails | "Puedo MEDIR y PROTEGER mi sistema" |
| 3 | Deploy + CI/CD | Lambda, SAM, GitHub Actions | "Puedo DESPLEGAR y MANTENER mi sistema" |

**El loop de LLMOps que han interiorizado:**

```
Código → Push → Lint → Tests → Evals (promptfoo) →
Deploy (SAM/Lambda) → Producción → Observar (Langfuse) →
Detectar problemas → Mejorar prompt → Código → Push → ...
```

**Conexión con próximos módulos:**

- **RAG:** La observabilidad de Langfuse se extiende naturalmente a tracing de retrieval + generation. Las evals de RAG usan RAGAS (faithfulness, relevancy).
- **Agentic:** El tracing de Langfuse captura tool calls y loops de razonamiento. Los guardrails se aplican por step del agente.
- **AWS avanzado:** Lo que hoy desplegaron con SAM se puede escalar con Step Functions para orquestación, SQS para async, y DynamoDB para estado.

---

## Resumen de herramientas del módulo

| Herramienta | Propósito | Licencia | Instalación |
|---|---|---|---|
| **Langfuse** | Observabilidad + prompt management | MIT | Docker Compose en EC2 |
| **promptfoo** | Evaluación y testing de LLMs | MIT | `npx promptfoo@latest` |
| **LLM Guard** | Guardrails open source | MIT | `pip install llm-guard` |
| **AWS Bedrock** | Acceso a modelos (Claude) | Managed | Console + boto3 |
| **Bedrock Guardrails** | Guardrails managed | Managed | Console + API |
| **AWS SAM** | IaC para serverless | Open source | `pip install aws-sam-cli` |
| **GitHub Actions** | CI/CD | Free tier | `.github/workflows/` |

---

## Material a preparar por el instructor

### Código starter / templates

1. **Repo template** con estructura:
   ```
   techshop-assistant/
   ├── src/
   │   ├── handler.py          # Lambda handler con TODOs
   │   ├── guardrails.py       # Pipeline de guardrails con TODOs
   │   ├── bedrock_client.py   # Wrapper de Bedrock con Langfuse
   │   └── models.py           # Pydantic models para structured output
   ├── evals/
   │   ├── promptfooconfig.yaml  # Config de evals con TODOs
   │   └── golden-dataset.csv    # Vacío, se construye en clase
   ├── data/
   │   └── catalog.json          # Catálogo de productos TechShop
   ├── template.yaml              # SAM template con TODOs
   ├── .github/
   │   └── workflows/
   │       └── deploy.yml         # CI/CD workflow con TODOs
   ├── pyproject.toml
   └── README.md
   ```

2. **Notebook de setup** para el Bloque 1.1: verificación de credenciales, primera llamada a Bedrock, primera traza en Langfuse.

3. **Catálogo de TechShop** (catalog.json): 20 productos con datos suficientes para ejercicios de recomendación.

4. **Cheat sheets** (una página cada uno):
   - API de Bedrock `converse()` y `converse_stream()`.
   - Langfuse SDK: `@observe`, `get_client()`, scoring.
   - promptfoo: assertions disponibles, config YAML.
   - LLM Guard: scanners principales, input/output.
   - SAM template: estructura básica, Function URL, policies.
   - GitHub Actions: sintaxis YAML, OIDC config.