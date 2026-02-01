"""Training load scoring component."""

from pydantic import BaseModel, Field

from src.domain.models.training_load_summary import TrainingLoadSummary


class TrainingLoadScore(BaseModel):
    """Result of training load scoring."""

    score: float = Field(..., ge=0, le=1, description="Training load score (0-1)")
    fatigue_level: str = Field(..., description="Human-readable fatigue level")
    interpretation: str = Field(..., description="Detailed interpretation of current state")
    warnings: list[str] = Field(default_factory=list, description="Actionable warnings")

    summary: TrainingLoadSummary = Field(..., description="Underlying training load data")


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

        base_score = self._score_training_load(
            load_summary.acwr, load_summary.load_ratio, load_summary.days_since_last_run
        )

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

    def _score_training_load(self, acwr: float, load_ratio: float, days_since_last_run: int) -> float:
        """
        Score training load using ACWR and load ratio together.

        Load ratio helps distinguish between:
        - Sharp spike (high ACWR, high load_ratio) = injury risk
        - Controlled progression (moderate ACWR, elevated load_ratio) = acceptable
        - Intentional deload (low ACWR, low load_ratio, recent activity) = recovery week, well-rested
        - Unintentional detraining (low ACWR, low load_ratio, long gap) = needs attention
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
            # ACWR < 0.8 (below baseline)
            # Use days_since_last_run to distinguish intentional recovery from detraining
            if load_ratio < 0.7:
                # Both metrics low - check recency of activity
                if days_since_last_run <= 4:
                    # Still actively training, just reduced volume = intentional recovery
                    self.warnings.append("Recovery week detected - reduced training volume")
                    return min(1.0, 0.92 + (0.7 - load_ratio) * 0.2)
                else:
                    # Long gap + low volume = detraining
                    self.warnings.append(
                        f"Very low training volume with {days_since_last_run} days since last run - detraining risk"
                    )
                    deficit = 0.8 - acwr
                    penalty = min(deficit * 0.5, 0.35)
                    return max(0.5, 0.85 - penalty)

            # Moderate load_ratio with low ACWR = gradual decline or inconsistency
            deficit = 0.8 - acwr
            if load_ratio < 0.9:
                self.warnings.append("Training volume below baseline - potential detraining")
            penalty = min(deficit * 0.4, 0.25)  # Reduced penalty
            return max(0.65, 0.85 - penalty)

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
            if load_summary.acwr < 0.8 and load_summary.load_ratio < 0.7:
                return "Fresh (Recovery Week)", "Deload week - well-rested and ready for hard training when you resume."
            if load_summary.acwr < 0.8:
                return "Fresh (Reduced Volume)", "Lower training volume. Well-rested for quality workouts."
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
