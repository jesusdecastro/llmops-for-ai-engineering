.PHONY: install dev lint format format-check typecheck test security tf-fmt tf-validate tf-check qa clean pre-commit streamlit streamlit-install help

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala el paquete
	uv sync --no-dev

dev:  ## Instala el paquete con dependencias de desarrollo
	uv sync
	uv run pre-commit install

lint:  ## Ejecuta el linter (ruff check)
	uv run ruff check src/ tests/ examples/

format:  ## Formatea el código (ruff format)
	uv run ruff format src/ tests/ examples/

format-check:  ## Verifica el formato sin modificar
	uv run ruff format --check src/ tests/ examples/

typecheck:  ## Ejecuta type checking (pyright)
	uv run pyright src/techshop_agent

test:  ## Ejecuta los tests
	uv run pytest tests/ -v

security:  ## Ejecuta checks de seguridad en Python
	uv run bandit -q -r src/techshop_agent

tf-fmt:  ## Verifica formato Terraform
	terraform -chdir=infrastructure/terraform fmt -recursive -check

tf-validate:  ## Valida Terraform
	terraform -chdir=infrastructure/terraform init -backend=false
	terraform -chdir=infrastructure/terraform validate

tf-check: tf-fmt tf-validate  ## Ejecuta checks Terraform

qa: lint format-check typecheck test security  ## Ejecuta quality gates de Python

pre-commit:  ## Ejecuta pre-commit en todos los archivos
	uv run pre-commit run --all-files

clean:  ## Limpia archivos generados
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

example:  ## Ejecuta el ejemplo básico
	uv run python examples/basic_usage.py

streamlit-install:  ## Instala las dependencias de la UI Streamlit
	cd streamlit_app && uv sync

streamlit:  ## Arranca la interfaz Streamlit del agente (puerto 8501)
	cd streamlit_app && uv run streamlit run app.py --server.port 8501
