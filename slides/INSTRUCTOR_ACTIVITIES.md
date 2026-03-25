# 🎓 Actividades del Instructor — Kahoot y Padlet

Material interactivo para usar entre bloques. **No forma parte de las slides de Gamma.app.**

---

## Resumen de cuándo usar cada actividad

| Momento | Tipo | Duración | Objetivo |
|---------|------|----------|---------|
| Después M1 | Kahoot | 5 min | Fijar conceptos: LLMOps, ciclo, testing |
| Después M1 | Padlet | 5 min | Activar conocimiento previo sobre fallos |
| Después M2 | Kahoot | 5 min | Fijar: Trace/Span/Generation, @observe, prompt drift, labels |

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

