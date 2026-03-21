# Plan de implementación: standsagent-tools-basicas

- [x] 1. [MVP] Preparar configuración base del agente para Bedrock, OTEL y Langfuse
  - **Objetivo:** Dejar configurados los parámetros mínimos de ejecución local (modelo, exporter OTEL y variables de prompt management), migrar `AgentConfig` a Pydantic `BaseModel` con validación, estandarizar `uv` y dejar `hatchling` como backend de build con instalación editable sin `PYTHONPATH`.
  - **Archivos afectados:** `src/techshop_agent/config.py`, `pyproject.toml`, `.env.example` (si aplica), `README.md` (sección de variables, si aplica).
  - **Requisito(s) que cubre:** 4.4, 5.1
  - **Criterio de done verificable:** El agente inicia con configuración válida usando `AgentConfig` Pydantic y puede resolver una consulta sin errores de inicialización cuando las variables requeridas están presentes; los comandos de dev se ejecutan con `uv`, el backend de build es `hatchling` y el paquete funciona instalado en editable sin `PYTHONPATH`.
  - **Test/check asociado:** Test de configuración que valida lectura de `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, nombre/label de prompt y modelo Bedrock, ejecutado con `uv run pytest`; verificación de import del paquete tras `uv pip install -e .`.
  - **Riesgo de implementación:** Configuración incompleta por diferencias de entorno local de alumnos.
  - _Requirements: 4.4, 5.1_

- [x] 2. [MVP] Crear y validar el dataset local de catálogo
  - **Objetivo:** Incorporar `catalog.json` con 15-20 productos inventados y campos mínimos para búsquedas v1 y validaciones anti-alucinación.
  - **Archivos afectados:** `src/techshop_agent/data/catalog.json` (o ruta equivalente), tests de fixture de catálogo.
  - **Requisito(s) que cubre:** 2.1, 7.6
  - **Criterio de done verificable:** El JSON carga correctamente, contiene entre 15 y 20 productos y todos incluyen nombre, precio, stock y descripción.
  - **Test/check asociado:** Test de esquema del catálogo y conteo de productos.
  - **Riesgo de implementación:** Datos inconsistentes que rompan búsquedas o validaciones posteriores.
  - _Requirements: 2.1, 7.6_

- [x] 3. [MVP] Implementar tool `search_catalog` v1 por keyword matching (P)
  - **Objetivo:** Construir la búsqueda deliberadamente limitada usando `lower()+in`, sin ranking ni semántica.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/responder.py` (si aplica), tests unitarios de catálogo.
  - **Requisito(s) que cubre:** 2.1, 2.2, 2.3, 2.4, 2.5
  - **Criterio de done verificable:** La tool devuelve matches exactos, 0 resultados con sinónimos no presentes y mensaje explícito cuando no hay resultados.
  - **Test/check asociado:** Suite unitaria con casos exact match, sinónimo fallido, múltiples matches y no encontrado.
  - **Riesgo de implementación:** Introducir lógica “inteligente” no deseada que reduzca el valor didáctico.
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. [MVP] Crear y validar el dataset local de FAQs
  - **Objetivo:** Incorporar `faqs.json` con 10-12 preguntas de políticas redactadas para exponer limitaciones de matching por sinónimos.
  - **Archivos afectados:** `src/techshop_agent/data/faqs.json` (o ruta equivalente), tests de fixture FAQ.
  - **Requisito(s) que cubre:** 3.1
  - **Criterio de done verificable:** El JSON carga correctamente, contiene entre 10 y 12 FAQs y cada entrada tiene pregunta y respuesta.
  - **Test/check asociado:** Test de esquema y conteo de FAQs.
  - **Riesgo de implementación:** Cobertura temática insuficiente para devoluciones/envíos/garantías/pagos/horarios.
  - _Requirements: 3.1_

- [x] 5. [MVP] Implementar tool `get_faq_answer` v1 por keywords con stopwords básicas (P)
  - **Objetivo:** Construir la búsqueda v1 de políticas con exclusión mínima de stopwords y selección de primera coincidencia.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/responder.py` (si aplica), tests unitarios FAQ.
  - **Requisito(s) que cubre:** 3.1, 3.2, 3.3, 3.4, 3.5
  - **Criterio de done verificable:** La tool retorna FAQ correcta con vocabulario presente, falla con sinónimos no incluidos, elige primera coincidencia y responde mensaje explícito en no match.
  - **Test/check asociado:** Suite unitaria con casos de match directo, sinónimo fallido, múltiples matches y ausencia de resultados.
  - **Riesgo de implementación:** Lista de stopwords excesiva que elimine términos relevantes.
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. [MVP] Implementar enrutamiento de intención y orquestación de tools
  - **Objetivo:** Clasificar consultas en producto, políticas o mixtas e invocar la(s) tool(s) correspondiente(s) en el mismo turno.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/responder.py`, tests de integración del pipeline.
  - **Requisito(s) que cubre:** 1.1, 1.2, 1.3
  - **Criterio de done verificable:** Una consulta de producto usa solo catálogo, una de políticas usa solo FAQ y una mixta ejecuta ambas tools en la misma interacción.
  - **Test/check asociado:** Tests de integración de routing con mocks de tools.
  - **Riesgo de implementación:** Ambigüedad de intención que degrade selección de tool.
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 7. [MVP] Implementar resolución de `out_of_scope` y `general` con regla de escalación
  - **Objetivo:** Aplicar categorías de salida cuando no corresponde invocar tools y forzar escalación humana cuando aplique.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/responder.py`, tests de clasificación de salida.
  - **Requisito(s) que cubre:** 1.4, 7.4, 7.5
  - **Criterio de done verificable:** Consultas fuera de dominio retornan `out_of_scope` con `requires_human=true`, y consultas ambiguas internas retornan `general`.
  - **Test/check asociado:** Tests unitarios de categoría y consistencia `confidence=low -> requires_human=true`.
  - **Riesgo de implementación:** Sobreuso de `out_of_scope` en consultas válidas del dominio.
  - _Requirements: 1.4, 7.4, 7.5_

- [x] 8. [MVP] Integrar system prompt desde Langfuse Prompt Management con fallback seguro
  - **Objetivo:** Cargar prompt por nombre/label, interpolar variables del dominio y activar fallback hardcoded con warning si Langfuse falla.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/config.py`, `src/techshop_agent/__init__.py` (si aplica), tests de prompt provider.
  - **Requisito(s) que cubre:** 5.1, 5.2, 5.3, 5.4
  - **Criterio de done verificable:** El agente usa prompt remoto cuando está disponible, usa fallback cuando no lo está y refleja cambios de label `production` en la siguiente ejecución.
  - **Test/check asociado:** Tests de integración con cliente Langfuse mockeado para éxito, fallo y cambio de versión.
  - **Riesgo de implementación:** Gestión de credenciales o timeouts que bloquee la inicialización.
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 9. [MVP] Instrumentar trazas OTEL completas para Langfuse
  - **Objetivo:** Emitir agent spans, cycle spans, LLM spans y tool spans con atributos mínimos y vínculo por `user_id`.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/config.py`, pruebas de observabilidad.
  - **Requisito(s) que cubre:** 4.1, 4.2, 4.3, 4.4
  - **Criterio de done verificable:** Cada consulta genera un trace con todos los spans esperados; cada tool span incluye nombre, parámetros, resultado y duración; el trace incluye `user_id` cuando existe.
  - **Test/check asociado:** Test de integración de trazas con exporter de prueba o assertions sobre spans emitidos.
  - **Riesgo de implementación:** Pérdida de atributos clave por instrumentación parcial.
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 10. [MVP] Implementar fallback resiliente ante fallos de tools y LLM
  - **Objetivo:** Devolver respuestas controladas por tipo de fallo sin inventar datos y registrando error en traza.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, `src/techshop_agent/responder.py`, tests de resiliencia.
  - **Requisito(s) que cubre:** 6.1, 6.2, 6.3, 6.5
  - **Criterio de done verificable:** Fallos/timeout de catálogo, FAQ o LLM devuelven mensaje controlado con `confidence=low` y `requires_human=true`, y dejan evidencia trazable del error.
  - **Test/check asociado:** Tests de integración con inyección de excepciones y timeouts por dependencia.
  - **Riesgo de implementación:** Mensajes inconsistentes que no permitan diagnóstico en observabilidad.
  - _Requirements: 6.1, 6.2, 6.3, 6.5_

- [x] 11. [MVP] Garantizar contrato estructurado `TechShopResponse` en todas las salidas
  - **Objetivo:** Forzar serialización consistente con categorías correctas y validación de referencias de producto.
  - **Archivos afectados:** `src/techshop_agent/responder.py`, `src/techshop_agent/agent.py`, `src/techshop_agent/config.py` (si aplica), tests de contrato.
  - **Requisito(s) que cubre:** 1.5, 7.1, 7.2, 7.3, 7.6
  - **Criterio de done verificable:** Todas las respuestas son parseables al contrato; `category` refleja correctamente product/faq; los productos mencionados existen en catálogo.
  - **Test/check asociado:** Tests unitarios y de integración con validación de esquema y validación cruzada contra `catalog.json`.
  - **Riesgo de implementación:** Desalineación entre ensamblado de respuesta y resultados reales de tools.
  - _Requirements: 1.5, 7.1, 7.2, 7.3, 7.6_

- [ ] 12. [MVP] Verificar cumplimiento del SLA funcional de 15 segundos
  - **Objetivo:** Comprobar que el flujo end-to-end cumple el tiempo máximo nominal bajo condiciones de infraestructura esperadas.
  - **Archivos afectados:** `tests/test_agent.py`, utilidades de test/performance livianas (si aplica).
  - **Requisito(s) que cubre:** 6.4
  - **Criterio de done verificable:** Escenario nominal de consulta completa en <= 15 segundos en entorno de prueba definido.
  - **Test/check asociado:** Test no funcional de latencia p95 o benchmark controlado reproducible.
  - **Riesgo de implementación:** Variabilidad de red/servicios externos que haga inestable la métrica.
  - _Requirements: 6.4_

- [ ] 13. [FUTURO] Diseñar interfaz extensible para tools v2 con firma compatible
  - **Objetivo:** Preparar feature flag y contrato estable para habilitar v2 semántica sin romper integración existente.
  - **Archivos afectados:** `src/techshop_agent/config.py`, `src/techshop_agent/agent.py`, pruebas de compatibilidad de firma.
  - **Requisito(s) que cubre:** 8.3
  - **Criterio de done verificable:** Con feature flag desactivada, comportamiento v1 permanece intacto; con flag activada, la firma pública de tool no cambia.
  - **Test/check asociado:** Test de regresión de contrato de tool y configuración por feature flag.
  - **Riesgo de implementación:** Acoplamiento accidental entre implementación v1 y v2.
  - _Requirements: 8.3_

- [ ] 14. [FUTURO] Implementar búsqueda semántica v2 con embeddings + FAISS
  - **Objetivo:** Añadir motor semántico in-memory para recuperar sinónimos relevantes y mejorar recall frente a v1.
  - **Archivos afectados:** `src/techshop_agent/agent.py`, módulo nuevo de retrieval semántico (si aplica), dependencias de embeddings/FAISS.
  - **Requisito(s) que cubre:** 8.1, 8.2
  - **Criterio de done verificable:** Con tools v2 habilitadas, consultas por sinónimos devuelven resultados semánticamente relevantes utilizando embeddings y FAISS `IndexFlatL2`.
  - **Test/check asociado:** Tests de integración semántica con casos de sinónimos (p. ej., "laptop" -> productos con "portátil").
  - **Riesgo de implementación:** Consumo de memoria/latencia por indexación en tiempo de ejecución.
  - _Requirements: 8.1, 8.2_

- [ ]* 15. [FUTURO] Ejecutar evaluación comparativa v1 vs v2 sobre mismo golden dataset
  - **Objetivo:** Medir mejora funcional de v2 manteniendo comparabilidad metodológica con baseline v1.
  - **Archivos afectados:** `tests/` (suite de eval comparativa), configuración de evaluación (promptfoo u otra herramienta usada por el curso).
  - **Requisito(s) que cubre:** 8.4
  - **Criterio de done verificable:** Reporte de resultados comparable entre v1 y v2 con mismo dataset, mismas métricas y evidencia de diferencia.
  - **Test/check asociado:** Pipeline de evaluación reproducible con resultados versionados.
  - **Riesgo de implementación:** Sesgo de comparación por cambios no controlados en dataset o configuración.
  - _Requirements: 8.4_
