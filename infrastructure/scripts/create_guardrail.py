"""Create the TechShop Bedrock Guardrail and print the ID.

Usage:
    python infrastructure/scripts/create_guardrail.py

Requires:
    - AWS credentials configured (env vars, profile, or IAM role)
    - AWS_DEFAULT_REGION set (defaults to us-east-1)

The script creates a guardrail with:
    - Content filters: PROMPT_ATTACK (HIGH), INSULTS (MEDIUM), HATE (HIGH),
      SEXUAL (HIGH), VIOLENCE (HIGH), MISCONDUCT (MEDIUM)
    - Denied topics: cooking, sports, politics, health
    - Word policy: competitor brand names
    - Sensitive info: credit card, email, phone, AWS keys (BLOCK)

After creation, add the printed ID to your .env:
    BEDROCK_GUARDRAIL_ID=<id>
"""

from __future__ import annotations

import os
import sys

import boto3
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

COMPETITOR_BRANDS = [
    "apple", "samsung", "sony", "dell", "hp", "lenovo",
    "asus", "microsoft", "bose", "jbl", "google", "amazon",
    "iphone", "macbook", "galaxy", "pixel",
]


def create_guardrail() -> dict:
    """Create the TechShop guardrail and return the API response."""
    client = boto3.client("bedrock", region_name=REGION)

    response = client.create_guardrail(
        name="techshop-agent-guardrail",
        description="Guardrail para el agente TechShop — filtra prompt injection, "
        "PII, toxicidad, off-topic y marcas competidoras.",
        # ── Content filters ──────────────────────────────────────────────
        contentPolicyConfig={
            "filtersConfig": [
                {
                    "type": "PROMPT_ATTACK",
                    "inputStrength": "HIGH",
                    "outputStrength": "NONE",
                },
                {
                    "type": "INSULTS",
                    "inputStrength": "MEDIUM",
                    "outputStrength": "MEDIUM",
                },
                {
                    "type": "HATE",
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                },
                {
                    "type": "SEXUAL",
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                },
                {
                    "type": "VIOLENCE",
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                },
                {
                    "type": "MISCONDUCT",
                    "inputStrength": "MEDIUM",
                    "outputStrength": "MEDIUM",
                },
            ],
        },
        # ── Denied topics ────────────────────────────────────────────────
        topicPolicyConfig={
            "topicsConfig": [
                {
                    "name": "cooking",
                    "definition": "Preguntas sobre recetas, ingredientes, cocina o alimentacion.",
                    "type": "DENY",
                    "examples": [
                        "Cual es la mejor receta de paella?",
                        "Como se hace una tortilla de patatas?",
                    ],
                },
                {
                    "name": "sports",
                    "definition": "Preguntas sobre deportes, partidos, resultados o equipos.",
                    "type": "DENY",
                    "examples": [
                        "Quien gano la Champions League?",
                        "Cual es el mejor equipo de futbol?",
                    ],
                },
                {
                    "name": "politics",
                    "definition": "Preguntas sobre politica, elecciones, gobierno o partidos politicos.",
                    "type": "DENY",
                    "examples": [
                        "Quien es el presidente de Espana?",
                        "Que opinas de las proximas elecciones?",
                    ],
                },
                {
                    "name": "health",
                    "definition": "Preguntas sobre salud, sintomas, tratamientos o enfermedades.",
                    "type": "DENY",
                    "examples": [
                        "Tengo dolor de cabeza, que puedo tomar?",
                        "Cuales son los sintomas de la gripe?",
                    ],
                },
            ],
        },
        # ── Word policy (competitor brands) ──────────────────────────────
        wordPolicyConfig={
            "wordsConfig": [{"text": brand} for brand in COMPETITOR_BRANDS],
            "managedWordListsConfig": [{"type": "PROFANITY"}],
        },
        # ── Sensitive information (PII) ──────────────────────────────────
        sensitiveInformationPolicyConfig={
            "piiEntitiesConfig": [
                {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
                {"type": "EMAIL", "action": "BLOCK"},
                {"type": "PHONE", "action": "BLOCK"},
                {"type": "AWS_ACCESS_KEY", "action": "BLOCK"},
                {"type": "AWS_SECRET_KEY", "action": "BLOCK"},
            ],
        },
        # ── Blocked messages ─────────────────────────────────────────────
        blockedInputMessaging=(
            "Lo siento, no puedo procesar tu consulta por razones de seguridad. "
            "Por favor, reformula tu pregunta sobre productos o servicios de TechShop."
        ),
        blockedOutputsMessaging=(
            "Lo siento, no puedo proporcionar esa informacion en este momento. "
            "Puedo ayudarte con productos y servicios de TechShop."
        ),
    )
    return response


def main() -> None:
    print(f"Creando guardrail en region {REGION}...")
    try:
        response = create_guardrail()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    guardrail_id = response["guardrailId"]
    version = response["version"]
    arn = response["guardrailArn"]

    print()
    print("Guardrail creado:")
    print(f"  ID:      {guardrail_id}")
    print(f"  Version: {version}")
    print(f"  ARN:     {arn}")
    print()
    print("Agrega esto a tu .env:")
    print(f"  BEDROCK_GUARDRAIL_ID={guardrail_id}")
    print(f"  BEDROCK_GUARDRAIL_VERSION={version}")


if __name__ == "__main__":
    main()
