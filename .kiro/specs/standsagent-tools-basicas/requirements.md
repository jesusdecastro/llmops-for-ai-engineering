# Requisitos de Especificación: TechShop Agent (Strands Agents)

## 1) Objetivo de negocio
TechShop Agent es el artefacto base del módulo de LLMOps (3 días, 24h). Debe atender consultas de clientes sobre productos y políticas de tienda de forma consistente, segura y trazable.
El objetivo principal es proporcionar a los alumnos un agente funcional con limitaciones deliberadas y controladas que generen fallos observables, medibles y mejorables con prácticas de LLMOps.
La solución debe permitir escalamiento a humano cuando el agente no tenga suficiente certeza o detecte riesgo.
El resultado esperado del MVP es un agente operativo que los alumnos instrumenten, evalúen, protejan y desplieguen sin modificar su lógica core.

## 2) Alcance (in-scope)
- [MVP] Resolver consultas de catálogo con `search_catalog` (keyword matching sobre JSON local con productos inventados).
- [MVP] Resolver consultas de políticas de tienda con `get_faq_answer` (keyword matching sobre JSON local de FAQs).
- [MVP] Devolver respuestas estructuradas con `answer`, `confidence`, `category` y `requires_human`.
- [MVP] Generar trazas ricas via OpenTelemetry para Langfuse (agent spans, cycle spans, LLM spans, tool spans).
- [MVP] Consumir system prompt desde Langfuse Prompt Management (separado del código, versionado con labels).
- [MVP] Soportar fallback seguro cuando una tool falle o no devuelva resultados.
- [MVP] Funcionar localmente por alumno con dependencias mínimas (`strands-agents[otel]`, credenciales AWS, env vars Langfuse).
- [MVP] Definir `AgentConfig` como clase basada en Pydantic (`BaseModel`) con validación declarativa de configuración obligatoria.
- [MVP] Utilizar `uv` para la gestión de entornos, sincronización de dependencias y ejecución de comandos de desarrollo.
- [MVP] Configurar empaquetado Python con backend `hatchling` en `pyproject.toml` para build/install reproducible del paquete.
- [FUTURO] Evolucionar tools v1 (keyword matching) a v2 (embeddings + FAISS in-memory) como puente al módulo de RAG.
- [FUTURO] Añadir memoria conversacional por sesión.
- [FUTURO] Desplegar como Lambda con SAM y Function URL (ejercicio Día 3 del módulo).

## 3) No-alcance (out-of-scope)
- [MVP] Consulta de estado de pedidos (requiere mock transaccional, menor valor didáctico para LLMOps que FAQs).
- [MVP] Procesamiento de pagos, devoluciones o cambios de pedido.
- [MVP] Integración con CRM corporativo, billing o sistemas externos reales.
- [MVP] Soporte multilingüe distinto de español.
- [MVP] Guardrails de entrada/salida (los implementan los alumnos en el Día 2 del módulo).
- [MVP] Interfaz de usuario (los alumnos interactúan via script Python o curl contra Lambda).
- [FUTURO] Personalización avanzada por perfil de cliente o segmentación dinámica.
- [FUTURO] Escalación asistida con creación automática de ticket.

## 4) Supuestos (funcionales/técnicos)
- [MVP] El catálogo es un JSON estático local con 15-20 productos inventados (nombres ficticios para evitar conocimiento del modelo via training data).
- [MVP] Las FAQs son un JSON estático local con 10-12 preguntas redactadas con vocabulario específico para provocar fallos de keyword matching con sinónimos.
- [MVP] Las tools v1 usan keyword matching puro (`str.lower()` + `in`). Las limitaciones son deliberadas, documentadas y constituyen el motor de aprendizaje del módulo.
- [MVP] El modelo es Claude Haiku 4.5 via AWS Bedrock (inference profiles globales: `us.anthropic.*`).
- [MVP] El entorno dispone de credenciales AWS (IAM Identity Center) y variables de entorno de Langfuse (OTEL endpoint, auth).
- [MVP] El entorno local de ejecución y desarrollo se gestiona con `uv` (incluyendo instalación de dependencias y ejecución de tests/checks).
- [MVP] `AgentConfig` centraliza configuración en una clase Pydantic con validaciones explícitas para campos críticos (Langfuse, OTEL y prompt management).
- [MVP] El proyecto se instala en modo editable (`uv pip install -e .`) sin depender de `PYTHONPATH` manual.
- [MVP] Cada alumno ejecuta su instancia local y diferencia trazas con `user_id="student-XX"`.
- [MVP] Las consultas de usuario llegan en texto plano y no requieren procesamiento de archivos.
- [FUTURO] Podrán incorporarse nuevas tools o mejorarse las existentes sin romper el contrato de respuesta.

## 5) Riesgos y mitigaciones
- [MVP] Riesgo: agente alucina productos no devueltos por la tool. Severidad: **esperada (didáctica)**. Mitigación: system prompt instruye "responder solo con datos de la tool"; los fallos alimentan el golden dataset de evals que construyen los alumnos.
- [MVP] Riesgo: agente responde fuera de ámbito (ej: asesoría legal). Severidad: **esperada (didáctica)**. Mitigación: system prompt define restricciones; los alumnos implementan guardrails de output en Día 2.
- [MVP] Riesgo: tool devuelve 0 resultados por limitación de keyword matching. Severidad: **esperada (didáctica)**. Mitigación: los alumnos detectan el patrón en Langfuse (tool span vacío → generation con datos inventados).
- [MVP] Riesgo: exposición de PII en entrada del usuario. Severidad: baja. Mitigación: los alumnos implementan scanners de LLM Guard en Día 2; el agente base no incluye guardrails.
- [MVP] Riesgo: caída o timeout de AWS Bedrock. Severidad: baja. Mitigación: manejo de error con respuesta controlada y `requires_human=true`.
- [MVP] Riesgo: costes excesivos de Bedrock. Severidad: media. Mitigación: `max_tokens: 1024` hardcoded, AWS Budget con alertas, solo modelo Haiku.
- [FUTURO] Riesgo: deuda técnica por expansión de tools. Mitigación: contrato de respuesta estable (`TechShopResponse`) y validaciones automáticas.

## 6) Dependencias externas
- [MVP] Strands Agents SDK con soporte OTEL (`strands-agents[otel]`).
- [MVP] AWS Bedrock con Claude Haiku 4.5 habilitado y quota increase solicitada.
- [MVP] Langfuse v3 self-hosted en EC2 (Docker Compose) con headless init (proyecto, org, API keys pre-creados).
- [MVP] JSON estático de catálogo de productos (`catalog.json`, 15-20 productos inventados).
- [MVP] JSON estático de FAQs de políticas (`faqs.json`, 10-12 preguntas).
- [MVP] `pydantic` v2 para modelado y validación de configuración.
- [MVP] `uv` como herramienta de gestión de entornos/dependencias Python.
	- [MVP] `hatchling` como backend de build definido en `pyproject.toml`.
	- [FUTURO] Bedrock Titan Embeddings o sentence-transformers local (para tools v2 con FAISS).
- [FUTURO] AWS SAM CLI para despliegue serverless en Lambda.

## 7) Requisitos EARS + criterios de aceptación verificables

### Requisito 1 [MVP]: Orquestación de tools por intención
**Objetivo:** Como instructor, quiero que TechShop Agent invoque la tool correcta según la intención del usuario, para que los alumnos observen decisiones de routing en las trazas de Langfuse.

#### Criterios de aceptación (EARS)
1. When la consulta del usuario sea sobre un producto o recomendación de compra, the TechShop Agent shall invocar `search_catalog` con la consulta como parámetro.
2. When la consulta del usuario sea sobre políticas de tienda (devoluciones, envíos, garantías, pagos, horarios), the TechShop Agent shall invocar `get_faq_answer` con la pregunta como parámetro.
3. When la consulta del usuario requiera información de producto Y de políticas, the TechShop Agent shall invocar ambas tools en el mismo turno.
4. If la intención no pueda clasificarse como producto o política de tienda, the TechShop Agent shall responder con `category="out_of_scope"` y `requires_human=true` sin invocar ninguna tool.
5. The TechShop Agent shall devolver siempre una respuesta con los campos `answer`, `confidence`, `category` y `requires_human`.

### Requisito 2 [MVP]: Calidad funcional de `search_catalog` v1
**Objetivo:** Como instructor, quiero una tool de búsqueda con limitaciones deliberadas y documentadas, para que los alumnos las detecten con observabilidad y las midan con evals.

#### Criterios de aceptación (EARS)
1. When se busque un producto por nombre exacto presente en el catálogo (ej: "ProBook X1"), the tool shall devolver al menos nombre, precio, stock y descripción de dicho producto.
2. When se busque usando un sinónimo no presente en el catálogo (ej: "laptop" cuando el catálogo usa "portátil"), the tool shall devolver 0 resultados. **Este fallo es deliberado.**
3. When la query matchee múltiples productos, the tool shall devolver todos los matches sin ranking ni límite. **Esta ausencia de ranking es deliberada.**
4. If no se encuentren productos, the tool shall devolver un mensaje explícito indicando "no se encontraron productos para: {query}".
5. The tool shall buscar mediante keyword matching puro: `query.lower()` contenido en `(nombre + " " + descripción).lower()` de cada producto, sin stemming, fuzzy matching ni análisis semántico.

### Requisito 3 [MVP]: Calidad funcional de `get_faq_answer` v1
**Objetivo:** Como instructor, quiero una tool de FAQs con las mismas limitaciones deliberadas, para mantener consistencia en los fallos observables.

#### Criterios de aceptación (EARS)
1. When se pregunte usando vocabulario presente en las FAQs (ej: "reembolso" cuando la FAQ usa "reembolso"), the tool shall devolver la pregunta y respuesta de la FAQ que matchee.
2. When se pregunte usando sinónimos no presentes en las FAQs (ej: "devolver" cuando la FAQ usa "reembolso"), the tool shall devolver 0 resultados. **Este fallo es deliberado.**
3. If múltiples FAQs matcheen, the tool shall devolver la primera coincidencia sin ranking por relevancia. **Esta selección arbitraria es deliberada.**
4. If no se encuentre ninguna FAQ, the tool shall devolver un mensaje explícito indicando "no se encontró información sobre: {question}".
5. The tool shall buscar mediante keyword matching: palabras de `question.lower()` (excluyendo stopwords básicas) contenidas en `(faq.question + " " + faq.answer).lower()`.

### Requisito 4 [MVP]: Trazabilidad via OpenTelemetry
**Objetivo:** Como instructor, quiero trazas ricas automáticas en Langfuse, para que los alumnos puedan analizar el comportamiento del agente sin instrumentar manualmente.

#### Criterios de aceptación (EARS)
1. When se procese una consulta, the TechShop Agent shall generar un trace en Langfuse que contenga: agent span (nivel superior), cycle spans (por cada ciclo del event loop), LLM spans (con tokens, prompt y completion) y tool spans (con nombre, parámetros y resultado).
2. When se invoque una tool, the tool span shall registrar nombre de la tool, parámetros de entrada, resultado devuelto y duración.
3. The TechShop Agent shall asociar cada trace a `user_id` cuando esté disponible, para permitir filtrado por alumno en Langfuse.
4. The TechShop Agent shall enviar trazas via OTEL exporter configurado con variables de entorno (`OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`).

### Requisito 5 [MVP]: Gestión de prompt externalizada
**Objetivo:** Como instructor, quiero que el system prompt viva en Langfuse Prompt Management, para que los alumnos puedan iterar el prompt sin tocar el código del agente.

#### Criterios de aceptación (EARS)
1. When se inicialice el agente, the TechShop Agent shall obtener el system prompt desde Langfuse Prompt Management usando el nombre de prompt y label configurados.
2. If el prompt no esté disponible en Langfuse (ej: error de conexión), the TechShop Agent shall usar un prompt fallback hardcoded y registrar un warning en los logs.
3. The prompt en Langfuse shall soportar variables (`{{catalog_categories}}`, `{{faq_topics}}`) que el agente rellena al inicializar.
4. When un alumno cree una nueva versión del prompt en Langfuse y la promueva al label `production`, the TechShop Agent shall usar la nueva versión en la siguiente ejecución sin requerir redeploy.

### Requisito 6 [MVP]: Comportamiento ante fallos
**Objetivo:** Como instructor, quiero que el agente maneje fallos de forma controlada, para que los alumnos vean patrones de resiliencia en las trazas.

#### Criterios de aceptación (EARS)
1. If `search_catalog` falle o agote tiempo, the TechShop Agent shall devolver un mensaje de limitación temporal sin inventar datos de producto, con `confidence="low"` y `requires_human=true`.
2. If `get_faq_answer` falle o agote tiempo, the TechShop Agent shall informar indisponibilidad de la información de políticas, con `confidence="low"` y `requires_human=true`.
3. If el modelo LLM (Bedrock) falle o agote tiempo, the TechShop Agent shall devolver una respuesta genérica de error con `requires_human=true`.
4. The TechShop Agent shall completar la respuesta en un máximo de 15 segundos en condiciones nominales de infraestructura.
5. When falle cualquier dependencia, the TechShop Agent shall registrar el error en la traza de Langfuse con tipo de error y contexto de operación.

### Requisito 7 [MVP]: Respuesta estructurada verificable
**Objetivo:** Como instructor, quiero respuestas con campos verificables, para que los alumnos puedan escribir assertions deterministas en promptfoo y validaciones con Pydantic.

#### Criterios de aceptación (EARS)
1. The TechShop Agent shall devolver siempre una respuesta parseable como `TechShopResponse(answer, confidence, category, requires_human)`.
2. When el agente responda con datos de producto, `category` shall ser `"product"`.
3. When el agente responda con datos de políticas, `category` shall ser `"faq"`.
4. If el agente responda a una consulta ambigua sin invocar tools, `category` shall ser `"general"`.
5. If `confidence` sea `"low"`, `requires_human` shall ser `true`.
6. When el agente mencione un producto en `answer`, dicho producto shall existir en `catalog.json`. **El incumplimiento de este criterio indica alucinación y es un caso válido para el golden dataset.**

### Requisito 8 [FUTURO]: Evolución de tools a v2 (embeddings + FAISS)
**Objetivo:** Como instructor, quiero poder evolucionar las tools a búsqueda semántica, para conectar con el módulo de RAG y medir la mejora con evals.

#### Criterios de aceptación (EARS)
1. Where la feature de tools v2 esté habilitada, when se busque un sinónimo (ej: "laptop"), the tool shall devolver resultados semánticamente relevantes (ej: productos con "portátil").
2. Where la feature de tools v2 esté habilitada, the tool shall usar embeddings (Bedrock Titan o sentence-transformers local) con FAISS `IndexFlatL2` in-memory.
3. The tools v2 shall mantener la misma firma que v1 (`search_catalog(query: str) -> str`) para no romper la integración con el agente.
4. When los alumnos ejecuten evals v1 vs v2 con el mismo golden dataset, the resultados shall ser comparables para medir la mejora.

## Preguntas abiertas
- ¿Cuál es el umbral de confianza que fuerza `requires_human=true`? (Propuesta: dejarlo como ejercicio de guardrails para los alumnos en Día 2.)
- ¿Se necesita un catálogo de stopwords para español en `get_faq_answer`, o basta con una lista mínima hardcoded?
- ¿El prompt fallback hardcoded debe ser funcional o mínimo? (Propuesta: funcional pero simplificado, para que el agente no se rompa completamente si Langfuse no está disponible.)