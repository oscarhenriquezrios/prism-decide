# Prism-Decide 🏛️🔮

**Multi-agent deliberation system for better decisions.**

Refracta una decisión en múltiples perspectivas, como un prisma refracta la luz.

---

## 1. Project Structure

```
prism-decide/
│
├── pyproject.toml              # Dependencias, metadata, entry points
├── README.md                   # Quick start + philosophy
├── LICENSE                     # MIT
├── .env.example                # LLM_API_KEY variables
│
├── prism_decide/               # Main package
│   ├── __init__.py
│   ├── __main__.py             # python -m prism_decide
│   ├── cli.py                  # CLI with Rich (TUI)
│   ├── config.py               # YAML config loader
│   │
│   ├── core/
│   │   ├── classifier.py       # Classifies decision → category
│   │   ├── council.py          # Orchestrator: selects + runs agents
│   │   ├── synthesizer.py      # Combines verdicts → matrix
│   │   ├── runner.py           # Parallel agent execution
│   │   └── types.py            # Pydantic models (shared types)
│   │
│   ├── agents/
│   │   ├── base.py             # Abstract base agent
│   │   ├── financial.py        # 💰
│   │   ├── risk.py             # ⚠️
│   │   ├── growth.py           # 📈
│   │   ├── lifestyle.py        # 🧘
│   │   ├── rational.py         # 🧠
│   │   ├── emotional.py        # ❤️
│   │   ├── prospective.py      # 🔮
│   │   ├── social.py           # 👥
│   │   ├── operational.py      # 📋
│   │   ├── health.py           # 🏃
│   │   ├── market.py           # 📊
│   │   └── ethical.py          # ⚖️
│   │
│   ├── categories/
│   │   ├── registry.py         # Category → agents mapping
│   │   └── definitions.py      # Each category definition
│   │
│   ├── dynamic/
│   │   └── generator.py        # Generates contextual agents on-the-fly
│   │
│   └── providers/
│       ├── base.py             # Abstract LLM provider
│       ├── openai.py           # OpenAI / OpenRouter compatible
│       ├── anthropic.py        # Anthropic Claude
│       └── ollama.py           # Local models
│
├── tests/
│   ├── test_classifier.py
│   ├── test_synthesizer.py
│   ├── test_agents.py
│   └── test_council.py
│
├── examples/
│   ├── career.md               # Example: job change decision
│   ├── business.md             # Example: launch product?
│   └── personal.md             # Example: relationship decision
│
└── docs/
    ├── index.md
    ├── architecture.md
    ├── agent-guide.md          # How to create a new agent
    └── contributing.md
```

---

## 2. Core Data Flow

```
User input (e.g. "¿Debería cambiar de trabajo?")
    │
    ▼
┌─────────────────────┐
│  1. CLASSIFIER      │  ← LLM call: clasifica la decisión
│                     │     Output: Category + confidence
│  "CARRERA (94%)"    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  2. REGISTRY        │  ← Mapa: Career → [Financial, Risk, Growth, Lifestyle]
│                     │     + 1 dynamic agent if applicable
│  [💰📈⚠️🧘] + 1 Dyn │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  3. COUNCIL         │  ← Spawns agents in parallel
│                     │     Each agent gets:
│  ┌───┐ ┌───┐ ┌───┐ │       - Decision text
│  │💰│ │📈│ │⚠️│ │       - Its persona prompt
│  └───┘ └───┘ └───┘ │       - Score rubric (1-10)
│         ...         │     Each returns: {score, reasoning, verdict}
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  4. SYNTHESIZER     │  ← Aggregates all verdicts
│                     │     Builds matrix
│  MATRIX + SUMMARY   │     Generates final recommendation
└─────────┬───────────┘
          │
          ▼
      USER OUTPUT
```

---

## 3. Types (Pydantic Models)

```python
# core/types.py

class DecisionCategory(str, Enum):
    CAREER = "career"
    BUSINESS = "business"
    PERSONAL = "personal"
    HEALTH = "health"
    EDUCATION = "education"
    FINANCE = "finance"
    GENERAL = "general"

class ClassifierResult(BaseModel):
    category: DecisionCategory
    confidence: float  # 0-1
    alternatives: list[str]  # alternative options detected
    context_summary: str     # 2-3 sentence summary of the decision

class AgentVerdict(BaseModel):
    agent_id: str           # "financial", "risk", etc.
    agent_label: str        # "💰 Financiero"
    score_a: int            # Score for option A (1-10)
    score_b: int            # Score for option B (1-10)
    score_a_label: str      # "Quedarme"
    score_b_label: str      # "Cambiarme"
    reasoning: str          # 2-3 paragraph analysis
    key_factors: list[str]  # Top 3 factors considered

class DecisionMatrix(BaseModel):
    category: DecisionCategory
    decision_text: str
    options: list[str]       # The alternatives (2+)
    verdicts: list[AgentVerdict]
    totals: list[int]        # Sum per option
    recommendation: str
    confidence: float         # Overall confidence
```

---

## 4. Agent System

### Base Agent

```python
# agents/base.py

class BaseAgent(ABC):
    agent_id: str           # "financial"
    agent_label: str        # "💰 Financiero"
    description: str        # "Evalúa impacto económico..."
    icon: str               # "💰"
    
    @abstractmethod
    def get_system_prompt(self, decision: str, context: dict) -> str:
        """Build the agent's persona + context prompt."""
        
    @abstractmethod
    def parse_response(self, llm_output: str) -> AgentVerdict:
        """Parse LLM response into structured verdict."""
```

### Example: Financial Agent

```python
# agents/financial.py

class FinancialAgent(BaseAgent):
    agent_id = "financial"
    agent_label = "💰 Financiero"
    icon = "💰"
    description = "Evalúa ingresos, costos, ROI y salud financiera"
    
    def get_system_prompt(self, decision, context):
        return f"""
Eres un ANALISTA FINANCIERO experto en evaluar decisiones desde la perspectiva económica.

Evalúa esta decisión:
"{decision}"

Las opciones son:
{chr(10).join(f'• {o}' for o in context['options'])}

Variables que DEBES considerar:
- Impacto en ingresos a corto, mediano y largo plazo
- Costos directos e indirectos
- Riesgo financiero
- ROI proyectado
- Impacto en ahorros / patrimonio
- Estabilidad financiera

Devuelve tu análisis en este formato JSON:
{{
  "scores": [{{
    "option": "opción A",
    "score": <1-10>,
    "rationale": "razonamiento corto"
  }}, ...],
  "reasoning": "análisis completo de 2-3 párrafos",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación final"
}}
"""
    
    def parse_response(self, llm_output):
        # Parse JSON from LLM → AgentVerdict
        ...
```

---

## 5. Classifier

```python
# core/classifier.py

CATEGORY_DEFINITIONS = {
    "career": {
        "keywords": ["trabajo", "cambio", "renuncia", "empleo", "carrera",
                     "job", "career", "resign", "offer", "salary"],
        "agent_ids": ["financial", "risk", "growth", "lifestyle"],
        "description": "Decisiones sobre empleo, cambio laboral o carrera"
    },
    "business": {
        "keywords": ["emprender", "negocio", "inversión", "startup",
                     "business", "startup", "invest", "launch"],
        "agent_ids": ["financial", "risk", "market", "operational"],
        "description": "Decisiones sobre negocios, emprendimiento o inversiones"
    },
    "personal": {
        "keywords": ["pareja", "relación", "mudanza", "familia",
                     "relationship", "partner", "move", "family"],
        "agent_ids": ["emotional", "rational", "prospective", "social"],
        "description": "Decisiones personales, relaciones o estilo de vida"
    },
    "health": {
        "keywords": ["salud", "médico", "tratamiento", "ejercicio",
                     "health", "medical", "treatment", "diet"],
        "agent_ids": ["health", "emotional", "social", "prospective"],
        "description": "Decisiones sobre salud, bienestar o hábitos"
    },
    "education": {
        "keywords": ["estudiar", "curso", "diplomado", "universidad",
                     "study", "course", "degree", "education"],
        "agent_ids": ["growth", "financial", "prospective", "risk"],
        "description": "Decisiones sobre educación o formación"
    },
    "finance": {
        "keywords": ["invertir", "ahorrar", "comprar", "deuda",
                     "invest", "save", "buy", "debt", "mortgage"],
        "agent_ids": ["financial", "risk", "prospective", "rational"],
        "description": "Decisiones financieras o de inversión"
    },
    "general": {
        "keywords": [],
        "agent_ids": ["rational", "prospective", "risk", "emotional"],
        "description": "Decisión general sin clasificación específica"
    }
}
```

The classifier works in two modes:
1. **Rule-based first** — keyword matching for fast classification
2. **LLM fallback** — if confidence < 70%, ask the LLM to classify

---

## 6. Council (Orchestrator)

```python
# core/council.py

class Council:
    """Orchestrates the multi-agent deliberation."""
    
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.agents = load_all_agents()
        self.categories = load_categories()
    
    def deliberate(self, decision: str) -> DecisionMatrix:
        # 1. Classify
        classifier = Classifier(self.provider)
        classification = classifier.classify(decision)
        
        # 2. Select agents
        agent_ids = self.categories[classification.category].agent_ids
        if classification.confidence < 0.8:
            # Add dynamic agent for low-confidence categories
            dynamic_agent = DynamicGenerator(self.provider).generate(...)
            agent_ids.append(dynamic_agent.agent_id)
        
        selected_agents = [a for a in self.agents if a.agent_id in agent_ids]
        
        # 3. Extract options from decision (use LLM)
        options = extract_options(decision, self.provider)
        
        # 4. Run agents in parallel
        context = {"options": options, "category": classification.category}
        verdicts = run_agents_parallel(selected_agents, decision, context)
        
        # 5. Synthesize
        synthesizer = Synthesizer()
        matrix = synthesizer.build_matrix(decision, options, verdicts)
        
        return matrix
```

---

## 7. Dynamic Agent Generator

```python
# dynamic/generator.py

class DynamicAgentGenerator:
    """
    Generates a contextual agent based on the decision's specifics.
    For example, if the decision is about a relationship, it might
    generate a "Patrones Históricos" agent that looks at recurring
    patterns in the relationship.
    """
    
    def generate(self, decision: str, category: str, options: list[str]) -> BaseAgent:
        """
        Uses an LLM to generate:
        - agent_id
        - agent_label + icon
        - description
        - system_prompt tailored to the decision
        
        Returns a DynamicAgent instance with the generated parameters.
        """
        prompt = f"""
        Dada esta decisión: "{decision}"
        Categoría: {category}
        Opciones: {options}
        
        Genera un agente de análisis ESPECÍFICO para esta situación.
        No puede ser uno de los agentes predefinidos.
        Debe aportar una perspectiva que los predefinidos no cubren.
        
        Responde en JSON:
        {{"agent_id": "...", "label": "...", "icon": "...",
          "description": "...", "system_prompt": "..."}}
        """
        
        response = self.provider.complete(prompt)
        agent_params = parse_dynamic_agent(response)
        return DynamicAgent(**agent_params)
```

---

## 8. Providers

```python
# providers/base.py

class BaseProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "", 
                 temperature: float = 0.7) -> str:
        """Send prompt to LLM and return response."""
    
    @abstractmethod
    def complete_json(self, prompt: str, system: str = "",
                      temperature: float = 0.3) -> dict:
        """Get structured JSON response from LLM."""
```

---

## 9. CLI

```python
# cli.py

"""
Usage:
    prism-decide "¿Debería cambiar de trabajo?"
    prism-decide "¿Debería invertir en esto?"
    echo "¿Debería mudarme?" | prism-decide
    
Options:
    --agents     List available agents
    --categories List available categories
    --config     Path to config file
    --json       Output as JSON
    --output     Save report to file
"""
```

Uses **Rich** for:
- Live progress display during agent deliberation
- Collapsible agent panels
- Color-coded matrix table
- ASCII art logo on startup

---

## 10. Configuration

```yaml
# ~/.config/prism-decide/config.yaml (default)

provider:
  default: openai
  openai:
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}
  anthropic:
    model: claude-sonnet-4
    api_key: ${ANTHROPIC_API_KEY}
  ollama:
    model: llama3
    endpoint: http://localhost:11434

behavior:
  parallel_agents: true       # Run agents concurrently
  max_dynamic_agents: 2       # Max generated agents
  show_reasoning: true         # Show full agent reasoning
  color_theme: "default"      # Rich theme

categories:
  # You can customize which agents per category
  career:
    agents: [financial, risk, growth, lifestyle]
```

---

## 11. pyproject.toml

```toml
[project]
name = "prism-decide"
version = "0.1.0"
description = "Multi-agent deliberation system for better decisions"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"

dependencies = [
    "rich>=13.0",
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "httpx>=0.27",
    "click>=8.0",
]

[project.scripts]
prism-decide = "prism_decide.cli:main"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "black", "ruff"]
```

---

## 12. Implementation Order (MVP)

Phase 1 — Core:
- [ ] `types.py` — Pydantic models
- [ ] `providers/base.py` + `openai.py` — LLM connection
- [ ] `agents/base.py` — Base agent class
- [ ] `core/classifier.py` — Decision classification
- [ ] `core/council.py` — Orchestrator
- [ ] `core/synthesizer.py` — Matrix builder
- [ ] `categories/registry.py` — Map categories → agents

Phase 2 — Agents (first pass):
- [ ] `agents/financial.py`
- [ ] `agents/risk.py`
- [ ] `agents/growth.py`
- [ ] `agents/lifestyle.py`
- [ ] `agents/rational.py`

Phase 3 — User interface:
- [ ] `cli.py` — CLI with Rich
- [ ] `config.py` — YAML config

Phase 4 — Polish:
- [ ] `dynamic/generator.py` — Dynamic agents
- [ ] More agents (emotional, prospective, social, market...)
- [ ] Tests
- [ ] Examples
- [ ] Docs
- [ ] Publish to PyPI
