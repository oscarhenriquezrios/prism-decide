"""Synthesizer — combines agent verdicts into a decision matrix."""

from __future__ import annotations

from .types import AgentVerdict, DecisionCategory, DecisionMatrix


class Synthesizer:
    """Combines multiple agent verdicts into a final decision matrix."""

    def build_matrix(
        self,
        decision_text: str,
        options: list[str],
        verdicts: list[AgentVerdict],
        category: DecisionCategory = DecisionCategory.GENERAL,
    ) -> DecisionMatrix:
        """Build a complete decision matrix from all agent verdicts."""
        return DecisionMatrix(
            category=category,
            decision_text=decision_text,
            options=options,
            verdicts=verdicts,
        )

    def format_matrix(self, matrix: DecisionMatrix) -> str:
        """Format the decision matrix as visual panels."""
        from rich.box import HEAVY
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        if not matrix.options or not matrix.verdicts:
            console.print("[yellow]No hay datos para mostrar.[/]")
            return ""

        # ── Decision Header ──
        decision_text = matrix.decision_text[:80]
        if len(matrix.decision_text) > 80:
            decision_text += "…"

        console.print(Panel(
            f"[bold cyan]{decision_text}[/]",
            title="🔮  DECISIÓN",
            border_style="cyan",
            padding=(1, 3),
        ))
        console.print()

        # ── Category ──
        from .types import CATEGORY_LABELS
        cat_label = CATEGORY_LABELS.get(matrix.category, matrix.category.value)
        console.print(f"  [dim]📂 Categoría:[/] [bold]{cat_label}[/]")
        console.print()

        # ── Scores Table ──
        table = Table(
            title="🏆  MATRIZ DE PUNTUACIÓN",
            box=HEAVY,
            title_style="bold cyan",
            border_style="cyan",
            header_style="bold yellow",
            padding=(0, 2),
        )

        table.add_column("Agente", style="bold white", width=16)
        for opt in matrix.options:
            table.add_column(opt, justify="center", width=12)

        for v in matrix.verdicts:
            row = [f"{v.agent_icon} {v.agent_label}"]
            for opt in matrix.options:
                score = v.scores.get(opt, 0)
                if score >= 8:
                    style = "bold green"
                elif score >= 6:
                    style = "bold yellow"
                elif score >= 4:
                    style = "bold orange3"
                else:
                    style = "bold red"
                row.append(f"[{style}]{score}[/]")
            table.add_row(*row)

        # Totals row
        totals = matrix.totals
        total_row = ["🏆 TOTAL"]
        max_score = len(matrix.verdicts) * 10
        for opt in matrix.options:
            score = totals.get(opt, 0)
            pct = score / max_score if max_score else 0
            if pct >= 0.7:
                style = "bold green"
            elif pct >= 0.5:
                style = "bold yellow"
            else:
                style = "bold red"
            total_row.append(f"[{style}]{score}[/]")
        table.add_row(*total_row, style="bold")

        console.print(table)
        console.print()

        # ── Recommendation ──
        rec = matrix.get_recommendation()
        console.print(Panel(
            f"[bold green]{rec}[/]",
            title="🎯  RECOMENDACIÓN",
            border_style="green",
            padding=(1, 3),
        ))
        console.print()

        # ── Agent Reasoning ──
        for v in matrix.verdicts:
            scores = list(v.scores.values())
            avg = sum(scores) / len(scores) if scores else 0
            if avg >= 7:
                badge = "[bold green]👍[/]"
            elif avg >= 4:
                badge = "[bold yellow]🤷[/]"
            else:
                badge = "[bold red]👎[/]"

            score_line = "  ".join(f"{opt}: [bold]{v.scores.get(opt, '?')}[/]" for opt in matrix.options)
            console.print(Panel(
                f"{badge}  [bold]{v.agent_icon} {v.agent_label}[/]   [dim]{score_line}[/]\n\n[dim]{v.reasoning}[/]",
                border_style="blue",
                padding=(1, 2),
            ))
            console.print()

        return ""

    def format_json(self, matrix: DecisionMatrix) -> str:
        """Format the matrix as JSON (for --json flag)."""
        import json
        return json.dumps(matrix.model_dump(), indent=2, ensure_ascii=False)
