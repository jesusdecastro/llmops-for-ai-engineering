# Guía de contribución

## Flujo recomendado

1. Crea una rama por cambio.
2. Implementa cambios pequeños y verificables.
3. Ejecuta pruebas y linters antes de abrir PR.
4. Describe claramente alcance, impacto y validaciones en la PR.

## Estándares mínimos

- Mantener tipado y estilo consistente con el proyecto.
- Evitar cambios no relacionados con el objetivo de la tarea.
- Documentar cambios funcionales en `docs/` cuando corresponda.

## Validación local

```bash
make lint
make test
```

## Convención de documentación

- La documentación vive bajo `docs/` con estructura temática.
- El `README.md` de la raíz se mantiene como punto de entrada.
