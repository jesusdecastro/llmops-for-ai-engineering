"""Agente principal de TechShop usando Strands Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langfuse import Langfuse
from langfuse.decorators import observe
from strands import Agent, tool
from strands.models import BedrockModel

from techshop_agent.config import AgentConfig
from techshop_agent.guardrails import GuardrailsManager
from techshop_agent.responder import AgentResponse

if TYPE_CHECKING:
    from collections.abc import Callable


class TechShopAgent:
    """Agente de atención al cliente para TechShop usando Strands Agent."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        """Inicializa el agente TechShop.

        Args:
            config: Configuración del agente (usa defaults si no se proporciona)
        """
        self.config = config or AgentConfig()
        self.config.validate()

        # Inicializar Langfuse
        self.langfuse = Langfuse(
            public_key=self.config.langfuse_public_key,
            secret_key=self.config.langfuse_secret_key,
            host=self.config.langfuse_host,
        )

        # Inicializar guardrails
        self.guardrails = GuardrailsManager(
            enable_input=self.config.enable_input_guardrails,
            enable_output=self.config.enable_output_guardrails,
        )

        # Configurar modelo Bedrock
        self.model = BedrockModel(
            model_id=self.config.model_id,
            region_name=self.config.aws_region,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Crear herramientas del agente
        self.tools = self._create_tools()

        # Inicializar Strands Agent
        self.agent = Agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        """Retorna el system prompt del agente TechShop.

        TODO (Día 1): Los alumnos mejorarán este prompt con:
        1. Rol y contexto detallado
        2. Instrucciones de comportamiento
        3. Restricciones explícitas
        4. Formato de salida
        5. Ejemplos few-shot
        6. Manejo de edge cases

        Returns:
            System prompt del agente
        """
        return """Eres un asistente de atención al cliente para TechShop,
una tienda de productos tecnológicos.

Tu objetivo es ayudar a los clientes con:
- Consultas sobre productos (especificaciones, disponibilidad, precios)
- Reclamaciones y problemas con pedidos
- Preguntas generales sobre la tienda

Restricciones:
- NO inventes información sobre productos que no existen
- NO proporciones precios si no están en el catálogo
- Si no sabes algo, admítelo y ofrece escalar a un humano
- Mantén un tono profesional y amigable

Formato de respuesta:
- Sé conciso pero completo
- Usa viñetas para listas
- Incluye información relevante de contacto cuando sea apropiado
"""

    def _create_tools(self) -> list[Callable]:
        """Crea las herramientas disponibles para el agente.

        TODO (Día 1): Los alumnos añadirán herramientas como:
        1. search_product_catalog - Buscar productos en el catálogo
        2. check_order_status - Verificar estado de pedidos
        3. get_product_details - Obtener detalles de un producto
        4. escalate_to_human - Escalar a atención humana

        Returns:
            Lista de herramientas del agente
        """

        @tool
        def get_product_info(product_name: str) -> str:
            """Obtiene información sobre un producto del catálogo.

            Args:
                product_name: Nombre del producto a buscar

            Returns:
                Información del producto o mensaje de no encontrado
            """
            # TODO: Implementar búsqueda real en catálogo
            return f"Información del producto '{product_name}' pendiente de implementar"

        @tool
        def check_order(order_id: str) -> str:
            """Verifica el estado de un pedido.

            Args:
                order_id: ID del pedido a verificar

            Returns:
                Estado actual del pedido
            """
            # TODO: Implementar verificación real de pedidos
            return f"Estado del pedido '{order_id}' pendiente de implementar"

        return [get_product_info, check_order]

    @observe(name="process_query")
    def process_query(
        self,
        user_query: str,
        user_id: str,  # noqa: ARG002
        session_id: str,  # noqa: ARG002
        context: dict | None = None,  # noqa: ARG002
    ) -> AgentResponse:
        """Procesa una consulta de usuario end-to-end.

        Flujo:
        1. Input guardrails - Validar y sanitizar la consulta
        2. Invocar Strands Agent - El agente decide qué herramientas usar
        3. Output guardrails - Validar la respuesta
        4. Retornar resultado - Con metadata completa

        TODO (Día 1): Los alumnos completarán:
        1. Instrumentación completa con Langfuse
        2. Registro de metadata (user_id, session_id, intent)
        3. Captura de tokens y costes
        4. Manejo de errores con fallbacks

        Args:
            user_query: Consulta del usuario
            user_id: ID del usuario
            session_id: ID de la sesión
            context: Contexto adicional (catálogo, historial, etc.)

        Returns:
            AgentResponse con la respuesta final
        """
        # 1. Input guardrails
        sanitized_query, is_safe, _input_metadata = self.guardrails.scan_input(user_query)

        if not is_safe:
            return AgentResponse(
                answer="Lo siento, no puedo procesar esa consulta.",
                confidence="high",
                category="out_of_scope",
                requires_human=True,
            )

        # 2. Invocar Strands Agent
        # TODO: Los alumnos añadirán manejo de errores y logging
        agent_response = self.agent(sanitized_query)

        # 3. Output guardrails
        validated_answer, is_valid, _output_metadata = self.guardrails.scan_output(
            agent_response, sanitized_query
        )

        if not is_valid:
            return AgentResponse(
                answer="Lo siento, no puedo proporcionar esa información.",
                confidence="low",
                category="out_of_scope",
                requires_human=True,
            )

        # 4. Construir respuesta
        # TODO: Los alumnos implementarán clasificación automática de categoría
        return AgentResponse(
            answer=validated_answer,
            confidence="medium",
            category="general",
            requires_human=False,
        )
