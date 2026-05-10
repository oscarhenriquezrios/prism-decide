"""Prism-Decide CLI — terminal interface with Rich."""

from __future__ import annotations

import sys
from typing import Optional

import click

from .agents import list_available_agents
from .categories.registry import list_categories
from .config import load_config
from .core.council import Council
from .core.synthesizer import Synthesizer
from .core.types import CATEGORY_LABELS, DecisionCategory
from .providers.openai import OpenAIProvider


def _get_provider(model: str, api_key: str):
    """Get the appropriate LLM provider."""
    if not api_key:
        import os
        api_key = os.environ.get("OPENAI_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")

    model_lower = model.lower()

    if "deepseek" in model_lower:
        return OpenAIProvider(model=model or "deepseek-chat", api_key=api_key,
                              base_url="https://api.deepseek.com/v1")
    elif "openrouter" in model_lower or model.startswith("openai/"):
        return OpenAIProvider(model=model, api_key=api_key,
                              base_url="https://openrouter.ai/api/v1")
    elif model.startswith("gpt") or "openai" in model or not model:
        return OpenAIProvider(model=model or "gpt-4o-mini", api_key=api_key)
    elif "claude" in model_lower or "anthropic" in model_lower:
        from .providers.anthropic import AnthropicProvider
        return AnthropicProvider(model=model, api_key=api_key)
    else:
        return OpenAIProvider(model=model, api_key=api_key)


@click.group()
@click.option("--model", default=None, help="LLM model to use")
@click.option("--api-key", default="", help="API key (or set env var)")
@click.pass_context
def cli(ctx, model: Optional[str], api_key: str):
    """🏛️ Prism-Decide — Multi-agent deliberation for better decisions."""
    ctx.ensure_object(dict)

    # Load config file if available (silent fallback)
    cfg = {}
    try:
        cfg = load_config()
    except Exception:
        pass

    resolved_model = model or cfg.get("provider", {}).get(cfg.get("provider", {}).get("default", "openai"), {}).get("model", "gpt-4o-mini")
    if not api_key:
        import os
        api_key = os.environ.get("OPENAI_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")

    ctx.obj["provider"] = _get_provider(resolved_model, api_key)


@cli.command()
@click.argument("decision", required=False)
@click.option("--options", "-o", multiple=True, help="Override options (use multiple times)")
@click.option("--agents", "-a", multiple=True, help="Override agents (use multiple times)")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.pass_context
def decide(ctx, decision: Optional[str], options, agents, json_output):
    """Analyze a decision using multiple AI agents.

    DECISION is the question you want to analyze, e.g.:
    "¿Debería cambiar de trabajo?"
    "¿Me conviene emprender o seguir empleado?"
    """
    if not decision:
        decision = _read_stdin()
    if not decision:
        click.echo("Error: You must provide a decision.")
        sys.exit(1)

    provider = ctx.obj["provider"]
    council = Council(provider)
    syn = Synthesizer()

    agent_ids = list(agents) if agents else None
    explicit_options = list(options) if options else None

    click.echo()
    click.echo("🔮  PRISM-DECIDE")
    click.echo("━" * 40)
    click.echo()

    with click.progressbar(
        length=1,
        label="🧠 Reuniendo el consejo...",
        show_eta=False,
        show_percent=False,
    ) as bar:
        matrix = council.deliberate(decision, agent_ids=agent_ids, options=explicit_options)
        bar.update(1)

    click.echo()
    click.echo(f"📂 Categoría: {CATEGORY_LABELS.get(matrix.category, matrix.category.value)}")
    click.echo()

    if json_output:
        click.echo(syn.format_json(matrix))
    else:
        click.echo(syn.format_matrix(matrix))

    click.echo()


@cli.command("list-agents")
def list_agents():
    """List all available agents."""
    click.echo("\n🧑‍⚖️  AGENTES DISPONIBLES\n")
    for a in list_available_agents():
        click.echo(f"  {a['icon']} {a['label']:<20} — {a['description']}")
    click.echo()


@cli.command()
@click.pass_context
def setup(ctx):
    """🔧 Interactive setup — configure providers, models, and preferences."""
    import os
    from pathlib import Path

    config_dir = Path.home() / ".config" / "prism-decide"
    config_path = config_dir / "config.yaml"

    click.echo()
    click.echo("╔══════════════════════════════════════╗")
    click.echo("║   🔮  PRISM-DECIDE SETUP WIZARD      ║")
    click.echo("╚══════════════════════════════════════╝")
    click.echo()

    # --- Step 1: Default provider ---
    click.echo("📡  PROVEEDOR PRINCIPAL")
    click.echo()
    provider = click.prompt(
        "¿Qué proveedor de LLM quieres usar por defecto?",
        type=click.Choice(["openai", "deepseek", "openrouter", "anthropic", "ollama"], case_sensitive=False),
        default="deepseek",
        show_choices=True,
    )

    provider_configs = {
        "openai": {"model": "gpt-4o-mini", "base_url": "", "env_key": "OPENAI_API_KEY"},
        "deepseek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1", "env_key": "DEEPSEEK_API_KEY"},
        "openrouter": {"model": "openai/deepseek-chat", "base_url": "https://openrouter.ai/api/v1", "env_key": "OPENROUTER_API_KEY"},
        "anthropic": {"model": "claude-sonnet-4-20250514", "base_url": "", "env_key": "ANTHROPIC_API_KEY"},
        "ollama": {"model": "llama3", "base_url": "http://localhost:11434/v1", "env_key": ""},
    }

    pconf = provider_configs[provider]
    click.echo(f"\n  → Modelo sugerido: {pconf['model']}")
    if provider != "ollama":
        model = click.prompt("  Modelo a usar", default=pconf["model"])
    else:
        model = click.prompt("  Modelo Ollama (ej: llama3, mistral)", default=pconf["model"])

    # --- Step 2: API Key ---
    click.echo()
    if provider == "ollama":
        api_key = ""
        click.echo("  ✅ Ollama corre local — no necesita API key")
    else:
        env_hint = pconf["env_key"]
        existing = os.environ.get(env_hint, "")
        if existing:
            click.echo(f"  ℹ️  Variable {env_hint} ya está configurada en el entorno")
        key = click.prompt(
            f"  API Key (se guardará en ~/.config/prism-decide/config.yaml)",
            default="",
            hide_input=True,
        )
        api_key = key or f"${{{env_hint}}}"

    # --- Step 3: Behavior defaults ---
    click.echo()
    click.echo("⚙️  COMPORTAMIENTO")
    click.echo()
    parallel = click.confirm("  ¿Ejecutar agentes en paralelo?", default=True)
    reasoning = click.confirm("  ¿Mostrar razonamiento detallado de cada agente?", default=True)

    click.echo()
    click.echo("🎨  APARIENCIA")
    theme = click.prompt(
        "  Tema de color",
        type=click.Choice(["default", "dark", "minimal", "high-contrast"], case_sensitive=False),
        default="default",
        show_choices=True,
    )

    # --- Build config ---
    config = {
        "provider": {
            "default": provider,
            provider: {
                "model": model,
                "api_key": api_key,
            },
        },
        "behavior": {
            "parallel_agents": parallel,
            "show_reasoning": reasoning,
            "color_theme": theme,
        },
    }

    if provider == "ollama":
        config["provider"][provider].pop("api_key", None)

    if pconf["base_url"] and provider != "openai":
        config["provider"][provider]["base_url"] = pconf["base_url"]

    # --- Write config ---
    config_dir.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    click.echo()
    click.echo("━" * 40)
    click.echo(f"✅  Configuración guardada en:")
    click.echo(f"   {config_path}")
    click.echo()
    click.echo("📋  Resumen:")
    click.echo(f"   Proveedor:    {provider}")
    click.echo(f"   Modelo:       {model}")
    click.echo(f"   Paralelo:     {'Sí' if parallel else 'No'}")
    click.echo(f"   Razonamiento: {'Sí' if reasoning else 'No'}")
    click.echo(f"   Tema:         {theme}")
    click.echo()
    click.echo("▶️  Ahora puedes ejecutar:")
    click.echo(f"   prism-decide decide \"¿Debería...\"")
    click.echo()


@cli.command("list-categories")
def list_categories_cmd():
    """List all decision categories."""
    click.echo("\n📂 CATEGORÍAS DE DECISIÓN\n")
    for c in list_categories():
        agents_fmt = ", ".join(c["agents"])
        click.echo(f"  {c['label']:<25} → {agents_fmt}")
    click.echo()


@cli.command()
def version():
    """Show version."""
    from importlib.metadata import version as get_version
    try:
        ver = get_version("prism-decide")
    except Exception:
        ver = "0.1.0 (dev)"
    click.echo(f"Prism-Decide v{ver}")


def _read_stdin() -> str:
    """Read decision from stdin (pipe mode)."""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def main():
    """Entry point for console scripts."""
    cli(obj={})


if __name__ == "__main__":
    main()
