"""Basic usage example for the TechShop Agent.

Run with:
    uv run python examples/basic_usage.py

Requires environment variables (see .env.example):
    AWS_REGION           — AWS region for Bedrock (e.g. eu-west-1)
    AWS_PROFILE or       — AWS credentials (profile or key/secret)
    AWS_ACCESS_KEY_ID
    MODEL_ID             — optional, defaults to Claude Haiku 4.5
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from techshop_agent import create_agent  # noqa: E402

DEMO_QUERIES = [
    "¿Qué portátiles tenéis por menos de 1000 €?",
    "¿Cuál es la política de devoluciones?",
    "Recomiéndame un smartphone gama alta",
]


def main() -> None:
    print("🛒 TechShop Agent — Demo\n" + "=" * 40)
    agent = create_agent()

    for query in DEMO_QUERIES:
        print(f"\n👤 Usuario: {query}")
        response = agent(query)
        print(f"🤖 Alex: {response}")
        print("-" * 40)


if __name__ == "__main__":
    main()
