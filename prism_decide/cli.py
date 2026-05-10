"""Prism-Decide CLI — terminal interface with Rich."""

from __future__ import annotations

import sys
from typing import Optional

import click

from .agents import list_available_agents
from .categories.registry import list_categories
from .core.council import Council
from .core.synthesizer import Synthesizer
from .core.types import CATEGORY_LABELS, DecisionCategory
from .providers.openai import OpenAIProvider


def _get_provider(model: str, api_key: str):
    """Get the appropriate LLM provider."""
    if not api_key:
        # Try to read from env
        import os
        api_key = os.environ.get("OPENAI_API_KEY", "")

    if model.startswith("gpt") or "openai" in model or not model:
        return OpenAIProvider(model=model or "gpt-4o-mini", api_key=api_key)
    elif model.startswith("claude") or "anthropic" in model:
        from .providers.anthropic import AnthropicProvider
        return AnthropicProvider(model=model, api_key=api_key)
    else:
        # Default to OpenAI-compatible
        return OpenAIProvider(model=model, api_key=api_key)


@click.group()
@click.option("--model", default="gpt-4o-mini", help="LLM model to use")
@click.option("--api-key", default="", help="API key (or set OPENAI_API_KEY env)")
@click.pass_context
def cli(ctx, model: str, api_key: str):
    """🏛️ Prism-Decide — Multi-agent deliberation for better decisions."""
    ctx.ensure_object(dict)
    ctx.obj["provider"] = _get_provider(model, api_key)


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
