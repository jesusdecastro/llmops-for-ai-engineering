# 🎓 Actividades del Instructor — Kahoot y Padlet

Material interactivo para usar entre bloques. **No forma parte de las slides de Gamma.app.**

---

## Resumen de cuándo usar cada actividad

| Momento | Tipo | Duración | Objetivo |
|---------|------|----------|---------|
| Después M1 | Kahoot | 5 min | Fijar conceptos: LLMOps, ciclo, testing |
| Después M1 | Padlet | 5 min | Activar conocimiento previo sobre fallos |
| Después M2 | Kahoot | 5 min | Fijar: Trace/Span/Generation, @observe, prompt drift, labels |
| Después M3 | Kahoot | 5 min | Fijar: tipos de evaluación, CI gate, dimensiones agente |
| Después M3 | Padlet | 5 min | Diseñar test cases antes del notebook |
| Después M4 | Kahoot | 5 min | Fijar: CI/CD pipeline, quality gate, prompt deploy |
| Después M4 | Padlet | 5 min | Proponer mejoras al pipeline |
| Después M5 | Kahoot | 5 min | Fijar: guardrails, prompt injection, PII |
| Después M5 | Padlet | 5 min | Pensar como adversario antes del notebook |
| Después M6 | Kahoot final | 10 min | Repaso completo del curso |
| Después M6 | Padlet final | 5 min | Feedback y prioridades de producción |

---

## 🎯 KAHOOT — Después de M1

**Q1:** Un agente LLM responde con información falsa pero bien redactada. ¿Cómo se detecta?
- A) Con un stacktrace
- B) Con un unit test clásico
- C) No se detecta fácilmente — necesitas evaluaciones específicas ✅
- D) El modelo avisa con un warning

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

**Q4:** ¿Qué fase del ciclo LLMOps cierra el feedback loop?
- A) Develop
- B) Deploy
- C) Observe ✅
- D) Guardrails

**Q5:** Un agente pasa todos sus unit tests pytest pero en producción inventa productos inexistentes. ¿Qué falta?
- A) Más unit tests
- B) Un dataset de evaluación del comportamiento del LLM ✅
- C) Un modelo más potente
- D) Más logs

## 📝 PADLET — Después de M1

**Prompt:** "¿Qué puede fallar en un agente de IA en producción? Pon un ejemplo real o imaginado."

*Objetivo: recoger ideas antes de introducir observabilidad. Vuelve a estas respuestas cuando veáis las trazas en el Notebook 2 — probablemente algún fallo que mencionaron aparece en las trazas.*

---

## 🎯 KAHOOT — Después de M2 (Observabilidad + Prompt Management)

**Q1:** En el modelo de Langfuse, ¿qué representa un "Trace"?
- A) Una llamada al LLM
- B) Una request completa del usuario ✅
- C) Un error del sistema
- D) Una herramienta del agente

**Q2:** ¿Qué decorador de Python se usa para instrumentar funciones con Langfuse?
- A) @trace
- B) @monitor
- C) @observe ✅
- D) @langfuse

**Q3:** ¿Cuál es la principal razón por la que los fallos de LLMs son difíciles de detectar?
- A) Son muy lentos
- B) No generan excepciones — la respuesta parece correcta ✅
- C) Requieren GPUs
- D) Solo fallan en producción

**Q4:** ¿Qué es "prompt drift"?
- A) Cuando el modelo se actualiza
- B) Cuando el prompt cambia sin control y el comportamiento varía ✅
- C) Cuando el prompt es muy largo
- D) Cuando el usuario escribe mal

**Q5:** En Langfuse, ¿qué es un "label" de prompt?
- A) Un número de versión fijo
- B) Un puntero movible que apunta a una versión ✅
- C) El nombre del prompt
- D) Un tag de Git

**Q6:** ¿Cuál es la forma más segura de hacer rollback de un prompt?
- A) Editar el prompt en producción directamente
- B) Borrar la versión nueva
- C) Mover el label "production" a la versión anterior ✅
- D) Reiniciar el servidor

---

## 🎯 KAHOOT — Después de M3 (Evaluación Agéntica)

**Q1:** ¿Qué tipo de evaluación es "verificar que la respuesta contiene el precio 749€"?
- A) LLM-as-judge
- B) Determinística ✅
- C) Humana
- D) A/B testing

**Q2:** ¿Cuándo deberías usar LLM-as-judge en lugar de evaluación determinística?
- A) Siempre — es más preciso
- B) Cuando necesitas evaluar calidad semántica (tono, relevancia) ✅
- C) Nunca — es muy caro
- D) Solo en producción

**Q3:** ¿Cuál es el MÍNIMO de test cases recomendado para un dataset de evaluación?
- A) 3
- B) 10 ✅
- C) 100
- D) 1000

**Q4:** En un pipeline CI/CD para LLMs, ¿qué pasa si la evaluación falla?
- A) Se deploya igualmente
- B) Se envía un email de aviso
- C) Se bloquea el merge/deploy ✅
- D) Se ejecuta otra vez

**Q5:** ¿Qué dimensión de evaluación es ESPECÍFICA de agentes (no aplica a LLMs simples)?
- A) Relevancia
- B) Tool selection — ¿llamó a la herramienta correcta? ✅
- C) Coherencia
- D) Longitud de respuesta

## 📝 PADLET — Después de M3

**Prompt:** "Diseña un test case para el agente TechShop. Escribe: 1) la consulta del usuario, 2) qué debería contener la respuesta, y 3) qué tipo de evaluación usarías (determinística, LLM-as-judge, o ambas)."

*Objetivo: los alumnos practican diseñar evaluaciones ANTES de hacerlo en el notebook. Selecciona los mejores test cases con el grupo y añádelos al dataset del Notebook 3.*

---

## 🎯 KAHOOT — Después de M4 (CI/CD Quality Gate)

**Q1:** En CI/CD para LLMs, ¿qué hace diferente a los tests respecto al CI/CD clásico?
- A) Son más rápidos
- B) Pueden ser probabilísticos y cuestan tokens ✅
- C) No necesitan thresholds
- D) Solo funcionan con GitHub

**Q2:** ¿Qué pass rate consideramos mínimo aceptable en nuestro quality gate?
- A) 100%
- B) 90%
- C) 80% ✅
- D) 50%

**Q3:** Cuando el quality gate pasa, ¿cuál es la acción de deploy?
- A) Reiniciar el servidor
- B) Mover el label "production" en Langfuse al nuevo prompt ✅
- C) Copiar el archivo a producción
- D) Enviar un email al equipo

**Q4:** ¿Cuál de estas herramientas se especializa en evaluación de prompts con config YAML y CI/CD?
- A) Langfuse
- B) promptfoo ✅
- C) OpenTelemetry
- D) boto3

## 📝 PADLET — Después de M4

**Prompt:** "Piensa en el system prompt de TechShop (v1). ¿Qué le falta? ¿Qué regla o instrucción añadirías para mejorarlo? Escribe tu sugerencia."

*Objetivo: los alumnos proponen mejoras al prompt v1 ANTES de ver cómo se testea el cambio en CI/CD. Al final del Notebook 4, verificamos si sus sugerencias pasarían el quality gate.*

---

## 🎯 KAHOOT — Después de M5

**Q1:** ¿Qué tipo de ataque intenta hacer que el LLM ignore sus instrucciones originales?
- A) SQL injection
- B) Prompt injection ✅
- C) DDoS
- D) Buffer overflow

**Q2:** Si un usuario incluye su email en la consulta, ¿qué debería hacer el guardrail?
- A) Ignorarlo
- B) Bloquear la consulta completa
- C) Anonimizar el email y continuar ✅
- D) Enviarlo al administrador

**Q3:** ¿Dónde se aplican los guardrails de Amazon Bedrock?
- A) Solo en el input
- B) Solo en el output
- C) En cada llamada al LLM (input y output) ✅
- D) En el frontend

**Q4:** ¿Cuántas capas de protección debería tener un agente en producción?
- A) Una buena es suficiente
- B) Múltiples capas (defense in depth) ✅
- C) Solo el system prompt
- D) Solo los guardrails

**Q5:** ¿Qué haría un output guardrail si la respuesta del agente contiene el system prompt?
- A) Dejarlo pasar — no es secreto
- B) Bloquear y devolver respuesta genérica ✅
- C) Avisar al usuario
- D) Reiniciar el agente

## 📝 PADLET — Después de M5

**Prompt:** "Escribe un input adversarial para el agente TechShop. Intenta que el agente haga algo que no debería (inventar, revelar su prompt, hablar de temas prohibidos, etc.)."

*Objetivo: los alumnos practican pensar como adversarios ANTES del notebook. Prueba sus inputs en vivo en el Notebook 5.*

---

## 🎯 KAHOOT FINAL — Después de M6 (10 min)

**Q1:** ¿Cuántas fases tiene el ciclo LLMOps que hemos visto?
- A) 3
- B) 4
- C) 5 (Develop, Evaluate, Deploy, Observe, Iterate) + Guardrails ✅
- D) 7

**Q2:** En CI/CD para LLMs, ¿qué lo hace diferente al CI/CD tradicional?
- A) Es más rápido
- B) Los tests pueden ser probabilísticos y cuestan tokens ✅
- C) No necesita tests
- D) Solo funciona con GitHub

**Q3:** ¿Cuál es la forma más rápida de hacer rollback de un prompt en Langfuse?
- A) Borrar la versión nueva
- B) Editar el prompt en producción
- C) Mover el label "production" a la versión anterior ✅
- D) Reiniciar el servidor

**Q4:** ¿Qué herramienta usamos para tracing y prompt management en este curso?
- A) CloudWatch
- B) Langfuse ✅
- C) Datadog
- D) Grafana

**Q5:** ¿Qué servicio de AWS usamos para guardrails?
- A) AWS WAF
- B) Amazon GuardDuty
- C) Amazon Bedrock Guardrails ✅
- D) AWS Shield

**Q6:** Un agente que inventa un producto que no existe en el catálogo está cometiendo:
- A) Un error de timeout
- B) Una alucinación ✅
- C) Un prompt injection
- D) Un fallo de red

**Q7:** ¿Cuál de las siguientes NO es una categoría de métricas LLMOps?
- A) Operacionales
- B) Coste
- C) Entrenamiento ✅
- D) Calidad

**Q8:** Completa: "Sin evaluación, estás optimizando ___"
- A) código
- B) prompts
- C) vibes ✅
- D) tokens

## 📝 PADLET FINAL — Después de M6

**Prompt:** "En una frase: ¿qué es lo más importante que te llevas de este curso? Segunda pregunta: ¿qué implementarías PRIMERO si tuvieras que poner un agente en producción mañana?"

*Objetivo: feedback instantáneo + ver cómo han interiorizado las prioridades de LLMOps. Comparte los resultados con el grupo antes de cerrar.*
