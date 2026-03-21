"""Agente principal de TechShop usando Strands Agent."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from langfuse import Langfuse, observe
from opentelemetry import trace
from strands import Agent, tool
from strands.models import BedrockModel

from techshop_agent.config import AgentConfig
from techshop_agent.guardrails import GuardrailsManager
from techshop_agent.responder import AgentResponse

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Literal


LOGGER = logging.getLogger(__name__)
TRACER = trace.get_tracer(__name__)


FAQ_STOPWORDS = {
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "y",
    "o",
    "un",
    "una",
    "que",
    "en",
    "por",
    "para",
    "con",
    "sobre",
}

PRODUCT_KEYWORDS = {
    "producto",
    "productos",
    "comprar",
    "precio",
    "stock",
    "portátil",
    "smartphone",
    "tablet",
    "auriculares",
}

FAQ_KEYWORDS = {
    "reembolso",
    "devolución",
    "devoluciones",
    "envío",
    "envíos",
    "garantía",
    "garantías",
    "pago",
    "pagos",
    "horario",
    "horarios",
    "política",
    "políticas",
}

STORE_CONTEXT_KEYWORDS = {
    "tienda",
    "techshop",
    "catálogo",
    "catalogo",
    "producto",
    "productos",
    "compra",
    "comprar",
    "cliente",
}


def search_catalog_v1(query: str) -> str:
    """Busca productos en catálogo con matching v1 deliberadamente limitado."""
    with TRACER.start_as_current_span("tool.search_catalog") as span:
        span.set_attribute("tool.name", "search_catalog")
        span.set_attribute("tool.input.query", query)

        catalog_path = Path(__file__).parent / "data" / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

        normalized_query = query.lower()
        matches: list[dict[str, object]] = []

        for product in catalog:
            searchable_text = f"{product['nombre']} {product['descripcion']}".lower()
            if normalized_query in searchable_text:
                matches.append(
                    {
                        "nombre": product["nombre"],
                        "precio": product["precio"],
                        "stock": product["stock"],
                        "descripcion": product["descripcion"],
                    }
                )

        span.set_attribute("tool.output.match_count", len(matches))

        if not matches:
            return f"no se encontraron productos para: {query}"

        return json.dumps(matches, ensure_ascii=False)


def get_faq_answer_v1(question: str) -> str:
    """Busca información FAQ con matching por palabras y stopwords básicas."""
    with TRACER.start_as_current_span("tool.get_faq_answer") as span:
        span.set_attribute("tool.name", "get_faq_answer")
        span.set_attribute("tool.input.question", question)

        faqs_path = Path(__file__).parent / "data" / "faqs.json"
        faqs = json.loads(faqs_path.read_text(encoding="utf-8"))

        words = [word for word in question.lower().split() if word not in FAQ_STOPWORDS]

        for faq in faqs:
            searchable_text = f"{faq['pregunta']} {faq['respuesta']}".lower()
            if any(word in searchable_text for word in words):
                span.set_attribute("tool.output.match_found", True)
                return json.dumps(
                    {
                        "pregunta": faq["pregunta"],
                        "respuesta": faq["respuesta"],
                        "tema": faq["tema"],
                    },
                    ensure_ascii=False,
                )

        span.set_attribute("tool.output.match_found", False)
        return f"no se encontró información sobre: {question}"


def classify_tool_intent(query: str) -> tuple[bool, bool]:
    """Clasifica si la consulta requiere tool de catálogo, FAQ o ambas."""
    query_lower = query.lower()
    needs_product = any(keyword in query_lower for keyword in PRODUCT_KEYWORDS)
    needs_faq = any(keyword in query_lower for keyword in FAQ_KEYWORDS)
    return needs_product, needs_faq


def is_store_context_query(query: str) -> bool:
    """Determina si una consulta ambigua pertenece al dominio de la tienda."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in STORE_CONTEXT_KEYWORDS)


def resolve_system_prompt(
    *,
    langfuse_client: Langfuse,
    prompt_name: str,
    prompt_label: str,
    prompt_variables: dict[str, str],
    fallback_prompt: str,
) -> str:
    """Resuelve el system prompt desde Langfuse con fallback seguro."""
    try:
        prompt_client = langfuse_client.get_prompt(
            prompt_name,
            label=prompt_label,
            type="text",
            fallback=fallback_prompt,
        )
        return prompt_client.compile(**prompt_variables)
    except Exception as exc:
        LOGGER.warning("Langfuse prompt unavailable, using fallback prompt: %s", exc)
        return fallback_prompt


class TechShopAgent:
    """Agente de atención al cliente para TechShop usando Strands Agent."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        """Inicializa el agente TechShop.

        Args:
            config: Configuración del agente (usa defaults si no se proporciona)
        """
        self.config = config or AgentConfig()
        self.config.validate_config()

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
        """Retorna el system prompt del agente TechShop."""
        data_dir = Path(__file__).parent / "data"
        catalog = json.loads((data_dir / "catalog.json").read_text(encoding="utf-8"))
        faqs = json.loads((data_dir / "faqs.json").read_text(encoding="utf-8"))

        catalog_categories = sorted({item.get("categoria", "general") for item in catalog})
        faq_topics = sorted({item.get("tema", "general") for item in faqs})

        prompt_variables = {
            "catalog_categories": ", ".join(catalog_categories),
            "faq_topics": ", ".join(faq_topics),
        }

        fallback_prompt = """Eres un asistente de atención al cliente para TechShop,
una tienda de productos tecnológicos.

Tu objetivo es ayudar a los clientes con:
- Consultas sobre productos (especificaciones, disponibilidad, precios)
- Consultas sobre políticas de tienda (devoluciones, envíos, garantías, pagos, horarios)

Categorías de catálogo disponibles: {{catalog_categories}}
Temas de FAQ disponibles: {{faq_topics}}

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

        return resolve_system_prompt(
            langfuse_client=self.langfuse,
            prompt_name=self.config.langfuse_prompt_name,
            prompt_label=self.config.langfuse_prompt_label,
            prompt_variables=prompt_variables,
            fallback_prompt=fallback_prompt,
        )

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
        def search_catalog(query: str) -> str:
            """Busca productos en el catálogo local por keyword matching."""
            return search_catalog_v1(query)

        @tool
        def get_faq_answer(question: str) -> str:
            """Busca respuestas sobre políticas de tienda en FAQs locales."""
            return get_faq_answer_v1(question)

        return [search_catalog, get_faq_answer]

    def _build_error_response(
        self,
        *,
        span: trace.Span,
        exc: Exception,
        context: str,
        answer: str,
        category: Literal["product", "faq", "complaint", "general", "out_of_scope"],
    ) -> AgentResponse:
        span.record_exception(exc)
        span.set_attribute("error.type", type(exc).__name__)
        span.set_attribute("error.context", context)
        return AgentResponse(
            answer=answer,
            confidence="low",
            category=category,
            requires_human=True,
        )

    def _handle_mixed_query(self, query: str, span: trace.Span) -> AgentResponse:
        try:
            product_answer = search_catalog_v1(query)
            faq_answer = get_faq_answer_v1(query)
            return AgentResponse(
                answer=f"{product_answer}\n{faq_answer}",
                confidence="medium",
                category="general",
                requires_human=False,
            )
        except Exception as exc:
            return self._build_error_response(
                span=span,
                exc=exc,
                context="mixed_tools",
                answer=(
                    "Tenemos una limitación temporal para consultar productos y políticas. "
                    "Te derivo con un agente humano."
                ),
                category="general",
            )

    def _handle_product_query(self, query: str, span: trace.Span) -> AgentResponse:
        try:
            return AgentResponse(
                answer=search_catalog_v1(query),
                confidence="medium",
                category="product",
                requires_human=False,
            )
        except Exception as exc:
            return self._build_error_response(
                span=span,
                exc=exc,
                context="search_catalog",
                answer=(
                    "No puedo consultar productos en este momento. "
                    "Inténtalo más tarde o te derivo con un agente humano."
                ),
                category="product",
            )

    def _handle_faq_query(self, query: str, span: trace.Span) -> AgentResponse:
        try:
            return AgentResponse(
                answer=get_faq_answer_v1(query),
                confidence="medium",
                category="faq",
                requires_human=False,
            )
        except Exception as exc:
            return self._build_error_response(
                span=span,
                exc=exc,
                context="get_faq_answer",
                answer=(
                    "No puedo consultar políticas de tienda en este momento. "
                    "Te derivo con un agente humano."
                ),
                category="faq",
            )

    def _handle_general_query(self, query: str, span: trace.Span) -> AgentResponse:
        try:
            return AgentResponse(
                answer=str(self.agent(query)),
                confidence="medium",
                category="general",
                requires_human=False,
            )
        except Exception as exc:
            return self._build_error_response(
                span=span,
                exc=exc,
                context="llm",
                answer=(
                    "Tengo una limitación temporal para procesar esta consulta. "
                    "Te derivo con un agente humano."
                ),
                category="general",
            )

    @observe(name="process_query")
    def process_query(
        self,
        user_query: str,
        user_id: str,
        session_id: str,
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
        with TRACER.start_as_current_span("agent.process_query") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("session.id", session_id)
            span.set_attribute("query.length", len(user_query))

            # 1. Input guardrails
            sanitized_query, is_safe, _input_metadata = self.guardrails.scan_input(user_query)

            if not is_safe:
                span.set_attribute("query.safe", False)
                return AgentResponse(
                    answer="Lo siento, no puedo procesar esa consulta.",
                    confidence="high",
                    category="out_of_scope",
                    requires_human=True,
                )

            span.set_attribute("query.safe", True)
            needs_product, needs_faq = classify_tool_intent(sanitized_query)
            span.set_attribute("routing.needs_product", needs_product)
            span.set_attribute("routing.needs_faq", needs_faq)

            if needs_product and needs_faq:
                response = self._handle_mixed_query(sanitized_query, span)
            elif needs_product:
                response = self._handle_product_query(sanitized_query, span)
            elif needs_faq:
                response = self._handle_faq_query(sanitized_query, span)
            elif is_store_context_query(sanitized_query):
                response = self._handle_general_query(sanitized_query, span)
            else:
                response = AgentResponse(
                    answer=(
                        "Esta consulta está fuera del alcance de TechShop. "
                        "Te derivo con un agente humano para continuar."
                    ),
                    confidence="low",
                    category="out_of_scope",
                    requires_human=True,
                )

            span.set_attribute("response.category", response.category)
            span.set_attribute("response.requires_human", response.requires_human)
            return response

        # 2. Invocar Strands Agent
        # TODO: Los alumnos añadirán manejo de errores y logging
        agent_response = self.agent(sanitized_query)
        response_text = str(agent_response)

        # 3. Output guardrails
        validated_answer, is_valid, _output_metadata = self.guardrails.scan_output(
            response_text, sanitized_query
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
