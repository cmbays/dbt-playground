"""
FS5 Scores Widget.

Displays adherence score, health pulse, and test metrics.
Implements FR-006 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass, field
from html import escape
from typing import Literal


@dataclass
class ScoresWidget:
    """Widget displaying score metrics.

    Attributes:
        adherence_score: Workflow adherence score (0-120)
        adherence_rating: Rating category
        adherence_breakdown: Component breakdown
        health_pulse: Health pulse score (0-100)
        health_components: Health component breakdown
        test_passed: Number of tests passing
        test_total: Total number of tests
        test_pass_rate: Pass rate percentage
    """

    adherence_score: int
    adherence_rating: Literal["EXCELLENT", "GOOD", "FAIR", "POOR"]
    adherence_breakdown: dict = field(default_factory=dict)
    health_pulse: int = 0
    health_components: dict = field(default_factory=dict)
    test_passed: int = 0
    test_total: int = 0
    test_pass_rate: float = 0.0

    @classmethod
    def from_adherence_score(
        cls,
        score,  # AdherenceScore from services
        health_pulse: int = 0,
        health_components: dict | None = None,
        test_results: dict | None = None,
    ) -> "ScoresWidget":
        """Create widget from AdherenceScore and optional health/test data.

        Args:
            score: AdherenceScore from calculate_adherence_score()
            health_pulse: Health pulse score (0-100)
            health_components: Health component breakdown
            test_results: Test results dict with passed, total, pass_rate

        Returns:
            ScoresWidget instance
        """
        # Build adherence breakdown
        breakdown = {
            "base_points": score.base_points,
            "completion_bonus": score.completion_bonus,
            "penalties": [
                {
                    "type": p.type,
                    "count": p.count,
                    "deducted": p.points_deducted,
                    "details": p.details,
                }
                for p in score.penalties
            ],
            "phases_completed": score.phases_completed,
        }

        # Get test results
        test_passed = 0
        test_total = 0
        test_pass_rate = 0.0
        if test_results:
            test_passed = test_results.get("passed", 0)
            test_total = test_results.get("total", 0)
            test_pass_rate = test_results.get("pass_rate", 0.0)

        return cls(
            adherence_score=score.final_score,
            adherence_rating=score.rating,
            adherence_breakdown=breakdown,
            health_pulse=health_pulse,
            health_components=health_components or {},
            test_passed=test_passed,
            test_total=test_total,
            test_pass_rate=test_pass_rate,
        )

    @classmethod
    def empty(cls) -> "ScoresWidget":
        """Create empty widget for new sessions."""
        return cls(
            adherence_score=0,
            adherence_rating="POOR",
            adherence_breakdown={},
            health_pulse=0,
            health_components={},
            test_passed=0,
            test_total=0,
            test_pass_rate=0.0,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "adherence_score": self.adherence_score,
            "adherence_rating": self.adherence_rating,
            "adherence_breakdown": self.adherence_breakdown,
            "health_pulse": self.health_pulse,
            "health_components": self.health_components,
            "test_passed": self.test_passed,
            "test_total": self.test_total,
            "test_pass_rate": self.test_pass_rate,
        }

    def _get_rating_color(self) -> str:
        """Get color for adherence rating."""
        return {
            "EXCELLENT": "green",
            "GOOD": "blue",
            "FAIR": "yellow",
            "POOR": "red",
        }.get(self.adherence_rating, "gray")

    def render_console(self) -> str:
        """Render widget for console output.

        Returns:
            Formatted string for terminal display
        """
        # Adherence bar
        adherence_filled = min(20, int(self.adherence_score / 6))  # 120 max, 20 chars
        adherence_bar = "█" * adherence_filled + "░" * (20 - adherence_filled)

        # Health bar
        health_filled = min(20, int(self.health_pulse / 5))  # 100 max, 20 chars
        health_bar = "█" * health_filled + "░" * (20 - health_filled)

        # Test bar
        test_filled = min(20, int(self.test_pass_rate / 5)) if self.test_total > 0 else 0
        test_bar = "█" * test_filled + "░" * (20 - test_filled)

        lines = [
            "┌─────────────────────────────────────┐",
            "│            SCORES                   │",
            "├─────────────────────────────────────┤",
            f"│ Adherence: {self.adherence_score:>3}/{120} [{adherence_bar}] │",
            f"│ Rating:    {self.adherence_rating:<24} │",
            "├─────────────────────────────────────┤",
            f"│ Health:    {self.health_pulse:>3}/100 [{health_bar}] │",
            "├─────────────────────────────────────┤",
            f"│ Tests:     {self.test_passed:>3}/{self.test_total:<3} [{test_bar}] │",
            f"│ Pass Rate: {self.test_pass_rate:.1f}%{' ' * 22}│",
            "└─────────────────────────────────────┘",
        ]
        return "\n".join(lines)

    def render_html(self) -> str:
        """Render widget as HTML fragment.

        Returns:
            HTML string for dashboard embedding
        """
        rating_class = f"rating-{self.adherence_rating.lower()}"

        # Generate penalty list with HTML escaping for security
        penalty_html = ""
        if self.adherence_breakdown.get("penalties"):
            penalty_items = []
            for p in self.adherence_breakdown["penalties"]:
                penalty_items.append(
                    f'<li class="penalty">{escape(str(p["type"]))}: -{p["deducted"]} ({escape(str(p["details"]))})</li>'
                )
            penalty_html = f"<ul class='penalty-list'>{''.join(penalty_items)}</ul>"

        return f"""
        <div class="widget scores-widget">
            <h3>Scores</h3>
            <div class="widget-content">
                <div class="score-row">
                    <div class="score-item">
                        <span class="score-label">Adherence</span>
                        <span class="score-value {rating_class}">{self.adherence_score}</span>
                        <span class="score-max">/120</span>
                        <progress value="{self.adherence_score}" max="120"></progress>
                        <span class="rating-badge {rating_class}">{self.adherence_rating}</span>
                    </div>
                </div>
                {penalty_html}
                <div class="score-row">
                    <div class="score-item">
                        <span class="score-label">Health Pulse</span>
                        <span class="score-value">{self.health_pulse}</span>
                        <span class="score-max">/100</span>
                        <progress value="{self.health_pulse}" max="100"></progress>
                    </div>
                </div>
                <div class="score-row">
                    <div class="score-item">
                        <span class="score-label">Tests</span>
                        <span class="score-value">{self.test_passed}/{self.test_total}</span>
                        <span class="score-max">({self.test_pass_rate:.1f}%)</span>
                        <progress value="{self.test_passed}" max="{max(self.test_total, 1)}"></progress>
                    </div>
                </div>
            </div>
        </div>
        """
