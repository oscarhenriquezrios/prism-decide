# Prism-Decide 🏛️🔮

**Multi-agent deliberation system for better decisions.**

Refracta una decisión en múltiples perspectivas, como un prisma refracta la luz.

```bash
pip install prism-decide
```

```bash
prism-decide "¿Debería cambiar de trabajo?"
```

## Philosophy

Una sola IA te da una respuesta. Un consejo de agentes especializados te da una **decisión informada**.

Prism-Decide reúne un "consejo" de agentes de IA, cada uno experto en un área distinta (financiero, riesgo, crecimiento, emocional...). Cada agente analiza la misma decisión desde su perspectiva sin ver a los otros. Luego el sistema sintetiza todo en una **matriz de decisión** con puntajes y recomendación.

## How it works

```
Tú: "¿Me cambio de trabajo?"
  │
  ▼ Clasificador: CARRERA (94%)
  │
  ▼ Consejo: 💰📈⚠️🧘 (4 agentes en paralelo)
  │
  ▼ Síntesis: Matriz de decisión + recomendación
```

## Project Status

🚧 **Early development** — MVP en construcción.

- [ ] Core engine (classifier, council, synthesizer)
- [ ] 5 base agents (financial, risk, growth, lifestyle, rational)
- [ ] CLI with Rich
- [ ] Dynamic agent generation
- [ ] PyPI release

## License

MIT
