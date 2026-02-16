.PHONY: install dev lint format test clean pre-commit help

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala el paquete
	uv pip install -e .

dev:  ## Instala el paquete con dependencias de desarrollo
	uv pip install -e ".[dev]"
	pre-commit install

lint:  ## Ejecuta el linter (ruff check)
	ruff check src/ tests/ examples/

format:  ## Formatea el código (ruff format)
	ruff format src/ tests/ examples/

format-check:  ## Verifica el formato sin modificar
	ruff format --check src/ tests/ examples/

test:  ## Ejecuta los tests
	pytest tests/ -v

pre-commit:  ## Ejecuta pre-commit en todos los archivos
	pre-commit run --all-files

clean:  ## Limpia archivos generados
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

example:  ## Ejecuta el ejemplo básico
	python examples/basic_usage.py
