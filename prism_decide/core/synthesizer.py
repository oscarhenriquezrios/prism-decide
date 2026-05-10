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
        """Format the decision matrix as a readable text table."""
        if not matrix.options or not matrix.verdicts:
            return "No hay datos para mostrar."

        # Header
        opt_widths = [max(len(opt), 15) for opt in matrix.options]
        total_width = sum(opt_widths) + 25

        lines = []
        lines.append("┌" + "─" * total_width + "┐")
        lines.append(f"│ {'DECISIÓN:'} {' ' * (total_width - 10)}│")
        lines.append(f"│ {matrix.decision_text[:70]} {' ' * max(0, total_width - len(matrix.decision_text[:70]) - 1)}│")

        # Per-agent scores
        lines.append("├" + "─" * total_width + "┤")
        header = f"│ {'':>3} │"
        for opt in matrix.options:
            header += f" {opt:<{max(len(opt), 12)}} │"
        lines.append(header)

        lines.append("├" + "─" * total_width + "┤")

        for v in matrix.verdicts:
            row = f"│ {v.agent_icon} {v.agent_label:<12} │"
            for opt in matrix.options:
                score = v.scores.get(opt, 0)
                row += f" {score:^{max(len(opt), 12)}} │"
            lines.append(row)

        # Totals
        lines.append("├" + "─" * total_width + "┤")
        totals = matrix.totals
        row = f"│ {'🏆 TOTAL':<16} │"
        for opt in matrix.options:
            score = totals.get(opt, 0)
            row += f" {score:^{max(len(opt), 12)}} │"
        lines.append(row)
        lines.append("└" + "─" * total_width + "┘")

        # Recommendation
        lines.append("")
        lines.append(f"🎯 {matrix.get_recommendation()}")

        return "\n".join(lines)

    def format_json(self, matrix: DecisionMatrix) -> str:
        """Format the matrix as JSON (for --json flag)."""
        import json
        return json.dumps(matrix.model_dump(), indent=2, ensure_ascii=False)
