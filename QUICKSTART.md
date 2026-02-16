# Quickstart - TechShop Agent

Guía rápida para empezar a trabajar con el agente TechShop en 5 minutos.

## 1. Clonar y Configurar (2 min)

```bash
# Clonar el repositorio
git clone <repository-url>
cd techshop-agent

# Crear entorno virtual
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
uv pip install -e ".[dev]"
pre-commit install
```

## 2. Configurar Credenciales (2 min)

```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env con tus credenciales
notepad .env  # Windows
# nano .env  # Linux/Mac
```

Necesitas:
- **AWS_BEDROCK_API_KEY**: Obtener en [Bedrock Console](https://console.aws.amazon.com/bedrock) → API keys
- **LANGFUSE_PUBLIC_KEY** y **LANGFUSE_SECRET_KEY**: Proporcionados por el instructor
- **LANGFUSE_HOST**: URL de la instancia de Langfuse del curso

## 3. Habilitar Modelo en Bedrock (1 min)

1. Ir a [Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navegar a **Model access** → **Manage model access**
3. Habilitar **Claude Haiku 4.5**
4. Esperar 2-3 minutos

## 4. Verificar Instalación (30 seg)

```bash
# Ejecutar tests
make test

# Ejecutar ejemplo
make example
```

Si ves ✓ en los tests y respuestas del agente en el ejemplo, ¡estás listo!

## 5. Verificar Langfuse (30 seg)

1. Abrir Langfuse en el navegador: http://your-langfuse-instance:3000
2. Ir a **Traces**
3. Deberías ver las trazas del ejemplo que acabas de ejecutar

## Comandos Esenciales

```bash
make help          # Ver todos los comandos
make lint          # Verificar código
make format        # Formatear código
make test          # Ejecutar tests
make example       # Ejecutar ejemplo
```

## Estructura del Código

```python
# src/techshop_agent/agent.py - Agente principal
from strands import Agent, tool
from langfuse.decorators import observe

class TechShopAgent:
    @observe(name="process_query")
    def process_query(self, user_query: str, ...):
        # TODO: Los alumnos implementarán aquí
        pass
```

## TODOs del Curso

Busca comentarios `TODO` en el código:

```bash
# Buscar TODOs
rg "TODO" src/
```

### Día 1 - TODOs en `agent.py`:
- [ ] Mejorar system prompt
- [ ] Añadir metadata a trazas
- [ ] Implementar herramientas del agente
- [ ] Capturar tokens y costes

### Día 2 - TODOs en `guardrails.py`:
- [ ] Implementar input scanners
- [ ] Implementar output scanners
- [ ] Crear golden dataset
- [ ] Configurar promptfoo

### Día 3 - Crear archivos nuevos:
- [ ] `.github/workflows/ci.yml`
- [ ] `.github/workflows/deploy.yml`
- [ ] `template.yaml` (SAM)

## Troubleshooting Rápido

### Error: "Module 'strands' not found"
```bash
uv pip install -e ".[dev]"
```

### Error: "Access denied to model"
- Verificar que habilitaste Claude Haiku 4.5 en Bedrock Console
- Esperar 5-10 minutos para que se propague

### Error: "Langfuse credentials not configured"
```bash
# Verificar variables de entorno
echo $env:LANGFUSE_PUBLIC_KEY  # Windows PowerShell
# echo $LANGFUSE_PUBLIC_KEY  # Linux/Mac
```

### Pre-commit hooks fallan
```bash
make format  # Formatear automáticamente
git commit   # Intentar de nuevo
```

## Próximos Pasos

1. ✓ Setup completado
2. → Leer [README.md](README.md) para entender el proyecto
3. → Revisar [CONTRIBUTING.md](CONTRIBUTING.md) para convenciones
4. → Empezar con los ejercicios del Día 1

## Recursos Útiles

- [Documentación Strands](https://docs.strands.ai/)
- [Documentación Langfuse](https://langfuse.com/docs)
- [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## Soporte

Si tienes problemas:
1. Revisar [SETUP.md](SETUP.md) para troubleshooting detallado
2. Preguntar al instructor
3. Revisar los logs de error completos

---

**¡Listo para empezar! 🚀**

Ejecuta `make example` para ver el agente en acción.
