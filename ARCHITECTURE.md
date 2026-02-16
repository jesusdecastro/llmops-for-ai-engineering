# Arquitectura del TechShop Agent

Este documento describe la arquitectura del agente TechShop y cómo interactúan sus componentes.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         Usuario / Cliente                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ user_query
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TechShopAgent                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              process_query() @observe                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │         1. Input Guardrails (GuardrailsManager)         │    │
│  │  • PromptInjection Scanner                              │    │
│  │  • PII Anonymization                                    │    │
│  │  • Toxicity Detection                                   │    │
│  │  • Secrets Detection                                    │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ sanitized_query                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         2. Strands Agent (Agent Framework)              │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │  System Prompt                                    │  │    │
│  │  │  • Rol y contexto                                 │  │    │
│  │  │  • Instrucciones de comportamiento               │  │    │
│  │  │  • Restricciones                                  │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                                                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │  Tools                                            │  │    │
│  │  │  • get_product_info()                             │  │    │
│  │  │  • check_order()                                  │  │    │
│  │  │  • [más herramientas...]                          │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                                                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │  BedrockModel                                     │  │    │
│  │  │  • model_id: claude-haiku-4-5                     │  │    │
│  │  │  • temperature: 0.3                               │  │    │
│  │  │  • max_tokens: 1024                               │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ agent_response                     │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         3. Output Guardrails (GuardrailsManager)        │    │
│  │  • Relevance Validation                                 │    │
│  │  • Topic Banning                                        │    │
│  │  • Format Validation                                    │    │
│  │  • Hallucination Detection                              │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ validated_response                 │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         4. Response Construction (AgentResponse)        │    │
│  │  • answer: str                                          │    │
│  │  • confidence: high/medium/low                          │    │
│  │  • category: product/complaint/general/out_of_scope     │    │
│  │  • requires_human: bool                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ AgentResponse
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Usuario / Cliente                        │
└─────────────────────────────────────────────────────────────────┘

                    Observabilidad (Langfuse)
┌─────────────────────────────────────────────────────────────────┐
│  Trace: process_query                                            │
│  ├─ Span: scan_input                                             │
│  │  └─ metadata: {scanners_passed, is_safe}                     │
│  ├─ Generation: bedrock_call                                     │
│  │  ├─ input_tokens: 150                                         │
│  │  ├─ output_tokens: 200                                        │
│  │  ├─ latency: 1.2s                                             │
│  │  └─ cost: $0.0003                                             │
│  └─ Span: scan_output                                            │
│     └─ metadata: {scanners_passed, is_valid}                    │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. TechShopAgent (Orquestador)

**Responsabilidad**: Coordinar el flujo completo de procesamiento de consultas.

**Componentes internos**:
- `AgentConfig`: Configuración centralizada
- `Langfuse`: Cliente de observabilidad
- `GuardrailsManager`: Gestor de guardrails
- `BedrockModel`: Modelo de AWS Bedrock
- `Agent`: Framework Strands Agent

**Métodos principales**:
- `process_query()`: Punto de entrada principal
- `_get_system_prompt()`: Genera el system prompt
- `_create_tools()`: Define las herramientas disponibles

### 2. Strands Agent (Framework Agentic)

**Responsabilidad**: Gestionar la interacción con el LLM y las herramientas.

**Características**:
- Gestión automática de herramientas
- Conversación con contexto
- Soporte multi-modelo
- Tool calling nativo

**Flujo interno**:
```
User Query → System Prompt + Tools → LLM Decision → Tool Execution → LLM Response
```

### 3. GuardrailsManager (Seguridad)

**Responsabilidad**: Validar y sanitizar inputs y outputs.

**Input Guardrails**:
- `PromptInjection`: Detecta intentos de jailbreak
- `Anonymize`: Redacta PII (emails, teléfonos, DNIs)
- `Toxicity`: Filtra contenido ofensivo
- `Secrets`: Detecta API keys, passwords

**Output Guardrails**:
- `Relevance`: Valida que la respuesta es relevante
- `BanTopics`: Bloquea temas prohibidos
- `Format`: Verifica formato esperado
- `FactualConsistency`: Detecta alucinaciones

### 4. Langfuse (Observabilidad)

**Responsabilidad**: Capturar y visualizar trazas de ejecución.

**Datos capturados**:
- Input/Output de cada paso
- Latencia por componente
- Tokens consumidos (input/output)
- Costes calculados
- Metadata personalizada
- Jerarquía de llamadas

**Estructura de trazas**:
```
Trace (process_query)
├── Span (scan_input)
├── Generation (bedrock_call)
│   ├── Prompt
│   ├── Completion
│   ├── Tokens
│   └── Cost
└── Span (scan_output)
```

## Flujo de Datos Detallado

### 1. Entrada del Usuario

```python
response = agent.process_query(
    user_query="¿Qué portátiles tenéis?",
    user_id="student01",
    session_id="session-123",
)
```

### 2. Input Guardrails

```python
# Escanear input
sanitized_query, is_safe, metadata = guardrails.scan_input(user_query)

# Si no es seguro, retornar respuesta de rechazo
if not is_safe:
    return AgentResponse(
        answer="Lo siento, no puedo procesar esa consulta.",
        confidence="high",
        category="out_of_scope",
        requires_human=True,
    )
```

### 3. Invocación del Agente

```python
# El agente decide automáticamente:
# 1. ¿Necesito usar herramientas?
# 2. ¿Qué herramienta(s) usar?
# 3. ¿Con qué parámetros?
# 4. ¿Cómo combinar los resultados?

agent_response = self.agent(sanitized_query)
```

**Ejemplo de decisión del agente**:
```
Query: "¿Qué portátiles tenéis?"
↓
Agent Decision: Usar tool get_product_info("portátiles")
↓
Tool Execution: get_product_info("portátiles") → "Tenemos 5 modelos..."
↓
Agent Response: "Actualmente tenemos 5 modelos de portátiles disponibles..."
```

### 4. Output Guardrails

```python
# Validar respuesta
validated_answer, is_valid, metadata = guardrails.scan_output(
    agent_response, sanitized_query
)

# Si no es válida, usar fallback
if not is_valid:
    return AgentResponse(
        answer="Lo siento, no puedo proporcionar esa información.",
        confidence="low",
        category="out_of_scope",
        requires_human=True,
    )
```

### 5. Construcción de Respuesta

```python
return AgentResponse(
    answer=validated_answer,
    confidence="medium",
    category="general",
    requires_human=False,
)
```

## Patrones de Diseño

### 1. Decorator Pattern (Observabilidad)

```python
@observe(name="process_query")
def process_query(self, user_query: str, ...) -> AgentResponse:
    # Langfuse captura automáticamente todo lo que ocurre aquí
    pass
```

**Ventajas**:
- Instrumentación no invasiva
- Separación de concerns
- Fácil de activar/desactivar

### 2. Strategy Pattern (Guardrails)

```python
class GuardrailsManager:
    def scan_input(self, query: str) -> tuple[str, bool, dict]:
        # Estrategia configurable de scanners
        if self.enable_input:
            # Aplicar scanners
            pass
```

**Ventajas**:
- Guardrails configurables
- Fácil añadir nuevos scanners
- Testeable independientemente

### 3. Builder Pattern (Agente)

```python
agent = Agent(
    model=model,
    tools=[tool1, tool2],
    system_prompt="...",
)
```

**Ventajas**:
- Configuración clara
- Validación en construcción
- Inmutable después de crear

### 4. Facade Pattern (TechShopAgent)

```python
class TechShopAgent:
    def process_query(self, ...):
        # Oculta la complejidad de:
        # - Guardrails
        # - Strands Agent
        # - Langfuse
        # - Validaciones
```

**Ventajas**:
- API simple para el usuario
- Complejidad encapsulada
- Fácil de usar y testear

## Configuración

### AgentConfig

```python
@dataclass
class AgentConfig:
    # AWS Bedrock
    aws_region: str = "us-east-1"
    model_id: str = "anthropic.claude-haiku-4-5-v1:0"
    max_tokens: int = 1024
    temperature: float = 0.3
    
    # Langfuse
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str
    
    # Guardrails
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True
```

### Variables de Entorno

```bash
# AWS
AWS_BEDROCK_API_KEY=xxx
AWS_REGION=us-east-1

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=http://localhost:3000
```

## Extensibilidad

### Añadir Nueva Herramienta

```python
@tool
def nueva_herramienta(param: str) -> str:
    """Descripción de la herramienta.
    
    Args:
        param: Descripción del parámetro
    """
    # Implementación
    return resultado

# Añadir a la lista de herramientas
tools = [get_product_info, check_order, nueva_herramienta]
```

### Añadir Nuevo Guardrail

```python
from llm_guard.input_scanners import CustomScanner

def scan_input(self, user_query: str):
    scanners = [
        PromptInjection(),
        Anonymize(),
        CustomScanner(),  # Nuevo scanner
    ]
    # Aplicar scanners...
```

### Cambiar Modelo

```python
# En config.py
model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0"

# O usar otro proveedor
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-sonnet-4-20250514",
    max_tokens=2048,
)
```

## Métricas y Monitorización

### Métricas Clave

1. **Latencia**:
   - P50, P95, P99 de `process_query()`
   - Latencia por componente (guardrails, LLM, tools)

2. **Costes**:
   - Coste por consulta
   - Coste por usuario
   - Coste por categoría de consulta

3. **Calidad**:
   - Tasa de respuestas que requieren humano
   - Distribución de confianza
   - Tasa de bloqueo por guardrails

4. **Uso**:
   - Consultas por minuto
   - Distribución de categorías
   - Herramientas más usadas

### Dashboard de Langfuse

```
┌─────────────────────────────────────────────────────────┐
│  Traces (últimas 24h)                                   │
│  ├─ Total: 1,234                                        │
│  ├─ Latencia media: 1.8s                                │
│  ├─ Coste total: $2.45                                  │
│  └─ Tasa de error: 0.5%                                 │
├─────────────────────────────────────────────────────────┤
│  Por Categoría                                          │
│  ├─ product: 45%                                        │
│  ├─ complaint: 30%                                      │
│  ├─ general: 20%                                        │
│  └─ out_of_scope: 5%                                    │
├─────────────────────────────────────────────────────────┤
│  Guardrails                                             │
│  ├─ Input bloqueados: 12 (1%)                           │
│  └─ Output bloqueados: 8 (0.6%)                         │
└─────────────────────────────────────────────────────────┘
```

## Seguridad

### Capas de Seguridad

1. **Input Validation**: Guardrails de entrada
2. **Output Validation**: Guardrails de salida
3. **API Keys**: Gestión segura de credenciales
4. **Rate Limiting**: Control de uso (futuro)
5. **Audit Logging**: Trazas completas en Langfuse

### Amenazas Mitigadas

- ✓ Prompt Injection
- ✓ PII Leakage
- ✓ Toxic Content
- ✓ Secret Exposure
- ✓ Off-topic Responses
- ✓ Hallucinations (parcial)

## Performance

### Optimizaciones

1. **Model Selection**: Haiku para tareas simples, Sonnet para complejas
2. **Token Optimization**: System prompts concisos
3. **Caching**: Respuestas similares (futuro)
4. **Streaming**: Respuestas progresivas (futuro)

### Benchmarks Esperados

- Latencia P95: < 3s
- Coste por consulta: $0.0003 - $0.001
- Throughput: 100 consultas/min (single instance)

## Testing

### Niveles de Testing

1. **Unit Tests**: Componentes individuales
2. **Integration Tests**: Flujo completo
3. **Evaluation Tests**: Golden dataset con promptfoo
4. **Red Team Tests**: Adversarial testing

### Cobertura

- Code Coverage: >80%
- Type Coverage: 100%
- Docstring Coverage: 100% (funciones públicas)

## Recursos

- [Strands Documentation](https://docs.strands.ai/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LLM Guard Documentation](https://llm-guard.com/)
