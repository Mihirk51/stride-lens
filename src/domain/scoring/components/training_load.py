"""Training load scoring component."""

from src.domain.models.training_load_summary import TrainingLoadScore, TrainingLoadSummary


class TrainingLoadComponent:
    """
    Scores training load fatigue/readiness.

    Philosophy:
    - 1.0 = Fresh/underloaded (ready for hard training)
    - 0.5 = Appropriately loaded (normal training)
    - 0.0 = Overloaded/fatigued (high injury risk)

    Research basis:
    - ACWR optimal range: 0.8-1.3 (Gabbett, 2016)
    - Load ratio complements ACWR for progressive overload detection
    """

    def __init__(self):
        self.warnings: list[str] = []

    def calculate(self, load_summary: TrainingLoadSummary) -> TrainingLoadScore:
        """Calculate training load readiness score from 0-1."""
        self.warnings = []

        base_score = self._score_training_load(load_summary.acwr, load_summary.load_ratio)

        rest_penalty = self._calculate_rest_penalty(
            load_summary.days_since_last_run, load_summary.consecutive_training_days
        )

        final_score = max(0, min(1, base_score - rest_penalty))

        fatigue_level, interpretation = self._interpret_score(final_score, load_summary)

        return TrainingLoadScore(
            score=round(final_score, 3),
            fatigue_level=fatigue_level,
            interpretation=interpretation,
            warnings=self.warnings.copy(),
            summary=load_summary,
        )

    def _score_training_load(self, acwr: float, load_ratio: float) -> float:
        """
        Score training load using ACWR and load ratio together.

        Load ratio helps distinguish between:
        - Sharp spike (high ACWR, high load_ratio) = injury risk
        - Controlled progression (moderate ACWR, elevated load_ratio) = acceptable
        - Detraining (low ACWR, low load_ratio) = needs attention
        """
        if acwr == 0:
            return 0.5

        is_progressing = load_ratio > 1.1

        if acwr > 1.5:
            self.warnings.append("Very high acute:chronic ratio - elevated injury risk")
            penalty = min((acwr - 1.5) * 0.3, 0.6)
            return max(0, 0.6 - penalty)

        elif acwr > 1.3:
            if is_progressing and load_ratio <= 1.3:
                self.warnings.append("Elevated load but progressing gradually - monitor fatigue")
                return 0.75
            else:
                self.warnings.append("Elevated acute:chronic ratio - monitor fatigue")
                return 0.85 - (acwr - 1.3) / 0.2 * 0.25

        elif 0.8 <= acwr <= 1.0:
            if load_ratio > 1.3:
                self.warnings.append("Training volume significantly above baseline")
                return 0.8
            return 0.85 + (acwr - 0.8) / 0.2 * 0.15

        elif 1.0 < acwr <= 1.3:
            if is_progressing and load_ratio <= 1.3:
                return 0.95
            return 1.0 - (acwr - 1.0) / 0.3 * 0.15

        else:
            deficit = 0.8 - acwr
            if load_ratio < 0.9:
                self.warnings.append("Training volume below baseline - potential detraining")
            penalty = min(deficit * 0.5, 0.35)
            return max(0.5, 0.85 - penalty)

    def _calculate_rest_penalty(self, days_since_last_run: int, consecutive_days: int) -> float:
        """Calculate penalty for inadequate rest patterns (0-1 scale)."""
        penalty = 0

        if consecutive_days >= 14:
            penalty += 0.2
            self.warnings.append(f"{consecutive_days} consecutive training days - high fatigue risk")
        elif consecutive_days >= 10:
            penalty += 0.15
            self.warnings.append(f"{consecutive_days} consecutive training days - moderate fatigue risk")
        elif consecutive_days >= 7:
            penalty += 0.1
            self.warnings.append(f"{consecutive_days} consecutive training days - fatigue risk")

        if days_since_last_run > 14:
            penalty += 0.25
            self.warnings.append(f"No run in {days_since_last_run} days - significant detraining likely")
        elif days_since_last_run > 10:
            penalty += 0.15
            self.warnings.append(f"No run in {days_since_last_run} days - detraining may occur")
        elif days_since_last_run > 7:
            penalty += 0.1
            self.warnings.append(f"No run in {days_since_last_run} days - consider resuming training")

        return penalty

    @staticmethod
    def _interpret_score(score: float, load_summary: TrainingLoadSummary) -> tuple[str, str]:
        """Provide human-readable interpretation of training load score."""
        if score >= 0.85:
            if load_summary.acwr < 0.8:
                return "Fresh (Underloaded)", "Well-rested but training volume below baseline. Good for hard workouts."
            return "Fresh", "Optimal training load. Ready for quality sessions or long runs."

        elif score >= 0.7:
            if load_summary.load_ratio > 1.1:
                return "Moderate Fatigue", "Increased training load. Monitor recovery and consider easy runs."
            return "Normal", "Appropriate training load. Maintain current schedule."

        elif score >= 0.5:
            return (
                "Elevated Fatigue",
                "Higher fatigue accumulation. Prioritize recovery and reduce intensity.",
            )

        else:
            if load_summary.acwr > 1.5:
                return (
                    "High Fatigue (Injury Risk)",
                    "Acute spike in training load. Rest or very easy recovery recommended.",
                )
            return "High Fatigue", "Significant fatigue. Consider rest day or light cross-training."
