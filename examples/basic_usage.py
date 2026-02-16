"""Ejemplo básico de uso del agente TechShop."""

from __future__ import annotations

from techshop_agent import TechShopAgent


def main() -> None:
    """Ejemplo de uso básico del agente TechShop."""
    # Inicializar el agente con configuración por defecto
    agent = TechShopAgent()

    # Ejemplo 1: Consulta sobre productos
    print("=" * 80)
    print("Ejemplo 1: Consulta sobre productos")
    print("=" * 80)

    response = agent.process_query(
        user_query="¿Qué portátiles tenéis disponibles?",
        user_id="student01",
        session_id="session-001",
    )

    print(f"Respuesta: {response.answer}")
    print(f"Confianza: {response.confidence}")
    print(f"Categoría: {response.category}")
    print(f"Requiere humano: {response.requires_human}")

    # Ejemplo 2: Consulta sobre un pedido
    print("\n" + "=" * 80)
    print("Ejemplo 2: Consulta sobre pedido")
    print("=" * 80)

    response = agent.process_query(
        user_query="¿Cuál es el estado de mi pedido #12345?",
        user_id="student01",
        session_id="session-001",
    )

    print(f"Respuesta: {response.answer}")
    print(f"Confianza: {response.confidence}")
    print(f"Categoría: {response.category}")
    print(f"Requiere humano: {response.requires_human}")

    # Ejemplo 3: Consulta fuera de ámbito
    print("\n" + "=" * 80)
    print("Ejemplo 3: Consulta fuera de ámbito")
    print("=" * 80)

    response = agent.process_query(
        user_query="¿Cuál es el sentido de la vida?",
        user_id="student01",
        session_id="session-001",
    )

    print(f"Respuesta: {response.answer}")
    print(f"Confianza: {response.confidence}")
    print(f"Categoría: {response.category}")
    print(f"Requiere humano: {response.requires_human}")


if __name__ == "__main__":
    main()
