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


@click.group(invoke_without_command=True)
@click.option("--model", default=None, help="LLM model to use (default: from config or gpt-4o-mini)")
@click.option("--provider", default=None, help="Provider: openai, deepseek, openrouter, anthropic, ollama")
@click.option("--api-key", default="", help="API key (or set env var)")
@click.option("--verbose", "-v", is_flag=True, help="Show provider/model info")
@click.pass_context
def cli(ctx, model: Optional[str], provider: Optional[str], api_key: str, verbose: bool):
    """🏛️ Prism-Decide — Multi-agent deliberation for better decisions."""
    ctx.ensure_object(dict)

    # Load config file if available (silent fallback)
    cfg = {}
    try:
        cfg = load_config()
    except Exception:
        pass

    # Resolve provider
    resolved_provider = provider or cfg.get("provider", {}).get("default", "")
    # Auto-detect from env vars if not set
    if not resolved_provider:
        import os
        if os.environ.get("DEEPSEEK_API_KEY"):
            resolved_provider = "deepseek"
        elif os.environ.get("OPENAI_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
            resolved_provider = "openai"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            resolved_provider = "anthropic"
        elif os.environ.get("OPENROUTER_API_KEY"):
            resolved_provider = "openrouter"
        else:
            resolved_provider = "openai"

    # Resolve model
    if model:
        resolved_model = model
    else:
        provider_cfg = cfg.get("provider", {}).get(resolved_provider, {})
        resolved_model = provider_cfg.get("model", "")
        if not resolved_model:
            default_models = {
                "openai": "gpt-4o-mini",
                "deepseek": "deepseek-v4-flash",
                "openrouter": "deepseek/deepseek-v4-flash",
                "anthropic": "claude-sonnet-4-20250514",
                "ollama": "llama3",
            }
            resolved_model = default_models.get(resolved_provider, "gpt-4o-mini")

    # Resolve API key — check config file first, then env vars
    if not api_key:
        import os
        provider_cfg = cfg.get("provider", {}).get(resolved_provider, {})
        api_key = provider_cfg.get("api_key", "")
        if api_key.startswith("${") and api_key.endswith("}"):
            env_var = api_key[2:-1]
            api_key = os.environ.get(env_var, "")
        if not api_key:
            env_keys = {
                "deepseek": "DEEPSEEK_API_KEY",
                "openai": "OPENAI_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }
            env_var = env_keys.get(resolved_provider, "OPENAI_API_KEY")
            api_key = os.environ.get(env_var, "")

    ctx.obj["_provider_name"] = resolved_provider
    ctx.obj["_model_name"] = resolved_model
    ctx.obj["_verbose"] = verbose
    ctx.obj["provider"] = _get_provider(resolved_model, api_key)

    # If no subcommand was given, show the TUI
    if ctx.invoked_subcommand is None:
        _show_tui(ctx.obj)


def _show_tui(obj: dict):
    """Full-screen TUI: header, agents by category, question dialog."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    import questionary

    console = Console()
    provider = obj["provider"]
    provider_name = obj["_provider_name"]
    model_name = obj["_model_name"]

    key_status = "✓" if hasattr(provider, "_api_key") and provider._api_key else "✗"

    while True:
        console.clear()
        console.print()

        # ── LAST MODIFIED ──
        import subprocess
        try:
            last_modified = subprocess.run(
                ["git", "log", "-1", "--format=%ad", "--date=short"],
                capture_output=True, text=True, cwd=__file__ and None,
                timeout=5,
            ).stdout.strip()
            commit_msg = subprocess.run(
                ["git", "log", "-1", "--format=%s"],
                capture_output=True, text=True, cwd=__file__ and None,
                timeout=5,
            ).stdout.strip()[:60]
            modified_str = f"\n[dim]📅 {last_modified}  ·  {commit_msg}[/]"
        except Exception:
            modified_str = ""

        # ── HEADER ──
        console.print(Panel.fit(
            "[bold cyan]🔮  PRISM-DECIDE[/]\n\n"
            "[white]Sistema multi-agente de deliberación para tomar mejores decisiones.[/]\n"
            "[white]Cada decisión es analizada por múltiples agentes de IA expertos en[/]\n"
            "[white]distintas áreas (financiera, riesgo, crecimiento, estilo de vida, emocional).[/]\n\n"
            f"[dim]⚡ {provider_name}/{model_name}  ·  API key: {key_status}[/]"
            f"{modified_str}",
            border_style="cyan",
            padding=(1, 4),
        ))
        console.print()

        # ── AGENTS BY CATEGORY ──
        console.print("  [bold yellow]🧠  AGENTES DISPONIBLES POR CATEGORÍA[/]")
        console.print()

        from .categories.registry import list_categories, CATEGORY_AGENTS
        from .core.types import CATEGORY_LABELS
        from .agents import AGENT_MAP

        # Build category → agents display
        cat_table = Table(box=None, padding=(0, 2))
        cat_table.add_column("", width=20)
        cat_table.add_column("", width=50)

        for cat, agent_ids in CATEGORY_AGENTS.items():
            label = CATEGORY_LABELS.get(cat, cat.value)
            agents_str = "  ".join(
                f"{AGENT_MAP[aid].agent_icon} {AGENT_MAP[aid].agent_label}"
                for aid in agent_ids if aid in AGENT_MAP
            )
            cat_table.add_row(f"  {label}", agents_str)

        console.print(cat_table)
        console.print()

        # ── QUESTION INPUT ──
        console.print(Panel(
            "[yellow]💬[/]  [bold]¿Qué decisión quieres analizar?[/]\n\n"
            "[dim]Escribe tu situación o pregunta, por ejemplo:[/]\n"
            "[dim]\"¿Debería aceptar la oferta de trabajo en BCTecnología?\"[/]",
            border_style="yellow",
            padding=(1, 3),
        ))
        console.print()

        decision = questionary.text(
            "",
            qmark="▸",
            instruction="",
            style=questionary.Style([
                ("qmark", "fg:cyan bold"),
                ("text", "fg:white"),
            ]),
        ).ask()

        if decision is None:
            console.print("\n[red]✗[/]  Hasta luego!\n")
            return

        decision = decision.strip()
        if not decision:
            continue

        # ── DELIBERATION ──
        console.clear()
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🔮  ANALIZANDO…[/]\n\n"
            f"[white]{decision}[/]",
            border_style="cyan",
            padding=(1, 4),
        ))
        console.print()

        from .core.council import Council
        from .core.synthesizer import Synthesizer

        council = Council(provider)
        syn = Synthesizer()

        import time
        start = time.time()

        with console.status("  [dim]consultando agentes…[/]", spinner="dots"):
            matrix = council.deliberate(decision)

        elapsed = time.time() - start

        console.print()
        syn.format_matrix(matrix)
        console.print(f"[dim]{provider_name}/{model_name}  ·  ⏱ {elapsed:.1f}s[/]")
        console.print()

        # ── CONTINUE OR EXIT ──
        again = questionary.confirm(
            "¿Analizar otra decisión?",
            default=True,
            qmark="▸",
        ).ask()

        if not again:
            console.print("\n[cyan]✗[/]  Hasta luego!\n")
            return


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

    from rich.console import Console
    from rich.panel import Panel
    console = Console()

    import time
    start = time.time()

    console.print(Panel.fit(
        f"[bold cyan]🔮  PRISM-DECIDE[/]\n[white]{decision}[/]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()

    with console.status("  [dim]consultando agentes…[/]", spinner="dots"):
        matrix = council.deliberate(decision, agent_ids=agent_ids, options=explicit_options)

    elapsed = time.time() - start

    console.print()

    if json_output:
        click.echo(syn.format_json(matrix))
    else:
        syn.format_matrix(matrix)

    model_name = ctx.obj.get("_model_name", "")
    provider_name = ctx.obj.get("_provider_name", "")
    console.print(f"[dim]{provider_name}/{model_name}  ·  ⏱ {elapsed:.1f}s[/]")
    console.print()

    verbose = ctx.parent.params.get("verbose", False)
    if verbose:
        console.print(f"[dim]key set: {'✓' if hasattr(provider, '_api_key') and provider._api_key else '✗'}[/]")


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
    import questionary
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text

    console = Console()
    config_dir = Path.home() / ".config" / "prism-decide"
    config_path = config_dir / "config.yaml"

    console.clear()
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🔮  PRISM-DECIDE  ⚡  SETUP WIZARD[/]",
        border_style="cyan",
        padding=(1, 6),
    ))
    console.print()

    # ── Step 1: Provider ──
    console.print("[bold yellow]📡  PROVEEDOR DE IA[/]\n")

    provider = questionary.select(
        "¿Qué proveedor de LLM quieres usar?",
        choices=[
            questionary.Choice(
                title="🧊  DeepSeek     — Barato, rápido, modelo chino potente",
                value="deepseek",
            ),
            questionary.Choice(
                title="🟢  OpenAI       — GPT-4o, el estándar de la industria",
                value="openai",
            ),
            questionary.Choice(
                title="🟣  OpenRouter   — Gateway multi-modelo (DeepSeek, GPT, Claude…)",
                value="openrouter",
            ),
            questionary.Choice(
                title="🔴  Anthropic    — Claude Sonnet, énfasis en seguridad",
                value="anthropic",
            ),
            questionary.Choice(
                title="🟠  Ollama       — Modelos locales gratuitos (llama3, mistral…)",
                value="ollama",
            ),
        ],
        qmark="▸",
        style=questionary.Style([
            ("qmark", "fg:cyan bold"),
            ("question", "fg:white bold"),
            ("answer", "fg:cyan bold"),
            ("pointer", "fg:cyan bold"),
            ("highlighted", "fg:cyan bold"),
            ("selected", "fg:green bold"),
        ]),
    ).ask()

    if provider is None:
        console.print("[red]Setup cancelado.[/]")
        return

    # Provider config table
    provider_configs = {
        "deepseek": {
            "model": "deepseek-v4-flash",
            "models": [
                "deepseek-v4-flash",
                "deepseek-v4-pro",
                "deepseek-chat (obsoleto 24/07/2026)",
                "deepseek-reasoner (obsoleto 24/07/2026)",
            ],
            "base_url": "https://api.deepseek.com/v1",
            "env_key": "DEEPSEEK_API_KEY",
            "color": "cyan",
        },
        "openai": {
            "model": "gpt-4o-mini",
            "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            "base_url": "",
            "env_key": "OPENAI_API_KEY",
            "color": "green",
        },
        "openrouter": {
            "model": "deepseek/deepseek-v4-flash",
            "models": [
                "deepseek/deepseek-v4-flash",
                "deepseek/deepseek-v4-pro",
                "anthropic/claude-sonnet-4",
                "openai/gpt-4o",
                "deepseek/deepseek-chat (obsoleto 24/07/2026)",
            ],
            "base_url": "https://openrouter.ai/api/v1",
            "env_key": "OPENROUTER_API_KEY",
            "color": "magenta",
        },
        "anthropic": {
            "model": "claude-sonnet-4-20250514",
            "models": ["claude-sonnet-4-20250514", "claude-haiku-3-5", "claude-opus-4"],
            "base_url": "",
            "env_key": "ANTHROPIC_API_KEY",
            "color": "red",
        },
        "ollama": {
            "model": "llama3",
            "models": ["llama3", "llama3:70b", "mistral", "mixtral", "codellama"],
            "base_url": "http://localhost:11434/v1",
            "env_key": "",
            "color": "orange3",
        },
    }

    pconf = provider_configs[provider]

    # ── Step 2: Model ──
    console.print()
    console.print("[bold yellow]🎯  MODELO[/]\n")

    if provider == "ollama":
        model = questionary.text(
            "Modelo Ollama (ej: llama3, mistral, mixtral):",
            default=pconf["model"],
            qmark="▸",
            style=questionary.Style([("qmark", "fg:cyan bold"), ("question", "fg:white bold")]),
        ).ask()
    else:
        model_choices = []
        for m in pconf["models"]:
            if "obsoleto" in m:
                clean_name = m.split(" (")[0]
                display = f"  {clean_name}  —  ⚠️  OBSOLETO (24/07/2026)"
            else:
                clean_name = m
                display = f"  {clean_name}"
            model_choices.append(
                questionary.Choice(title=display, value=clean_name)
            )
        model = questionary.select(
            "Selecciona el modelo:",
            choices=model_choices,
            default=pconf["model"],
            qmark="▸",
            style=questionary.Style([
                ("qmark", "fg:cyan bold"),
                ("question", "fg:white bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan bold"),
            ]),
        ).ask()

    if model is None:
        console.print("[red]Setup cancelado.[/]")
        return

    # ── Step 3: API Key ──
    console.print()
    console.print("[bold yellow]🔑  API KEY[/]\n")

    if provider == "ollama":
        api_key = ""
        console.print("  [green]✅[/] Ollama corre localmente — no necesita API key")
    else:
        env_hint = pconf["env_key"]
        existing = os.environ.get(env_hint, "")
        if existing:
            console.print(f"  [blue]ℹ️[/] Variable [bold]{env_hint}[/] ya está en el entorno")
        use_env = questionary.confirm(
            "¿Usar variable de entorno?",
            default=bool(existing),
            qmark="▸",
        ).ask() if not existing else True

        if use_env is None:
            console.print("[red]Setup cancelado.[/]")
            return

        if use_env:
            api_key = f"${{{env_hint}}}"
        else:
            key = questionary.password(
                "Pega tu API key:",
                qmark="▸",
                style=questionary.Style([("qmark", "fg:cyan bold"), ("question", "fg:white bold")]),
            ).ask()
            if key is None:
                console.print("[red]Setup cancelado.[/]")
                return
            api_key = key

    # ── Step 4: Behavior ──
    console.print()
    console.print("[bold yellow]⚙️  COMPORTAMIENTO[/]\n")

    parallel = questionary.confirm(
        "¿Ejecutar agentes en paralelo? (más rápido)",
        default=True,
        qmark="▸",
    ).ask()

    if parallel is None:
        console.print("[red]Setup cancelado.[/]")
        return

    reasoning = questionary.confirm(
        "¿Mostrar razonamiento detallado de cada agente?",
        default=True,
        qmark="▸",
    ).ask()

    if reasoning is None:
        console.print("[red]Setup cancelado.[/]")
        return

    console.print()
    console.print("[bold yellow]🎨  APARIENCIA[/]\n")

    theme = questionary.select(
        "Tema de color:",
        choices=[
            questionary.Choice(title="🌙  Default     — Claro y profesional", value="default"),
            questionary.Choice(title="🌚  Dark        — Modo oscuro elegante", value="dark"),
            questionary.Choice(title="📄  Minimal     — Sin colores, solo texto", value="minimal"),
            questionary.Choice(title="🌈  High-Contrast — Accesible, colores vibrantes", value="high-contrast"),
        ],
        default="default",
        qmark="▸",
        style=questionary.Style([
            ("qmark", "fg:cyan bold"),
            ("question", "fg:white bold"),
            ("pointer", "fg:cyan bold"),
            ("highlighted", "fg:cyan bold"),
        ]),
    ).ask()

    if theme is None:
        console.print("[red]Setup cancelado.[/]")
        return

    # ── Build config ──
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

    # ── Write config ──
    config_dir.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    console.clear()
    console.print()
    console.print(Panel.fit(
        "[bold green]✅  CONFIGURACIÓN COMPLETADA[/]",
        border_style="green",
        padding=(1, 4),
    ))
    console.print()

    # Summary table
    from rich.table import Table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style="bold yellow", width=18)
    summary.add_column(style="white")

    provider_meta = provider_configs[provider]
    summary.add_row("📡 Proveedor", f"[{provider_meta['color']}]{provider}[/]")
    summary.add_row("🎯 Modelo", f"[{provider_meta['color']}]{model}[/]")
    summary.add_row("⚙️  Paralelo", "✅ Sí" if parallel else "❌ No")
    summary.add_row("📖 Razonamiento", "✅ Sí" if reasoning else "❌ No")
    summary.add_row("🎨 Tema", theme)

    console.print(summary)
    console.print()
    console.print(f"  [dim]Guardado en: {config_path}[/]")
    console.print()
    console.print("  [cyan]▶[/]  Ahora ejecuta:  [bold]prism-decide decide \"¿Debería…\"[/]")
    console.print()


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
