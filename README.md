<div align="center">
  <h1>🏛️ Prism-Decide</h1>
  <p><strong>Multi-agent deliberation system for better decisions.</strong></p>
  <p><em>Refracta una decisión en múltiples perspectivas, como un prisma refracta la luz.</em></p>

  <p>
    <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
    <img src="https://img.shields.io/badge/agents-12-brightgreen" alt="12 Agents">
  </p>

  <pre>pip install prism-decide</pre>

  <pre>prism-decide decide "¿Debería cambiar de trabajo?"</pre>

  <p><em>O simplemente:</em></p>

  <pre>prism-decide</pre>

</div>

---

## ✨ Features

- **12 Expert Agents** — cada decisión analizada por múltiples especialistas desde distintas perspectivas
- **Interactive TUI** — pantalla completa con menús, sin argumentos (solo `prism-decide`)
- **Setup Wizard** — configuración guiada con flechas del teclado
- **Multi-provider** — DeepSeek, OpenAI, OpenRouter, Anthropic, Ollama
- **Rich Visual Output** — tablas coloreadas, paneles, razonamiento completo
- **CLI + TUI** — modo rápido (`decide "..."`) o modo interactivo (sin argumentos)

## 🤖 Agentes

| Icon | Agente | Área |
|------|--------|------|
| 💰 | Financiero | Ingresos, costos, ROI y salud financiera |
| 📈 | Crecimiento | Aprendizaje, desarrollo profesional, proyección |
| ⚠️ | Riesgo | Contingencias, downsides, planes B |
| 🧘 | Estilo de Vida | Equilibrio, estrés, flexibilidad |
| ❤️ | Emocional | Sentimientos, valores, felicidad |
| 📊 | Mercado | Dinámicas de mercado, competencia, demanda |
| ⚙️ | Operativo | Factibilidad, logística, recursos |
| 👥 | Social | Relaciones, reputación, comunidad |
| 🔭 | Prospectivo | Escenarios futuros, tendencias, disrupción |
| 💚 | Salud | Impacto físico, mental y bienestar |
| ⚖️ | Ético | Implicaciones morales, principios, valores |
| 🧠 | Racional | Lógica pura, datos objetivos, trade-offs |

## 🧠 Cómo funciona

```
Tú: "¿Me cambio de trabajo?"
  │
  ▼ Clasificador automático → CARRERA (94%)
  │
  ▼ Consejo de 8 agentes (en paralelo)
  │  💰 Financiero  📈 Crecimiento  ⚠️ Riesgo  🧘 Estilo Vida
  │  📊 Mercado     🔭 Prospectivo  👥 Social  🧠 Racional
  │
  ▼ Síntesis: Matriz de decisión + recomendación
```

Cada agente delibera **sin ver a los otros** (evita sesgo grupal). El sistema sintetiza todo en una matriz de puntuación con colores y recomendación final.

## 🚀 Quick Start

### 1. Instalar

```bash
git clone https://github.com/oscarhenriquezrios/prism-decide.git
cd prism-decide
pip install -e .
```

### 2. Configurar (opcional)

```bash
prism-decide setup
```

Te guía paso a paso: proveedor, modelo, API key, preferencias.

### 3. Usar

**Modo interactivo (recomendado):**
```bash
prism-decide
```
Abre la interfaz completa: header, agentes por categoría, cuadro de diálogo para escribir tu pregunta.

**Modo rápido (CLI):**
```bash
prism-decide decide "¿Debería aceptar la nueva oferta laboral?"
```

**Con opciones personalizadas:**
```bash
prism-decide decide "¿Me cambio de trabajo?" \
  --options "Quedarme en mi empleo actual" \
  --options "Irme a la nueva empresa"
```

**Seleccionar agentes específicos:**
```bash
prism-decide decide "¿Debería mudarme a otra ciudad?" \
  --agents lifestyle --agents financial --agents social
```

**Output como JSON:**
```bash
prism-decide decide "¿Debería?" --json
```

## 📡 Proveedores Soportados

| Proveedor | Modelo por defecto | Variable de entorno |
|-----------|-------------------|-------------------|
| 🧊 DeepSeek | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` |
| 🟢 OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| 🟣 OpenRouter | `deepseek/deepseek-v4-flash` | `OPENROUTER_API_KEY` |
| 🔴 Anthropic | `claude-sonnet-4` | `ANTHROPIC_API_KEY` |
| 🟠 Ollama (local) | `llama3` | — |

Forzar proveedor:
```bash
prism-decide --provider deepseek decide "¿Debería?"
prism-decide -v decide "¿Debería?"   # verbose: muestra modelo + API key status
```

## 📂 Categorías de Decisión

| Categoría | Agentes asignados |
|-----------|------------------|
| 💼 Carrera | Financiero, Riesgo, Crecimiento, Estilo Vida, Mercado, Prospectivo, Social, Racional |
| 🏢 Negocio | Financiero, Riesgo, Crecimiento, Emocional, Mercado, Operativo, Ético, Prospectivo |
| ❤️ Personal | Emocional, Riesgo, Estilo Vida, Financiero, Social, Salud, Ético, Racional |
| 🏥 Salud | Estilo Vida, Emocional, Riesgo, Crecimiento, Salud, Social, Racional, Prospectivo |
| 🎓 Educación | Crecimiento, Financiero, Riesgo, Estilo Vida, Prospectivo, Mercado, Racional, Social |
| 💰 Finanzas | Financiero, Riesgo, Crecimiento, Emocional, Mercado, Operativo, Racional, Prospectivo |
| 📌 General | Todos los 12 agentes |

## 🏗️ Arquitectura

```
prism-decide/
├── prism_decide/
│   ├── agents/           # 12 agentes especializados
│   ├── categories/       # Mapeo decisión → agentes
│   ├── core/             # Classifier, Council, Synthesizer
│   ├── providers/        # OpenAI, Anthropic (interfaz común)
│   ├── cli.py            # CLI + TUI con Rich + Questionary
│   └── config.py         # Config YAML + env vars
└── tests/
```

## 📜 License

MIT — haz lo que quieras, pero si haces algo interesante, cuéntanos.
