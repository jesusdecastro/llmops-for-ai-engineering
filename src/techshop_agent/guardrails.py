"""Guardrails de input y output usando LLM Guard."""

from __future__ import annotations

from langfuse.decorators import observe


class GuardrailsManager:
    """Gestiona los guardrails de input y output."""

    def __init__(self, *, enable_input: bool = True, enable_output: bool = True) -> None:
        """Inicializa el gestor de guardrails.

        Args:
            enable_input: Habilitar guardrails de input
            enable_output: Habilitar guardrails de output
        """
        self.enable_input = enable_input
        self.enable_output = enable_output

    @observe(name="scan_input")
    def scan_input(self, user_query: str) -> tuple[str, bool, dict]:
        """Escanea el input del usuario antes de enviarlo al LLM.

        TODO (Día 2): Los alumnos implementarán:
        1. Scanner de prompt injection
        2. Scanner de PII con anonimización
        3. Scanner de toxicidad
        4. Scanner de secrets
        5. Decisión: bloquear, redactar o continuar

        Args:
            user_query: Consulta original del usuario

        Returns:
            Tuple de (query_procesada, es_segura, metadata)
        """
        if not self.enable_input:
            return user_query, True, {}

        # TODO: Implementar input scanning con LLM Guard
        # Hint: from llm_guard.input_scanners import PromptInjection, Anonymize, Toxicity

        # Placeholder para el ejercicio
        return user_query, True, {"scanners_passed": []}

    @observe(name="scan_output")
    def scan_output(
        self,
        response: str,
        user_query: str,  # noqa: ARG002
    ) -> tuple[str, bool, dict]:
        """Escanea la respuesta del LLM antes de entregarla al usuario.

        TODO (Día 2): Los alumnos implementarán:
        1. Validación de relevancia
        2. Detección de temas prohibidos
        3. Verificación de formato
        4. Fallback si no pasa validación

        Args:
            response: Respuesta generada por el LLM
            user_query: Consulta original para contexto

        Returns:
            Tuple de (respuesta_procesada, es_válida, metadata)
        """
        if not self.enable_output:
            return response, True, {}

        # TODO: Implementar output scanning con LLM Guard
        # Hint: from llm_guard.output_scanners import Relevance, BanTopics

        # Placeholder para el ejercicio
        return response, True, {"scanners_passed": []}
